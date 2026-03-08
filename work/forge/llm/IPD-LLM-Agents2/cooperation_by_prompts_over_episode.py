"""
Cooperation rate visualization over episodes
Uses shared functions from functions.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Import shared functions
from functions import (
    load_game_files,
    load_json_file,
    extract_config,
    create_output_directory,
    save_figure,
    get_prompt_colors,
    get_prompt_type
)

PLOT_LABEL = "Cooperation Rate"

def extract_cooperation_data(json_files):
    """
    Extract cooperation data from all JSON files.
    
    Args:
        json_files: List of JSON file paths
        
    Returns:
        pd.DataFrame: DataFrame with all cooperation data
    """
    all_data = []
    
    for json_file in json_files:
        data = load_json_file(json_file)
        config = extract_config(data)
        
        # Determine prompt type from file path
        prompt_type = get_prompt_type(json_file)
        
        # Get temperature from config (default to 1.0 if not found)
        temperature = data.get('config', {}).get('temperature', 1.0)
        
        for episode_data in data['episodes']:
            # Get BERT sentiment if available
            sentiment_0 = episode_data.get('agent_0', {}).get('bert_sentiment', None)
            sentiment_1 = episode_data.get('agent_1', {}).get('bert_sentiment', None)
            
            all_data.append({
                'simulation': json_file,
                'prompt_type': prompt_type,
                'episode': episode_data['episode'],
                'agent_0_coop_rate': episode_data['agent_0']['cooperation_rate'],
                'agent_1_coop_rate': episode_data['agent_1']['cooperation_rate'],
                'sentiment_0': sentiment_0,
                'sentiment_1': sentiment_1,
                'num_episodes': config['num_episodes'],
                'rounds_per_episode': config['rounds_per_episode'],
                'history_window_size': config['window'],
                'temperature': temperature
            })
    
    return pd.DataFrame(all_data)

def assign_simulation_colors(simulations):
    """
    Assign unique colors to each simulation.
    
    Args:
        simulations: Array of unique simulation identifiers
        
    Returns:
        dict: Mapping of simulation to color
    """
    num_sims = len(simulations)
    return {
        sim: cm.Set1(i / max(num_sims - 1, 1)) 
        for i, sim in enumerate(simulations)
    }

def plot_cooperation_by_episode(df, output_path):
    """
    Create scatter plot of cooperation rates over episodes with separate means per prompt type.
    
    Args:
        df: DataFrame with cooperation data
        output_path: Path to save output figure
    """
    # Get unique simulations and assign colors
    simulations = df['simulation'].unique()
    sim_colors = assign_simulation_colors(simulations)
    
    # Calculate means for each prompt type
    prompt_types = df['prompt_type'].unique()
    prompt_means = {}
    for prompt_type in prompt_types:
        prompt_df = df[df['prompt_type'] == prompt_type]
        prompt_means[prompt_type] = prompt_df.groupby('episode')[['agent_0_coop_rate', 'agent_1_coop_rate']].mean()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor('#fafbfc')
    
    # Plot individual simulation points
    for sim in simulations:
        sim_df = df[df['simulation'] == sim]
        color = sim_colors[sim]
        
        # Create label with prompt type
        prompt_type = sim_df['prompt_type'].iloc[0]
        temp = sim_df['temperature'].iloc[0]
        sim_label = (f"{prompt_type} (ep={sim_df['num_episodes'].iloc[0]}, "
                    f"r={sim_df['rounds_per_episode'].iloc[0]}, "
                    f"h={sim_df['history_window_size'].iloc[0]}, "
                    f"t={temp})")
        
        # Plot Agent 0 (circles) - very faint
        ax.scatter(sim_df['episode'], sim_df['agent_0_coop_rate'],
                  color=color, alpha=0.3, s=40, marker='o',
                  label=f'{sim_label} – Agent 0')
        
        # Plot Agent 1 (triangles) - very faint
        ax.scatter(sim_df['episode'], sim_df['agent_1_coop_rate'],
                  color=color, alpha=0.3, s=40, marker='^',
                  label=f'{sim_label} – Agent 1')
        
        # Vertical line at last episode
        last_episode = sim_df['episode'].max()
        ax.axvline(x=last_episode, color=color, linewidth=1,
                  linestyle='--', alpha=0.5)
    
    # Define colors for each prompt type using shared function
    prompt_colors = get_prompt_colors('default')
    
    # Plot mean lines for each prompt type (BOLD)
    for prompt_type in sorted(prompt_types):
        if prompt_type in prompt_means and prompt_type != 'unknown':
            means = prompt_means[prompt_type]
            color = prompt_colors.get(prompt_type, '#34495e')
            
            # Average of both agents for cleaner visualization
            combined_mean = (means['agent_0_coop_rate'] + means['agent_1_coop_rate']) / 2
            
            ax.plot(means.index, combined_mean,
                   color=color, linewidth=4, marker='D', markersize=10,
                   label=f'{prompt_type.title()} (Mean)', zorder=15,
                   markeredgecolor='white', markeredgewidth=2.5)
    
    # Add 50% reference line
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
    
    # Styling
    ax.set_xlabel('Episode', fontsize=12, fontweight='bold')
    ax.set_ylabel(PLOT_LABEL, fontsize=12, fontweight='bold')
    ax.set_title('Cooperation Rate by Prompt Type', 
                fontsize=14, fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.grid(True, alpha=0.3)
    
    # Legend - show both individual games AND mean lines
    handles, labels = ax.get_legend_handles_labels()
    
    # Separate individual games from mean lines
    game_handles = []
    game_labels = []
    mean_handles = []
    mean_labels = []
    
    for h, l in zip(handles, labels):
        if 'Mean' in l:
            mean_handles.append(h)
            mean_labels.append(l)
        else:
            game_handles.append(h)
            game_labels.append(l)
    
    # Combine: mean lines first, then individual games
    all_handles = mean_handles + game_handles
    all_labels = mean_labels + game_labels
    
    # Create legend outside plot
    legend = ax.legend(all_handles, all_labels, 
                      fontsize=9, 
                      loc='upper left', 
                      bbox_to_anchor=(1.02, 1.0),
                      frameon=True, 
                      fancybox=True, 
                      shadow=True,
                      title='Bold lines = Mean trajectory\nFaint dots = Individual games\n○ = Agent 0  △ = Agent 1\n' + '─'*30,
                      title_fontsize=10)
    
    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close()
    
    return prompt_means

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Plot cooperation rates over episodes with separate means per prompt type"
    )
    parser.add_argument('--results-dir', type=str, default='results',
                       help='Directory containing JSON result files (can contain subdirs for different prompts)')
    parser.add_argument('--output-dir', type=str, default='graphs_stats',
                       help='Directory to save output plots')
    parser.add_argument('--output-name', type=str, 
                       default='cooperation_by_prompt_type.png',
                       help='Output filename')
    
    args = parser.parse_args()
    
    try:
        # Load files
        print(f"Loading game files from {args.results_dir}...")
        json_files = load_game_files(args.results_dir)
        print(f"Found {len(json_files)} JSON files")
        
        # Extract data
        print("Extracting cooperation data...")
        df = extract_cooperation_data(json_files)
        
        # Create output directory
        output_dir = create_output_directory(args.output_dir)
        output_path = output_dir / args.output_name
        
        # Create plot
        print("Creating visualization...")
        prompt_means = plot_cooperation_by_episode(df, output_path)
        
        # Save statistics
        print("Saving statistics...")
        stats_file = output_dir / 'cooperation_by_prompt_stats.txt'
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("COOPERATION RATES BY PROMPT TYPE\n")
            f.write("="*80 + "\n\n")
            # Summary statistics
            f.write("SUMMARY:\n")
            f.write("-"*80 + "\n")
            
            for prompt_type in sorted(prompt_means.keys()):
                if prompt_type != 'unknown':
                    prompt_df = df[df['prompt_type'] == prompt_type]
                    avg = ((prompt_df['agent_0_coop_rate'] + prompt_df['agent_1_coop_rate']) / 2).mean()
                    std = ((prompt_df['agent_0_coop_rate'] + prompt_df['agent_1_coop_rate']) / 2).std()
                    n_games = len(prompt_df['simulation'].unique())
                    
                    f.write(f"\n{prompt_type.upper()}:\n")
                    f.write(f"  Mean:    {avg:.2%}\n")
                    f.write(f"  Std Dev: {std:.2%}\n")
                    f.write(f"  Games:   {n_games}\n")
            
            # Episode-by-episode breakdown
            f.write("\n" + "="*80 + "\n")
            f.write("MEAN COOPERATION BY EPISODE:\n")
            f.write("="*80 + "\n\n")
            
            for prompt_type in sorted(prompt_means.keys()):
                if prompt_type != 'unknown':
                    f.write(f"{prompt_type.upper()}:\n")
                    f.write("-"*80 + "\n")
                    means = prompt_means[prompt_type]
                    combined = (means['agent_0_coop_rate'] + means['agent_1_coop_rate']) / 2
                    
                    f.write(f"{'Episode':<10}{'Combined':<15}\n")
                    f.write("-"*80 + "\n")
                    for ep in means.index:
                        f.write(f"{ep:<10}{combined.loc[ep]:.2%}\n")
                    f.write("\n")
        
        print(f"✓ Statistics saved to: {stats_file}")
        
        # Print summary for each prompt type
        print("\nMean cooperation rates by episode and prompt type:")
        for prompt_type in sorted(prompt_means.keys()):
            if prompt_type != 'unknown':
                print(f"\n{prompt_type.upper()}:")
                print(prompt_means[prompt_type].to_string())
        
        print("\n✓ Cooperation plotting complete!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
