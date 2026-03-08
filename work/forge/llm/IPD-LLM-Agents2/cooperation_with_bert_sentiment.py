import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from functions import (
    load_game_files, load_json_file, get_prompt_type,
    create_output_directory, save_figure, get_prompt_colors
)

from reflection_analysis_with_bert import calculate_prompt_sentiment_means

def extract_cooperation_data(json_files):
    all_data = []
    
    for json_file in json_files:
        data = load_json_file(json_file)
        # Determine prompt type
        prompt_type = get_prompt_type(json_file)
        
        for episode_data in data['episodes']:
            all_data.append({
                'simulation': json_file,
                'prompt_type': prompt_type,
                'episode': episode_data['episode'],
                'agent_0_coop_rate': episode_data['agent_0']['cooperation_rate'],
                'agent_1_coop_rate': episode_data['agent_1']['cooperation_rate']
            })
    
    return pd.DataFrame(all_data)

def plot_cooperation_with_sentiment(df, sentiment_means, output_path):
    """Plot cooperation with sentiment - subplots."""
    
    # Calculate cooperation means
    prompt_types = sorted([pt for pt in df['prompt_type'].unique() if pt != 'unknown'])
    coop_means = {}
    for prompt_type in prompt_types:
        prompt_df = df[df['prompt_type'] == prompt_type]
        coop_means[prompt_type] = prompt_df.groupby('episode')[['agent_0_coop_rate', 'agent_1_coop_rate']].mean()
    
    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(24, 7))
    fig.patch.set_facecolor('white')
    
    # ONLY 2 color groups needed
    coop_colors = get_prompt_colors('default')  # Red, gray, green for cooperation
    sentiment_color = '#6c3483'  # One purple for all sentiment
    text_color = '#2c3e50'  # One dark color for all text
    
    for idx, prompt_type in enumerate(prompt_types):
        ax1 = axes[idx]
        ax1.set_facecolor('white')
        ax2 = ax1.twinx()
        
        # Cooperation line
        if prompt_type in coop_means:
            means = coop_means[prompt_type]
            coop_color = coop_colors.get(prompt_type, text_color)
            combined_mean = (means['agent_0_coop_rate'] + means['agent_1_coop_rate']) / 2
            
            ax1.plot(means.index, combined_mean * 100,
                    color=coop_color, linewidth=3.5, linestyle='-',
                    label='Cooperation', zorder=10, alpha=0.9)
        
        # Sentiment line - same purple for all
        if prompt_type in sentiment_means:
            sent_data = sentiment_means[prompt_type]
            episodes = sorted(sent_data.keys())
            sentiments = [sent_data[ep] for ep in episodes]
            
            ax2.plot(episodes, sentiments,
                    color=sentiment_color, linewidth=3, linestyle='-',
                    label='Sentiment', zorder=9, alpha=0.85)
        
        # Titles and labels
        ax1.set_title(f'{prompt_type.upper()}', fontsize=18, fontweight='bold', 
                     pad=20, color=text_color)
        ax1.set_xlabel('Episode', fontsize=14, fontweight='600', color=text_color)
        ax1.set_ylabel('Cooperation (%)', fontsize=14, fontweight='600', color=text_color)
        ax2.set_ylabel('Sentiment', fontsize=14, fontweight='600', color=sentiment_color)
        ax2.yaxis.set_label_position('right')
        
        # Y-axes
        ax1.set_ylim(0, 105)
        ax1.set_yticks([0, 25, 50, 75, 100])
        ax1.set_yticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=12)

        ax2.set_ylim(-1.05, 1.05)
        ax2.set_yticks([-1, -0.5, 0, 0.5, 1])
        ax2.set_yticklabels(['-1.0', '-0.5', '0', '+0.5', '+1.0'], fontsize=12)
        
        # Ticks
        ax1.tick_params(axis='both', labelsize=11, colors=text_color, length=6, width=1.5)
        ax2.tick_params(axis='y', labelsize=11, colors=sentiment_color, length=6, width=1.5)
        
        # Grid & reference
        ax1.grid(True, axis='y', alpha=0.15, color='gray', zorder=0)
        ax1.set_axisbelow(True)
        ax1.axhline(y=50, color='gray', linestyle='--', alpha=0.3, linewidth=1.5)
        
        # Spines
        ax1.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        for spine in ['left', 'bottom', 'right']:
            ax1.spines[spine].set_linewidth(1.5)
            ax1.spines[spine].set_color('lightgray')
        ax2.spines['right'].set_linewidth(1.5)
        ax2.spines['right'].set_color('lightgray')
        
        # Legend - smart positioning based on subplot to avoid data overlap
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        
        if handles1 or handles2:
            # Choose position based on subplot to avoid overlap
            if idx == 0:  # Moral - typically high cooperation
                legend_loc = 'lower right'
            elif idx == 1:  # Neutral - middle cooperation
                legend_loc = 'upper right'
            else:  # Self-interest - typically low cooperation
                legend_loc = 'upper right'
            
            ax1.legend(handles1 + handles2, labels1 + labels2,
                      fontsize=11, loc=legend_loc, frameon=True,
                      fancybox=False, shadow=False, framealpha=0.95,
                      edgecolor='lightgray', borderpad=1, labelspacing=0.8)
    
    # Title & note
    fig.suptitle('Cooperation & Sentiment by Prompt Type', 
                fontsize=20, fontweight='bold', y=0.995, color=text_color)
    
    fig.text(0.5, 0.01, 
            'Cooperation (left axis), Sentiment (right axis, purple)',
            ha='center', fontsize=11, color='black', style='italic')
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.99])
    save_figure(fig, output_path)
    plt.close()
    
    return coop_means


def save_summary_statistics(coop_means, sentiment_means, output_dir):
    """Save summary statistics."""
    stats_file = output_dir / 'cooperation_sentiment_summary.txt'
    
    with open(stats_file, 'w') as f:
        
        f.write("\nSentiment means by prompt type:\n")
        for prompt_type in sorted(sentiment_means.keys()):
            sentiments = list(sentiment_means[prompt_type].values())
            avg = sum(sentiments) / len(sentiments)
            f.write(f"  {prompt_type:<15}: {avg:+.3f}\n")
    
    print(f"✓ Summary saved to: {stats_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Plot cooperation with sentiment (optimized)")
    parser.add_argument('--results-dir', type=str, default='results')
    parser.add_argument('--output-dir', type=str, default='graphs_stats')
    parser.add_argument('--output-name', type=str, default='cooperation_sentiment.png')
    
    args = parser.parse_args()
    
    try:
        print(f"Loading files from {args.results_dir}...")
        json_files = load_game_files(args.results_dir)
        print(f"Found {len(json_files)} files")
        
        df = extract_cooperation_data(json_files)
        sentiment_means = calculate_prompt_sentiment_means(json_files)
        
        output_dir = create_output_directory(args.output_dir)
        output_path = output_dir / args.output_name
        
        coop_means = plot_cooperation_with_sentiment(df, sentiment_means, output_path)
        save_summary_statistics(coop_means, sentiment_means, output_dir)
        
        print("\n✓ Complete!")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
