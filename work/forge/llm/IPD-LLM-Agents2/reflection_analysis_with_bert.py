"""
BERT-based Reflection Analysis for Episodic IPD
Uses zero-shot classification and semantic similarity
"""

import json
from pathlib import Path
from collections import defaultdict
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import warnings

# Import shared utility functions
from functions import (
    load_game_files, load_json_file, extract_config, get_prompt_type,
    create_output_directory, save_figure, apply_plot_styling,
    calculate_mean_trajectory, get_episode_range, print_progress
)

warnings.filterwarnings('ignore', message='.*position_ids.*')

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed")

print("Loading BERT models... (this may take a minute first time)")

# Load zero-shot classifier
classifier = pipeline(
    "zero-shot-classification", 
    model="typeform/distilbert-base-uncased-mnli",
    device=0 if torch.cuda.is_available() else -1,
    batch_size=8
)

# Sentiment model (distilbert fine-tuned on SST-2)
sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0 if torch.cuda.is_available() else -1
)

# Load sentence transformer for semantic similarity
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

print("✓ Models loaded!\n")


# Define categories for zero-shot classification
MORAL_CATEGORIES = [
    "care", "harm", "fairness", "cheating",
    "loyalty", "betrayal", "authority", "subversion",
    "sanctity", "degradation", "liberty", "oppression"
]

# Grouping for positive vs negative analysis
POSITIVE_MORAL = ["care", "fairness", "loyalty", "authority", "sanctity", "liberty"]
NEGATIVE_MORAL = ["harm", "cheating", "betrayal", "subversion", "degradation", "oppression"]

MORAL_THEMES = [
    "moral reasoning", "ethical judgment",
    "fairness and justice", "trust and cooperation",
    "exploitation and selfishness"
]

def get_moral_valence(category):
    """
    Determine if a moral category is positive or negative.
    
    Args:
        category: Moral category name
        
    Returns:
        str: 'positive' or 'negative'
    """
    if category in POSITIVE_MORAL:
        return 'positive'
    elif category in NEGATIVE_MORAL:
        return 'negative'
    else:
        return 'unknown'

def bert_sentiment_score(text):
    """Calculate sentiment score from -1 to +1"""
    result = sentiment_model(text)[0]
    label = result['label']
    score = result['score']
    
    return score if label == "POSITIVE" else -score

def bert_moral_density(text):
    """Calculate moral density percentage"""
    result = classifier(text, MORAL_THEMES)
    scores = result['scores']
    return (sum(scores) / len(scores)) * 100

def classify_reflection(reflection_text):
    """Classify reflection into moral reasoning categories"""
    result = classifier(reflection_text, MORAL_CATEGORIES)
    
    return {
        'top_category': result['labels'][0],
        'confidence': result['scores'][0],
        'all_scores': dict(zip(result['labels'], result['scores']))
    }

def calculate_moral_sophistication(reflection_text):
    """Calculate moral sophistication using semantic similarity"""
    
    prototypes = {
        'Level 0 - Reactive': "They defected so I defected back",
        'Level 1 - Simple Moral': "That wasn't fair to me",
        'Level 2 - Moral Reasoning': "Cooperation is fair because it benefits both of us equally and builds trust",
        'Level 3 - Complex Moral': "While defecting might maximize my short-term points, sustained mutual cooperation through consistent reciprocity creates better long-term outcomes for both participants and builds lasting trust"
    }
    
    reflection_embedding = similarity_model.encode(reflection_text, convert_to_tensor=True)
    
    similarities = {}
    for level, prototype_text in prototypes.items():
        prototype_embedding = similarity_model.encode(prototype_text, convert_to_tensor=True)
        similarity = util.cos_sim(reflection_embedding, prototype_embedding)[0][0].item()
        similarities[level] = similarity
    
    best_match = max(similarities.items(), key=lambda x: x[1])
    
    return {
        'sophistication_level': best_match[0],
        'confidence': best_match[1],
        'all_similarities': similarities
    }

def analyze_game_file(filepath):
    """Analyze all reflections in a game file with optimized batching"""
    data = load_json_file(filepath)
    config = extract_config(data)
    window = config['window']
    
    # Get temperature from config
    temperature = data.get('config', {}).get('temperature', 1.0)

    prompt_type = get_prompt_type(filepath)
    
    # Extract all reflections and metadata
    all_reflections = []
    reflection_info = []
    
    for episode in data['episodes']:
        ep_num = episode['episode']
        coop_0 = episode['agent_0']['cooperation_rate']
        coop_1 = episode['agent_1']['cooperation_rate']
        
        for agent_key in ['agent_0', 'agent_1']:
            all_reflections.append(episode[agent_key]['reflection'])
            reflection_info.append({
                'episode': ep_num,
                'agent': agent_key,
                'coop_0': coop_0,
                'coop_1': coop_1
            })
    
    print(f"  Processing {len(all_reflections)} reflections...")
    
    # Process all reflections
    all_classifications = []
    all_sophistications = []
    all_sentiments = []
    all_moral_densities = []
    
    for refl in all_reflections:
        all_classifications.append(classify_reflection(refl))
        all_sophistications.append(calculate_moral_sophistication(refl))
        all_sentiments.append(bert_sentiment_score(refl))
        all_moral_densities.append(bert_moral_density(refl))
    
    # Organize results by episode
    results = []
    episode_metrics = []
    episodes_dict = {}
    
    for idx, info in enumerate(reflection_info):
        ep_num = info['episode']
        
        if ep_num not in episodes_dict:
            episodes_dict[ep_num] = {
                'episode': ep_num,
                'window': window,
                'coop_0': info['coop_0'],
                'coop_1': info['coop_1'],
                'data': []
            }
        
        episodes_dict[ep_num]['data'].append({
            'agent': info['agent'],
            'reflection': all_reflections[idx],
            'classification': all_classifications[idx],
            'sophistication': all_sophistications[idx],
            'sentiment': all_sentiments[idx],
            'moral_density': all_moral_densities[idx]
        })
    
    # Convert to output format
    for ep_num in sorted(episodes_dict.keys()):
        ep = episodes_dict[ep_num]
        ep_data = ep['data']
        
        agent_0_data = [d for d in ep_data if d['agent'] == 'agent_0'][0]
        agent_1_data = [d for d in ep_data if d['agent'] == 'agent_1'][0]
        
        for agent_data in [agent_0_data, agent_1_data]:
            moral_cat = agent_data['classification']['top_category']
            results.append({
                'window': window,
                'episode': ep_num,
                'agent': agent_data['agent'],
                'reflection': agent_data['reflection'],
                'moral_category': moral_cat,
                'moral_valence': get_moral_valence(moral_cat),  # Add positive/negative
                'category_confidence': agent_data['classification']['confidence'],
                'sophistication_level': agent_data['sophistication']['sophistication_level'],
                'sophistication_confidence': agent_data['sophistication']['confidence'],
                'sentiment': agent_data['sentiment'],
                'moral_density': agent_data['moral_density']
            })
        
        episode_metrics.append({
            'episode': ep_num,
            'window': window,
            'temperature': temperature,
            'prompt_type': prompt_type,
            'sophistication_0': agent_0_data['sophistication']['confidence'],
            'sophistication_1': agent_1_data['sophistication']['confidence'],
            'sentiment_0': agent_0_data['sentiment'],
            'sentiment_1': agent_1_data['sentiment'],
            'moral_density_0': agent_0_data['moral_density'],
            'moral_density_1': agent_1_data['moral_density'],
            'cooperation_rate_0': ep['coop_0'],
            'cooperation_rate_1': ep['coop_1'],
            'sophistication': (agent_0_data['sophistication']['confidence'] + 
                             agent_1_data['sophistication']['confidence']) / 2,
            'sentiment': (agent_0_data['sentiment'] + agent_1_data['sentiment']) / 2,
            'moral_density': (agent_0_data['moral_density'] + agent_1_data['moral_density']) / 2,
            'cooperation_rate': (ep['coop_0'] + ep['coop_1']) / 2
        })
    
    return results, episode_metrics


def create_subplot_grid(n_items, cols=3):
    """Helper to create consistent subplot grids"""
    import math
    rows = math.ceil(n_items / cols)
    return rows, cols

def plot_moral_valence_trajectory(all_results, data_by_window, output_file):
    """Plot positive/negative moral valence over episodes with cooperation - separate subplot per agent"""
    if not HAS_MATPLOTLIB:
        return
    
    all_games = [(window, game) for window in data_by_window 
                 for game in data_by_window[window]]
    
    # Need 2 columns (Agent 0, Agent 1) and rows = number of games
    num_games = len(all_games)
    
    fig, axes = plt.subplots(num_games, 2, figsize=(14, 5 * num_games), facecolor='white')
    
    # Handle case of single game
    if num_games == 1:
        axes = axes.reshape(1, -1)
    
    for game_idx, (window, game) in enumerate(all_games):
        # Get game configuration info
        episodes = [ep['episode'] for ep in game]
        num_episodes = len(episodes)
        
        # Get temperature from first episode
        temp = game[0].get('temperature', 1.0) if game else 1.0
        prompt_type = game[0].get('prompt_type', 'unknown')
        # Calculate positive moral valence % for each episode
        pos_pct_0 = []
        pos_pct_1 = []
        
        for ep in episodes:
            # Agent 0
            ep_results_0 = [r for r in all_results 
                          if r['window']==window and r['episode']==ep and r['agent']=='agent_0']
            if ep_results_0:
                pos_count = sum(1 for r in ep_results_0 if r['moral_valence'] == 'positive')
                pos_pct_0.append((pos_count / len(ep_results_0)) * 100)
            else:
                pos_pct_0.append(0)
            
            # Agent 1
            ep_results_1 = [r for r in all_results 
                          if r['window']==window and r['episode']==ep and r['agent']=='agent_1']
            if ep_results_1:
                pos_count = sum(1 for r in ep_results_1 if r['moral_valence'] == 'positive')
                pos_pct_1.append((pos_count / len(ep_results_1)) * 100)
            else:
                pos_pct_1.append(0)
        
        # Get cooperation rates
        c0 = [ep['cooperation_rate_0'] * 100 for ep in game]
        c1 = [ep['cooperation_rate_1'] * 100 for ep in game]
        
        # Plot Agent 0 (left column)
        ax1_0 = axes[game_idx, 0]
        ax1_0.set_facecolor('white')
        ax2_0 = ax1_0.twinx()
        
        # Agent 0: Positive moral valence
        ax1_0.plot(episodes, pos_pct_0, linewidth=3, color='#27ae60', 
                  label=f'Positive Moral (ep={num_episodes}, h={window}, t={temp})', zorder=10)
        
        # Agent 0: Cooperation
        ax2_0.plot(episodes, c0, linestyle='--', linewidth=2.5, color='#3498db',
                  label='Cooperation Rate', marker='o', markeredgecolor='white', markeredgewidth=2)
        
        ax1_0.set_title(f'Game {game_idx+1} - Agent 0 | prompt={prompt_type}  h={window}  t={temp}', fontsize=14, fontweight='bold', pad=15)
        ax1_0.set_xlabel('Episode', fontsize=12, fontweight='600')
        ax1_0.set_ylabel('Positive Moral Valence (%)', fontsize=12, fontweight='600', color='#27ae60')
        ax2_0.set_ylabel('Cooperation Rate (%)', fontsize=12, fontweight='600', color='#2c3e50')
        
        ax1_0.set_ylim(0, 105)
        ax2_0.set_ylim(0, 105)
        ax1_0.tick_params(axis='y', labelcolor='#27ae60', labelsize=11)
        ax2_0.tick_params(axis='y', labelcolor='#2c3e50', labelsize=11)
        ax1_0.grid(True, alpha=0.2, color='gray')
        
        # Legend for Agent 0
        handles1_0, labels1_0 = ax1_0.get_legend_handles_labels()
        handles2_0, labels2_0 = ax2_0.get_legend_handles_labels()
        ax1_0.legend(handles1_0 + handles2_0, labels1_0 + labels2_0, 
                    fontsize=10, loc='best', framealpha=0.95)
        
        # Plot Agent 1 (right column)
        ax1_1 = axes[game_idx, 1]
        ax1_1.set_facecolor('white')
        ax2_1 = ax1_1.twinx()
        
        # Agent 1: Positive moral valence
        ax1_1.plot(episodes, pos_pct_1, linewidth=3, color='#16a085', 
                  label=f'Positive Moral (ep={num_episodes}, h={window}, t={temp})', zorder=10)
        
        # Agent 1: Cooperation
        ax2_1.plot(episodes, c1, linestyle='--', linewidth=2.5, color='#e74c3c',
                  label='Cooperation Rate', marker='o', markeredgecolor='white', markeredgewidth=2)
        
        ax1_1.set_title(f'Game {game_idx+1} - Agent 1 | prompt={prompt_type}  h={window}  t={temp}', fontsize=14, fontweight='bold', pad=15)
        ax1_1.set_xlabel('Episode', fontsize=12, fontweight='600')
        ax1_1.set_ylabel('Positive Moral Valence (%)', fontsize=12, fontweight='600', color='#16a085')
        ax2_1.set_ylabel('Cooperation Rate (%)', fontsize=12, fontweight='600', color='#2c3e50')
        
        ax1_1.set_ylim(0, 105)
        ax2_1.set_ylim(0, 105)
        ax1_1.tick_params(axis='y', labelcolor='#16a085', labelsize=11)
        ax2_1.tick_params(axis='y', labelcolor='#2c3e50', labelsize=11)
        ax1_1.grid(True, alpha=0.2, color='gray')
        
        # Legend for Agent 1
        handles1_1, labels1_1 = ax1_1.get_legend_handles_labels()
        handles2_1, labels2_1 = ax2_1.get_legend_handles_labels()
        ax1_1.legend(handles1_1 + handles2_1, labels1_1 + labels2_1, 
                    fontsize=10, loc='best', framealpha=0.95)
    
    fig.suptitle('BERT: Positive Moral Valence & Cooperation by Agent', 
                fontsize=18, fontweight='bold', y=0.998)
    plt.tight_layout(rect=[0, 0, 1, 0.995])
    save_figure(fig, output_file)
    plt.close()

def plot_sentiment_moral_density(data_by_window, output_file):
    """Plot sentiment AND moral density"""
    if not HAS_MATPLOTLIB:
        return
    
    all_games = [(window, game) for window in data_by_window 
                 for game in data_by_window[window]]
    
    rows, cols = create_subplot_grid(len(all_games))
    
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows), facecolor='white')
    axes = np.array(axes).reshape(-1)
    
    for idx, (window, game) in enumerate(all_games):
        ax1 = axes[idx]
        ax1.set_facecolor('#fafbfc')
        ax2 = ax1.twinx()
        
        episodes = [ep['episode'] for ep in game]
        s0, s1 = [ep['sentiment_0'] for ep in game], [ep['sentiment_1'] for ep in game]
        m0, m1 = [ep['moral_density_0'] for ep in game], [ep['moral_density_1'] for ep in game]
        
        # Sentiment (solid)
        ax1.plot(episodes, s0, linewidth=2.5, color='#3498db', label='Sentiment A0')
        ax1.plot(episodes, s1, linewidth=2.5, color='#e74c3c', label='Sentiment A1')
        
        # Moral density (dashed)
        ax2.plot(episodes, m0, linestyle='--', linewidth=2.5, color='#3498db', 
                label='Moral A0', marker='o', markeredgecolor='white', markeredgewidth=2)
        ax2.plot(episodes, m1, linestyle='--', linewidth=2.5, color='#e74c3c',
                label='Moral A1', marker='o', markeredgecolor='white', markeredgewidth=2)
        
        ax1.axhline(0, linestyle='--', alpha=0.3, color='#7f8c8d')
        ax1.set_title(f'Game {idx+1} (Window {window})', fontsize=13, fontweight='bold')
        ax1.set_xlabel('Episode', fontsize=11)
        ax1.set_ylabel('Sentiment Score', fontsize=11)
        ax2.set_ylabel('Moral Density (%)', fontsize=11)
        ax1.set_ylim(-1, 1.2)
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='best')
        
        apply_plot_styling(ax1, remove_spines=False)
        ax2.spines['right'].set_linewidth(2)
        ax2.spines['right'].set_color('#7f8c8d')
    
    for ax in axes[len(all_games):]:
        ax.set_visible(False)
    
    fig.suptitle('BERT: Sentiment & Moral Density Per Game', fontsize=18, fontweight='bold')
    plt.tight_layout()
    save_figure(fig, output_file)
    plt.close()

def plot_sophistication_cooperation(data_by_window, output_file):
    """Plot cooperation AND sophistication"""
    if not HAS_MATPLOTLIB:
        return
    
    all_games = [(window, game) for window in data_by_window 
                 for game in data_by_window[window]]
    
    rows, cols = create_subplot_grid(len(all_games))
    
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5.5 * rows), facecolor='white')
    axes = np.array(axes).reshape(-1)
    
    for idx, (window, game) in enumerate(all_games):
        ax1 = axes[idx]
        ax1.set_facecolor('#fafbfc')
        ax2 = ax1.twinx()
        
        episodes = [ep['episode'] for ep in game]
        c0, c1 = [ep['cooperation_rate_0'] * 100 for ep in game], [ep['cooperation_rate_1'] * 100 for ep in game]
        s0, s1 = [ep['sophistication_0'] for ep in game], [ep['sophistication_1'] for ep in game]
        
        # Cooperation (solid)
        ax1.plot(episodes, c0, linewidth=2.5, color='#3498db', label='Cooperation A0', zorder=10)
        ax1.plot(episodes, c1, linewidth=2.5, color='#e74c3c', label='Cooperation A1', zorder=10)
        
        # Sophistication (dashed)
        ax2.plot(episodes, s0, linestyle='--', linewidth=2.5, color='#3498db',
                label='Sophistication A0', marker='o', markeredgecolor='white', markeredgewidth=2)
        ax2.plot(episodes, s1, linestyle='--', linewidth=2.5, color='#e74c3c',
                label='Sophistication A1', marker='o', markeredgecolor='white', markeredgewidth=2)
        
        ax1.set_title(f'Game {idx+1} (Window {window})', fontsize=13, fontweight='bold', pad=10)
        ax1.set_xlabel('Episode', fontsize=11)
        ax1.set_ylabel('Cooperation Rate (%)', fontsize=11, color='#2c3e50')
        ax2.set_ylabel('Sophistication Score', fontsize=11, color='#2c3e50')
        ax1.set_ylim(0, 105)
        ax2.set_ylim(0, 1.05)
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='best')
        
        apply_plot_styling(ax1, remove_spines=False)
        ax2.spines['right'].set_linewidth(2)
        ax2.spines['right'].set_color('#7f8c8d')
    
    for ax in axes[len(all_games):]:
        ax.set_visible(False)
    
    fig.suptitle('BERT: Cooperation (Left) & Sophistication (Right)', 
                fontsize=18, fontweight='bold', y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    save_figure(fig, output_file)
    plt.close()

def plot_moral_category_trajectory(all_results, data_by_window, output_dir):
    """Plot moral category trajectories with cooperation rates"""
    if not HAS_MATPLOTLIB:
        return
    
    all_categories = sorted(set(r['moral_category'] for r in all_results))
    rows, cols = create_subplot_grid(len(all_categories))
    
    fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 5 * rows), facecolor='white')
    axes = np.array(axes).reshape(-1)
    
    for cat_idx, category in enumerate(all_categories):
        ax = axes[cat_idx]
        ax.set_facecolor('white')
        ax2 = ax.twinx()
        
        all_agent0_traj = []
        all_agent1_traj = []
        all_coop0_traj = []
        all_coop1_traj = []
        
        # Collect data from all games
        for window in sorted(data_by_window.keys()):
            for game in data_by_window[window]:
                episodes = [ep['episode'] for ep in game]
                
                # Moral category percentages
                pcts0 = [sum(1 for r in all_results 
                           if r['window']==window and r['episode']==ep 
                           and r['agent']=='agent_0' and r['moral_category']==category) * 100
                        for ep in episodes]
                pcts1 = [sum(1 for r in all_results 
                           if r['window']==window and r['episode']==ep 
                           and r['agent']=='agent_1' and r['moral_category']==category) * 100
                        for ep in episodes]
                
                ax.plot(episodes, pcts0, 'o-', color='blue', alpha=0.3, linewidth=1, markersize=4)
                ax.plot(episodes, pcts1, '^-', color='red', alpha=0.3, linewidth=1, markersize=4)
                
                all_agent0_traj.append((episodes, pcts0))
                all_agent1_traj.append((episodes, pcts1))
                
                # Cooperation rates
                coop0 = [ep['cooperation_rate_0'] * 100 for ep in game]
                coop1 = [ep['cooperation_rate_1'] * 100 for ep in game]
                all_coop0_traj.append((episodes, coop0))
                all_coop1_traj.append((episodes, coop1))
        
        # Calculate and plot means
        if all_agent0_traj:
            ep_range = get_episode_range(all_agent0_traj)
            
            means0 = calculate_mean_trajectory(all_agent0_traj, ep_range)
            means1 = calculate_mean_trajectory(all_agent1_traj, ep_range)
            coop_means0 = calculate_mean_trajectory(all_coop0_traj, ep_range)
            coop_means1 = calculate_mean_trajectory(all_coop1_traj, ep_range)
            
            ax.plot(ep_range, means0, 'o-', color='blue', linewidth=3, markersize=8,
                   markeredgecolor='white', markeredgewidth=2, zorder=10)
            ax.plot(ep_range, means1, '^-', color='red', linewidth=3, markersize=8,
                   markeredgecolor='white', markeredgewidth=2, zorder=10)
            
            ax2.plot(ep_range, coop_means0, 'o--', color='cyan', linewidth=2.5, markersize=7,
                    markeredgecolor='white', markeredgewidth=2, zorder=9)
            ax2.plot(ep_range, coop_means1, '^--', color='orange', linewidth=2.5, markersize=7,
                    markeredgecolor='white', markeredgewidth=2, zorder=9)
        
        ax.set_title(category.title(), fontsize=12, fontweight='bold')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Moral Category (%)', color='purple')
        ax2.set_ylabel('Cooperation Rate (%)', color='green')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='y', labelcolor='purple')
        ax2.tick_params(axis='y', labelcolor='green')
    
    for ax in axes[len(all_categories):]:
        ax.set_visible(False)
    
    legend_elements = [
        Line2D([0], [0], marker='o', color='blue', label='Agent 0 Moral Mean',
              markersize=6, linewidth=3, linestyle='-'),
        Line2D([0], [0], marker='^', color='red', label='Agent 1 Moral Mean',
              markersize=6, linewidth=3, linestyle='-'),
        Line2D([0], [0], marker='o', color='cyan', label='Agent 0 Coop Mean',
              markersize=6, linewidth=2.5, linestyle='--'),
        Line2D([0], [0], marker='^', color='orange', label='Agent 1 Coop Mean',
              markersize=6, linewidth=2.5, linestyle='--')
    ]
    
    fig.legend(handles=legend_elements, loc='upper center', ncol=4,
              fontsize=11, frameon=True, bbox_to_anchor=(0.5, 1.02))
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, output_dir / 'bert_category_trajectories.png')
    plt.close()

def save_statistics(all_results, data_by_window, output_dir):
    """Save detailed statistics and create bar charts"""
    stats_file = output_dir / 'bert_analysis_statistics.txt'
    
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"{'='*80}\n")
        f.write(f"BERT ANALYSIS RESULTS ({len(all_results)} reflections)\n")
        f.write(f"{'='*80}\n\n")
        
        game_counter = 1
        for window in sorted(data_by_window.keys()):
            for game in data_by_window[window]:
                f.write(f"{'='*80}\n")
                f.write(f"GAME {game_counter} (Window {window})\n")
                f.write(f"{'='*80}\n\n")
                
                prompt_type = game[0].get('prompt_type', 'unknown')
                temp = game[0].get('temperature')

                episode_nums = [ep['episode'] for ep in game]
                game_reflections = [r for r in all_results 
                                  if r['window'] == window and r['episode'] in episode_nums]
                
                agent_0_refl = [r for r in game_reflections if r['agent'] == 'agent_0']
                agent_1_refl = [r for r in game_reflections if r['agent'] == 'agent_1']
                
                # Build categories dicts BEFORE the writing loop
                categories_0 = {}
                for r in agent_0_refl:
                    cat = r['moral_category']
                    categories_0[cat] = categories_0.get(cat, 0) + 1

                categories_1 = {}
                for r in agent_1_refl:
                    cat = r['moral_category']
                    categories_1[cat] = categories_1.get(cat, 0) + 1

                # Process both agents — pass categories directly as tuple element
                for agent_num, agent_refl, categories in [
                    (0, agent_0_refl, categories_0),
                    (1, agent_1_refl, categories_1)
                ]:
                    f.write(f"{'AGENT ' + str(agent_num)} ({len(agent_refl)} reflections)\n")
                    f.write("-"*80 + "\n\n")
                    
                    f.write("Moral Category Distribution:\n")
                    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                        pct = (count / len(agent_refl)) * 100
                        valence = get_moral_valence(cat)
                        f.write(f"  {cat:<40} {count:>3} ({pct:>5.1f}%) [{valence}]\n")
                    
                    positive_count = sum(1 for r in agent_refl if r['moral_valence'] == 'positive')
                    negative_count = sum(1 for r in agent_refl if r['moral_valence'] == 'negative')
                    pos_pct = (positive_count / len(agent_refl)) * 100
                    neg_pct = (negative_count / len(agent_refl)) * 100
                    
                    f.write(f"\nMoral Valence Summary:\n")
                    f.write(f"  Positive moral reasoning: {positive_count:>3} ({pos_pct:>5.1f}%)\n")
                    f.write(f"  Negative moral reasoning: {negative_count:>3} ({neg_pct:>5.1f}%)\n")
                    
                    sophistication = {}
                    for r in agent_refl:
                        level = r['sophistication_level']
                        sophistication[level] = sophistication.get(level, 0) + 1
                    
                    f.write("\nMoral Sophistication Distribution:\n")
                    for level in ['Level 0 - Reactive', 'Level 1 - Simple Moral', 
                                'Level 2 - Moral Reasoning', 'Level 3 - Complex Moral']:
                        count = sophistication.get(level, 0)
                        pct = (count / len(agent_refl)) * 100
                        f.write(f"  {level:<35} {count:>3} ({pct:>5.1f}%)\n")
                    
                    avg_cat_conf = np.mean([r['category_confidence'] for r in agent_refl])
                    avg_soph_conf = np.mean([r['sophistication_confidence'] for r in agent_refl])
                    avg_sentiment = np.mean([r['sentiment'] for r in agent_refl])
                    avg_moral_density = np.mean([r['moral_density'] for r in agent_refl])
                    
                    f.write(f"\nAverage Scores:\n")
                    f.write(f"  Category Confidence:     {avg_cat_conf:.3f}\n")
                    f.write(f"  Sophistication:          {avg_soph_conf:.3f}\n")
                    f.write(f"  Sentiment:               {avg_sentiment:.3f}\n")
                    f.write(f"  Moral Density:           {avg_moral_density:.2f}%\n")
                    
                    best = max(agent_refl, key=lambda x: x['sophistication_confidence'])
                    f.write(f"\nHighest Sophistication Example ({best['sophistication_level']}):\n")
                    f.write(f"  \"{best['reflection'][:200]}...\"\n\n")
                
                # Now categories_0 and categories_1 are guaranteed correct for this game
                if HAS_MATPLOTLIB:
                    create_game_bar_chart(categories_0, categories_1, 
                                        len(agent_0_refl), len(agent_1_refl),
                                        game_counter, window, output_dir,
                                        prompt_type=prompt_type, temp=temp)
                
                game_counter += 1
        
        f.write(f"\n{'='*80}\n")
        f.write("BERT analysis complete!\n")
    
    print(f"\n✓ Statistics saved to: {stats_file}")

def create_game_bar_chart(categories_0, categories_1, n_refl_0, n_refl_1, 
                          game_num, window, output_dir, prompt_type, temp):
    """Create bar chart for a single game"""
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(14, 5), facecolor='white')
    
    for ax, categories, n_refl, color, agent_num in [
        (ax0, categories_0, n_refl_0, '#3498db', 0),
        (ax1, categories_1, n_refl_1, '#e74c3c', 1)
    ]:
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        cats = [item[0] for item in sorted_cats]
        counts = [item[1] for item in sorted_cats]
        pcts = [(c / n_refl) * 100 for c in counts]
        
        y_pos = np.arange(len(cats))
        bars = ax.barh(y_pos, counts, color=color, edgecolor='#2c3e50', 
                      linewidth=1.5, alpha=0.9)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(cats, fontsize=11)
        ax.set_xlabel('Count', fontsize=12, fontweight='bold')
        ax.set_title(f'Agent {agent_num}', fontsize=13, fontweight='bold')
        ax.invert_yaxis()
        
        for bar, pct in zip(bars, pcts):
            width = bar.get_width()
            ax.text(width + 0.3, bar.get_y() + bar.get_height()/2.,
                   f'{int(width)} ({pct:.1f}%)', ha='left', va='center', fontsize=10)
        
        apply_plot_styling(ax)
    
    fig.suptitle(f'Game {game_num} | prompt={prompt_type}  h={window}  t={temp} - Moral Categories', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    save_figure(fig, output_dir / f'bert_categories_game{game_num}.png')
    plt.close()

def add_bert_sentiment_to_games(json_files, output_dir=None):
    """
    Calculate BERT sentiment for existing game files and optionally save updated versions.
    Can be imported and used by other scripts without loading models twice.
    
    Args:
        json_files: List of JSON file paths
        output_dir: Optional directory to save updated JSON files with sentiment data
        
    Returns:
        dict: Mapping of filename to sentiment data
    """
    results = {}
    
    for filepath in json_files:
        data = load_json_file(filepath)
        file_key = Path(filepath).name
        results[file_key] = {'episodes': []}
        
        for episode in data['episodes']:
            ep_sentiments = {}
            
            for agent_key in ['agent_0', 'agent_1']:
                reflection = episode[agent_key].get('reflection', '')
                if reflection:
                    sentiment = bert_sentiment_score(reflection)
                    ep_sentiments[agent_key] = sentiment
                    
                    # Optionally add to episode data
                    if output_dir:
                        episode[agent_key]['bert_sentiment'] = sentiment
            
            results[file_key]['episodes'].append({
                'episode': episode['episode'],
                'sentiments': ep_sentiments
            })
        
        # Save updated file if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / file_key
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    return results

def calculate_prompt_sentiment_means(json_files):
    """Calculate average sentiment for each prompt type"""
    import pandas as pd
    
    all_data = []
    
    for json_file in json_files:
        data = load_json_file(json_file)
        prompt_type = get_prompt_type(json_file)
        # Calculate sentiment for each episode
        for episode in data['episodes']:
            sentiments = []
            
            for agent_key in ['agent_0', 'agent_1']:
                reflection = episode[agent_key].get('reflection', '')
                if reflection:
                    sentiment = bert_sentiment_score(reflection)
                    sentiments.append(sentiment)
            
            if sentiments:
                all_data.append({
                    'prompt_type': prompt_type,
                    'episode': episode['episode'],
                    'sentiment': sum(sentiments) / len(sentiments)
                })
    
    df = pd.DataFrame(all_data)
    
    # Calculate means by prompt type and episode
    means_dict = {}
    for prompt_type in df['prompt_type'].unique():
        if prompt_type != 'unknown':
            prompt_df = df[df['prompt_type'] == prompt_type]
            episode_means = prompt_df.groupby('episode')['sentiment'].mean().to_dict()
            means_dict[prompt_type] = episode_means
    
    return means_dict

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="BERT analysis of reflections")
    parser.add_argument('--results-dir', type=str, default='results',
                       help='Directory containing JSON result files')
    parser.add_argument('--output-dir', type=str, default='graphs_stats',
                       help='Directory to save output files')
    parser.add_argument('--sample', type=int, default=None, 
                       help='Analyze only first N reflections (for testing)')
    
    args = parser.parse_args()
    
    try:
        # Load game files using shared function
        files = load_game_files(args.results_dir)
        print(f"Found {len(files)} game files")
        print("Analyzing reflections with BERT...\n")
        # Create output directory using shared function
        output_dir = create_output_directory(args.output_dir)
        all_results = []
        data_by_window = defaultdict(list)
        
        for i, filepath in enumerate(files, 1):
            print_progress(i, len(files), "Processing files")
            
            try:
                file_results, episode_metrics = analyze_game_file(filepath)
                all_results.extend(file_results)
                
                if episode_metrics:
                    window = episode_metrics[0]['window']
                    data_by_window[window].append(episode_metrics)
                
                if args.sample and len(all_results) >= args.sample:
                    all_results = all_results[:args.sample]
                    break
                    
            except Exception as e:
                print(f"\n  Error processing {Path(filepath).name}: {e}")
                continue
        
        if not all_results:
            print("No reflections to analyze")
            return
        
        # Save statistics and create bar charts
        print("\nGenerating statistics and charts...")
        save_statistics(all_results, data_by_window, output_dir)
        
        # Generate visualization plots
        if data_by_window and HAS_MATPLOTLIB:
            print("Generating visualization plots...")
            
            plot_sentiment_moral_density(data_by_window, 
                                        output_dir / 'bert_sentiment_moral.png')
            plot_sophistication_cooperation(data_by_window, 
                                           output_dir / 'bert_sophistication_cooperation.png')
            plot_moral_valence_trajectory(all_results, data_by_window,
                                         output_dir / 'bert_moral_valence_cooperation.png')
            plot_moral_category_trajectory(all_results, data_by_window, output_dir)
            
            print(f"\n✓ All plots saved to: {output_dir}/")
        
        print("\n✓ BERT analysis complete!")
        
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
