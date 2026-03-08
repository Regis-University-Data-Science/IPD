"""
Cooperation rates grouped by history window size
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from functions import (
    load_game_files,
    create_output_directory,
    save_figure,
    get_prompt_colors
)

from cooperation_by_prompts_over_episode import extract_cooperation_data

PLOT_LABEL = "Cooperation Rate"

def plot_cooperation_by_window(df, output_path):
    """
    Plot cooperation rates grouped by history window size - one subplot per prompt type.
    
    Args:
        df: DataFrame with cooperation data
        output_path: Path to save output figure
    """
    # Get unique prompt types and windows
    prompt_types = sorted([pt for pt in df['prompt_type'].unique() if pt != 'unknown'])
    windows = sorted(df['history_window_size'].unique())
    
    # Create figure with 3 subplots (one per prompt type)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('white')
    
    # Assign colors to windows (consistent across subplots)
    window_colors = {
        window: cm.viridis(i / max(len(windows) - 1, 1))
        for i, window in enumerate(windows)
    }
    
    # Get prompt colors for backgrounds
    prompt_colors = get_prompt_colors('default')
    
    for idx, prompt_type in enumerate(prompt_types):
        ax = axes[idx]
        ax.set_facecolor('white')
        
        # Filter data for this prompt type
        prompt_df = df[df['prompt_type'] == prompt_type]
        
        # Plot individual games (faint)
        for sim in prompt_df['simulation'].unique():
            sim_df = prompt_df[prompt_df['simulation'] == sim]
            window = sim_df['history_window_size'].iloc[0]
            color = window_colors[window]
            
            ax.scatter(sim_df['episode'], sim_df['agent_0_coop_rate'],
                      color=color, alpha=0.15, s=25, marker='o')
            ax.scatter(sim_df['episode'], sim_df['agent_1_coop_rate'],
                      color=color, alpha=0.15, s=25, marker='^')
        
        # Calculate and plot means by window for this prompt type
        for window in windows:
            window_df = prompt_df[prompt_df['history_window_size'] == window]
            if not window_df.empty:
                means = window_df.groupby('episode')[['agent_0_coop_rate', 'agent_1_coop_rate']].mean()
                combined_mean = (means['agent_0_coop_rate'] + means['agent_1_coop_rate']) / 2
                
                color = window_colors[window]
                ax.plot(means.index, combined_mean * 100,
                       color=color, linewidth=3.5, marker='o', markersize=8,
                       label=f'h={window}', zorder=15,
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
                 framealpha=0.95, edgecolor='lightgray', title='History Window')
    
    # Overall title
    fig.suptitle('Cooperation Rate by History Window & Prompt Type', 
                fontsize=18, fontweight='bold', y=0.98, color='#2c3e50')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, output_path)
    plt.close()

def save_window_statistics(df, output_dir):
    """
    Save statistics on cooperation by history window and prompt type.
    
    Args:
        df: DataFrame with cooperation data
        output_dir: Output directory path
    """
    stats_file = output_dir / 'cooperation_by_window_stats.txt'
    
    prompt_types = sorted([pt for pt in df['prompt_type'].unique() if pt != 'unknown'])
    windows = sorted(df['history_window_size'].unique())
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("COOPERATION RATES BY HISTORY WINDOW\n")
        f.write("="*80 + "\n\n")
        
        # Overall by window (all prompts combined)
        f.write("OVERALL ACROSS ALL PROMPT TYPES:\n")
        f.write("-"*80 + "\n")
        for window in windows:
            window_df = df[df['history_window_size'] == window]
            avg = ((window_df['agent_0_coop_rate'] + window_df['agent_1_coop_rate']) / 2).mean()
            std = ((window_df['agent_0_coop_rate'] + window_df['agent_1_coop_rate']) / 2).std()
            n_games = len(window_df['simulation'].unique())
            f.write(f"  h={window:<3}  Mean: {avg:.2%}  Std: {std:.2%}  Games: {n_games}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("BY PROMPT TYPE:\n")
        f.write("="*80 + "\n\n")
        
        # By prompt type
        for prompt_type in prompt_types:
            f.write(f"{prompt_type.upper()}:\n")
            f.write("-"*80 + "\n")
            
            prompt_df = df[df['prompt_type'] == prompt_type]
            
            for window in windows:
                window_df = prompt_df[prompt_df['history_window_size'] == window]
                if not window_df.empty:
                    avg = ((window_df['agent_0_coop_rate'] + window_df['agent_1_coop_rate']) / 2).mean()
                    std = ((window_df['agent_0_coop_rate'] + window_df['agent_1_coop_rate']) / 2).std()
                    n_games = len(window_df['simulation'].unique())
                    f.write(f"  h={window:<3}  Mean: {avg:.2%}  Std: {std:.2%}  Games: {n_games}\n")
                else:
                    f.write(f"  h={window:<3}  No data\n")
            
            f.write("\n")
        
        # Comparison table
        f.write("="*80 + "\n")
        f.write("COMPARISON TABLE:\n")
        f.write("="*80 + "\n\n")
        
        # Header
        f.write(f"{'Window':<10}")
        for prompt_type in prompt_types:
            f.write(f"{prompt_type:<20}")
        f.write("\n" + "-"*80 + "\n")
        
        # Data rows
        for window in windows:
            f.write(f"h={window:<8}")
            for prompt_type in prompt_types:
                window_prompt_df = df[(df['history_window_size'] == window) & 
                                     (df['prompt_type'] == prompt_type)]
                if not window_prompt_df.empty:
                    avg = ((window_prompt_df['agent_0_coop_rate'] + 
                           window_prompt_df['agent_1_coop_rate']) / 2).mean()
                    f.write(f"{avg:.2%}              ")
                else:
                    f.write(f"{'N/A':<20}")
            f.write("\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("KEY FINDINGS:\n")
        f.write("="*80 + "\n\n")
        
        # Find highest and lowest cooperation by window
        overall_by_window = {}
        for window in windows:
            window_df = df[df['history_window_size'] == window]
            if not window_df.empty:
                avg = ((window_df['agent_0_coop_rate'] + window_df['agent_1_coop_rate']) / 2).mean()
                overall_by_window[window] = avg
        
        if overall_by_window:
            best_window = max(overall_by_window.items(), key=lambda x: x[1])
            worst_window = min(overall_by_window.items(), key=lambda x: x[1])
            
            f.write(f"Highest cooperation: h={best_window[0]} ({best_window[1]:.2%})\n")
            f.write(f"Lowest cooperation:  h={worst_window[0]} ({worst_window[1]:.2%})\n")
            f.write(f"Difference: {(best_window[1] - worst_window[1]):.2%}\n")
    
    print(f"✓ Statistics saved to: {stats_file}")

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Plot cooperation rates grouped by history window"
    )
    parser.add_argument('--results-dir', type=str, default='results/history',
                       help='Directory containing JSON result files')
    parser.add_argument('--output-dir', type=str, default='graphs_stats',
                       help='Directory to save output plots')
    parser.add_argument('--output-name', type=str, 
                       default='cooperation_with_window_prompt.png',
                       help='Output filename')
    
    args = parser.parse_args()
    
    try:
        # Load files
        print(f"Loading game files from {args.results_dir}...")
        json_files = load_game_files(args.results_dir)
        print(f"Found {len(json_files)} JSON files")
        
        # Extract data using shared function
        print("Extracting cooperation data...")
        df = extract_cooperation_data(json_files)
        
        # Create output directory
        output_dir = create_output_directory(args.output_dir)
        output_path = output_dir / args.output_name
        
        # Create plot
        print("Creating visualization...")
        plot_cooperation_by_window(df, output_path)
        
        # Save statistics
        print("Generating statistics...")
        save_window_statistics(df, output_dir)
        
        # Print summary
        print("\nMean cooperation rates by history window:")
        for window in sorted(df['history_window_size'].unique()):
            window_df = df[df['history_window_size'] == window]
            avg = ((window_df['agent_0_coop_rate'] + window_df['agent_1_coop_rate']) / 2).mean()
            print(f"  Window {window}: {avg:.2%}")
        
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
