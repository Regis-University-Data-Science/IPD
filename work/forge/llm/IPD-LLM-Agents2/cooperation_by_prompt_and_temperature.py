"""
Cooperation rates grouped by temperature
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm

from functions import (
    load_game_files,
    create_output_directory,
    save_figure
)

from cooperation_by_prompts_over_episode import extract_cooperation_data

PLOT_LABEL = "Cooperation Rate"

def plot_cooperation_by_temperature(df, output_path):
    """
    Plot cooperation rates grouped by temperature - one subplot per prompt type.
    
    Args:
        df: DataFrame with cooperation data
        output_path: Path to save output figure
    """
    # Get unique prompt types and temperatures
    prompt_types = sorted([pt for pt in df['prompt_type'].unique() if pt != 'unknown'])
    temperatures = sorted(df['temperature'].unique())
    
    # Create figure with 3 subplots (one per prompt type)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('white')
    
    # Assign colors to temperatures (consistent across subplots)
    temp_colors = {
        temp: cm.coolwarm(i / max(len(temperatures) - 1, 1))
        for i, temp in enumerate(temperatures)
    }
    
    for idx, prompt_type in enumerate(prompt_types):
        ax = axes[idx]
        ax.set_facecolor('white')
        
        # Filter data for this prompt type
        prompt_df = df[df['prompt_type'] == prompt_type]
        
        # Plot individual games (faint)
        for sim in prompt_df['simulation'].unique():
            sim_df = prompt_df[prompt_df['simulation'] == sim]
            temp = sim_df['temperature'].iloc[0]
            color = temp_colors[temp]
            
            ax.scatter(sim_df['episode'], sim_df['agent_0_coop_rate'],
                      color=color, alpha=0.15, s=25, marker='o')
            ax.scatter(sim_df['episode'], sim_df['agent_1_coop_rate'],
                      color=color, alpha=0.15, s=25, marker='^')
        
        # Calculate and plot means by temperature for this prompt type
        for temp in temperatures:
            temp_df = prompt_df[prompt_df['temperature'] == temp]
            if not temp_df.empty:
                means = temp_df.groupby('episode')[['agent_0_coop_rate', 'agent_1_coop_rate']].mean()
                combined_mean = (means['agent_0_coop_rate'] + means['agent_1_coop_rate']) / 2
                
                color = temp_colors[temp]
                ax.plot(means.index, combined_mean * 100,
                       color=color, linewidth=3.5, marker='s', markersize=8,
                       label=f't={temp}', zorder=15,
                       markeredgecolor='white', markeredgewidth=2)
        
        # Styling
        ax.axhline(y=50, color='gray', linestyle='--', alpha=0.3, linewidth=1.5)
        ax.set_xlabel('Episode', fontsize=12, fontweight='bold', color='#2c3e50')
        
        if idx == 0:
            ax.set_ylabel('Cooperation Rate (%)', fontsize=12, fontweight='bold', color='#2c3e50')
        
        ax.set_title(f'{prompt_type.upper()}', 
                    fontsize=16, fontweight='bold', pad=15, color='#2c3e50')
        
        ax.set_ylim(0, 105)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=11)
        ax.grid(True, alpha=0.2, color='gray')
        ax.tick_params(labelsize=11, colors='#2c3e50')
        
        # Legend
        ax.legend(fontsize=10, loc='best', frameon=True, 
                 framealpha=0.95, edgecolor='lightgray', title='Temperature')
    
    # Overall title
    fig.suptitle('Cooperation Rate by Temperature & Prompt Type', 
                fontsize=18, fontweight='bold', y=0.98, color='#2c3e50')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, output_path)
    plt.close()


def save_temperature_statistics(df, output_dir):
    """
    Save statistics on cooperation by temperature and prompt type.
    
    Args:
        df: DataFrame with cooperation data
        output_dir: Output directory path
    """
    stats_file = output_dir / 'cooperation_by_temperature_stats.txt'
    
    prompt_types = sorted([pt for pt in df['prompt_type'].unique() if pt != 'unknown'])
    temperatures = sorted(df['temperature'].unique())
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("COOPERATION RATES BY TEMPERATURE\n")
        f.write("="*80 + "\n\n")
        
        # Overall by temperature (all prompts combined)
        f.write("OVERALL ACROSS ALL PROMPT TYPES:\n")
        f.write("-"*80 + "\n")
        for temp in temperatures:
            temp_df = df[df['temperature'] == temp]
            avg = ((temp_df['agent_0_coop_rate'] + temp_df['agent_1_coop_rate']) / 2).mean()
            std = ((temp_df['agent_0_coop_rate'] + temp_df['agent_1_coop_rate']) / 2).std()
            n_games = len(temp_df['simulation'].unique())
            f.write(f"  t={temp:<5}  Mean: {avg:.2%}  Std: {std:.2%}  Games: {n_games}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("BY PROMPT TYPE:\n")
        f.write("="*80 + "\n\n")
        
        # By prompt type
        for prompt_type in prompt_types:
            f.write(f"{prompt_type.upper()}:\n")
            f.write("-"*80 + "\n")
            
            prompt_df = df[df['prompt_type'] == prompt_type]
            
            for temp in temperatures:
                temp_df = prompt_df[prompt_df['temperature'] == temp]
                if not temp_df.empty:
                    avg = ((temp_df['agent_0_coop_rate'] + temp_df['agent_1_coop_rate']) / 2).mean()
                    std = ((temp_df['agent_0_coop_rate'] + temp_df['agent_1_coop_rate']) / 2).std()
                    n_games = len(temp_df['simulation'].unique())
                    f.write(f"  t={temp:<5}  Mean: {avg:.2%}  Std: {std:.2%}  Games: {n_games}\n")
                else:
                    f.write(f"  t={temp:<5}  No data\n")
            
            f.write("\n")
        
        # Comparison table
        f.write("="*80 + "\n")
        f.write("COMPARISON TABLE:\n")
        f.write("="*80 + "\n\n")
        
        # Header
        f.write(f"{'Temp':<10}")
        for prompt_type in prompt_types:
            f.write(f"{prompt_type:<20}")
        f.write("\n" + "-"*80 + "\n")
        
        # Data rows
        for temp in temperatures:
            f.write(f"t={temp:<8}")
            for prompt_type in prompt_types:
                temp_prompt_df = df[(df['temperature'] == temp) & 
                                   (df['prompt_type'] == prompt_type)]
                if not temp_prompt_df.empty:
                    avg = ((temp_prompt_df['agent_0_coop_rate'] + 
                           temp_prompt_df['agent_1_coop_rate']) / 2).mean()
                    f.write(f"{avg:.2%}              ")
                else:
                    f.write(f"{'N/A':<20}")
            f.write("\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("KEY FINDINGS:\n")
        f.write("="*80 + "\n\n")
        
        # Find highest and lowest cooperation by temperature
        overall_by_temp = {}
        for temp in temperatures:
            temp_df = df[df['temperature'] == temp]
            if not temp_df.empty:
                avg = ((temp_df['agent_0_coop_rate'] + temp_df['agent_1_coop_rate']) / 2).mean()
                overall_by_temp[temp] = avg
        
        if overall_by_temp:
            best_temp = max(overall_by_temp.items(), key=lambda x: x[1])
            worst_temp = min(overall_by_temp.items(), key=lambda x: x[1])
            
            f.write(f"Highest cooperation: t={best_temp[0]} ({best_temp[1]:.2%})\n")
            f.write(f"Lowest cooperation:  t={worst_temp[0]} ({worst_temp[1]:.2%})\n")
            f.write(f"Difference: {(best_temp[1] - worst_temp[1]):.2%}\n\n")
            
            # Temperature interpretation
            f.write("INTERPRETATION:\n")
            f.write("-"*80 + "\n")
            f.write("Lower temperature (t < 1.0): More deterministic, consistent responses\n")
            f.write("Higher temperature (t > 1.0): More random, variable responses\n")
            f.write("Temperature = 1.0: Balanced randomness\n")
    
    print(f"✓ Statistics saved to: {stats_file}")

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Plot cooperation rates grouped by temperature"
    )
    parser.add_argument('--results-dir', type=str, default='results/temperature',
                       help='Directory containing JSON result files')
    parser.add_argument('--output-dir', type=str, default='graphs_stats',
                       help='Directory to save output plots')
    parser.add_argument('--output-name', type=str, 
                       default='cooperation_with_temperature_prompt.png',
                       help='Output filename')
    
    args = parser.parse_args()
    
    try:
        # Load files
        print(f"Loading game files from {args.results_dir}...")
        json_files = load_game_files(args.results_dir, recursive=True)
        print(f"Found {len(json_files)} JSON files")
        
        # Extract data using shared function
        print("Extracting cooperation data...")
        df = extract_cooperation_data(json_files)
        
        # Create output directory
        output_dir = create_output_directory(args.output_dir)
        output_path = output_dir / args.output_name
        
        # Create plot
        print("Creating visualization...")
        plot_cooperation_by_temperature(df, output_path)
        
        # Save statistics
        print("Generating statistics...")
        save_temperature_statistics(df, output_dir)
        
        # Print summary
        print("\nMean cooperation rates by temperature:")
        for temp in sorted(df['temperature'].unique()):
            temp_df = df[df['temperature'] == temp]
            avg = ((temp_df['agent_0_coop_rate'] + temp_df['agent_1_coop_rate']) / 2).mean()
            print(f"  Temperature {temp}: {avg:.2%}")
        
        print("\n✓ Plotting complete!")
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
