"""
Shared utility functions for IPD analysis
"""

import json
#import glob
import numpy as np
from pathlib import Path
from collections import defaultdict

def load_game_files(results_dir, recursive=False):
    """
    Load all JSON game files from a directory.
    
    Args:
        results_dir: Path to directory containing JSON files
        recursive: If True, search subdirectories as well
        
    Returns:
        list: List of file paths
    """
    results_path = Path(results_dir)
    if not results_path.exists():
        raise FileNotFoundError(f"Directory not found: {results_dir}")
    
    if recursive:
        # Search recursively for all JSON files
        files = list(results_path.rglob("*.json"))
    else:
        # Search only in the specified directory
        files = list(results_path.glob("*.json"))
    
    if not files:
        raise FileNotFoundError(f"No JSON files found in {results_dir}")
    
    return sorted([str(f) for f in files])

def load_json_file(filepath):
    """
    Load and parse a JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        dict: Parsed JSON data
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_config(data):
    """
    Extract configuration from game data.
    
    Args:
        data: Parsed JSON game data
        
    Returns:
        dict: Configuration dictionary
    """
    config = data.get('config', {})
    return {
        'window': config.get('history_window_size', 'unknown'),
        'num_episodes': config.get('num_episodes', 0),
        'rounds_per_episode': config.get('rounds_per_episode', 0)
    }

def get_prompt_type(filepath):
    file_path_lower = str(filepath).lower()
    if 'self' in file_path_lower or 'selfish' in file_path_lower:
        return 'self-interest'
    elif 'neutral' in file_path_lower:
        return 'neutral'
    elif 'moral' in file_path_lower:
        return 'moral'
    return 'unknown'

def group_by_window(all_results):
    """
    Group results by history window size.
    
    Args:
        all_results: List of result dictionaries
        
    Returns:
        dict: Results grouped by window
    """
    by_window = defaultdict(list)
    for result in all_results:
        window = result.get('window', 'unknown')
        by_window[window].append(result)
    return dict(by_window)

def calculate_episode_metrics(game_data, window):
    """
    Calculate per-episode metrics from game data.
    
    Args:
        game_data: Parsed JSON game data
        window: History window size
        
    Returns:
        list: List of episode metric dictionaries
    """
    episode_metrics = []
    
    for episode in game_data.get('episodes', []):
        ep_num = episode['episode']
        coop_0 = episode['agent_0']['cooperation_rate']
        coop_1 = episode['agent_1']['cooperation_rate']
        
        episode_metrics.append({
            'episode': ep_num,
            'window': window,
            'cooperation_rate_0': coop_0,
            'cooperation_rate_1': coop_1,
            'cooperation_rate': (coop_0 + coop_1) / 2
        })
    
    return episode_metrics

def create_output_directory(output_dir):
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir: Path to output directory
        
    Returns:
        Path: Path object for output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def save_figure(fig, filepath, dpi=300):
    """
    Save matplotlib figure with consistent settings.
    
    Args:
        fig: Matplotlib figure object
        filepath: Output file path
        dpi: Resolution (default: 300)
    """
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"Saved: {filepath}")

def calculate_mean_trajectory(trajectories, episode_range):
    """
    Calculate mean trajectory across multiple games.
    
    Args:
        trajectories: List of (episodes, values) tuples
        episode_range: List of episode numbers
        
    Returns:
        list: Mean values per episode
    """
    means = []
    for ep in episode_range:
        vals = [values[eps.index(ep)] for eps, values in trajectories if ep in eps]
        means.append(np.mean(vals) if vals else np.nan)
    return means

def get_episode_range(trajectories):
    """
    Get the full range of episodes across all trajectories.
    
    Args:
        trajectories: List of (episodes, values) tuples
        
    Returns:
        list: Episode range from min to max
    """
    if not trajectories:
        return []
    
    max_ep = max(max(eps) for eps, _ in trajectories)
    min_ep = min(min(eps) for eps, _ in trajectories)
    return list(range(min_ep, max_ep + 1))

def apply_plot_styling(ax, remove_spines=True):
    """
    Apply consistent styling to matplotlib axes.
    
    Args:
        ax: Matplotlib axes object
        remove_spines: Whether to remove top/right spines
    """
    ax.grid(True, alpha=0.2)
    
    if remove_spines:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_linewidth(2)
        ax.spines[spine].set_color('#7f8c8d')

def format_percentage_axis(ax, axis='y'):
    """
    Format axis to display percentages.
    
    Args:
        ax: Matplotlib axes object
        axis: Which axis to format ('y' or 'x')
    """
    if axis == 'y':
        ticks = ax.get_yticks()
        ax.set_yticklabels([f'{int(t)}%' if t == int(t) else f'{t:.0f}%' for t in ticks])
    else:
        ticks = ax.get_xticks()
        ax.set_xticklabels([f'{int(t)}%' if t == int(t) else f'{t:.0f}%' for t in ticks])

def extract_reflections_batch(game_data, window):
    """
    Extract all reflections from a game for batch processing.
    
    Args:
        game_data: Parsed JSON game data
        window: History window size
        
    Returns:
        tuple: (reflections list, metadata list)
    """
    reflections = []
    metadata = []
    
    for episode in game_data.get('episodes', []):
        ep_num = episode['episode']
        coop_0 = episode['agent_0']['cooperation_rate']
        coop_1 = episode['agent_1']['cooperation_rate']
        
        for agent_key in ['agent_0', 'agent_1']:
            reflections.append(episode[agent_key]['reflection'])
            metadata.append({
                'episode': ep_num,
                'agent': agent_key,
                'window': window,
                'coop_0': coop_0,
                'coop_1': coop_1
            })
    
    return reflections, metadata

def organize_results_by_episode(results, metadata, window):
    """
    Organize batched results back into episode structure.
    
    Args:
        results: List of analysis results (same length as metadata)
        metadata: List of metadata dictionaries
        window: History window size
        
    Returns:
        tuple: (results_list, episode_metrics_list)
    """
    episodes_dict = defaultdict(lambda: {'data': [], 'window': window})
    
    for idx, meta in enumerate(metadata):
        ep_num = meta['episode']
        episodes_dict[ep_num]['episode'] = ep_num
        episodes_dict[ep_num]['coop_0'] = meta['coop_0']
        episodes_dict[ep_num]['coop_1'] = meta['coop_1']
        episodes_dict[ep_num]['data'].append({
            'agent': meta['agent'],
            'result': results[idx]
        })
    
    return episodes_dict

def print_progress(current, total, prefix='Processing'):
    """
    Print progress indicator.
    
    Args:
        current: Current iteration number
        total: Total iterations
        prefix: Message prefix
    """
    percentage = (current / total) * 100
    print(f"{prefix} {current}/{total} ({percentage:.1f}%)", end='\r')
    if current == total:
        print()  # New line at completion

def get_prompt_colors(shade='default'):
    """
    Get consistent color palette for prompt types.
    
    Args:
        shade: Color shade variant ('default', 'light', 'dark')
        
    Returns:
        dict: Mapping of prompt_type to hex color
    """
    palettes = {
        'default': {
            'self-interest': '#e74c3c',  # Red
            'neutral': '#95a5a6',        # Gray
            'moral': '#27ae60'           # Green
        },
        'light': {
            'self-interest': '#ec7063',  # Light red
            'neutral': '#bdc3c7',        # Light gray
            'moral': '#52be80'           # Light green
        },
        'dark': {
            'self-interest': '#c0392b',  # Dark red
            'neutral': '#7f8c8d',        # Dark gray
            'moral': '#1e8449'           # Dark green
        }
    }
    
    return palettes.get(shade, palettes['default'])
