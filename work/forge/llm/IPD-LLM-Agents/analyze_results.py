#!/usr/bin/env python3
"""
Analyze results from LLM IPD games
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np


def load_game_results(filepath: str) -> Dict:
    """Load game results from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def plot_cooperation_over_time(results: Dict, output_path: str = None):
    """Plot cooperation rate over time (moving average)"""
    rounds = results['rounds']
    
    # Extract actions
    actions_0 = [1 if r['agent_0_action'] == 'COOPERATE' else 0 for r in rounds]
    actions_1 = [1 if r['agent_1_action'] == 'COOPERATE' else 0 for r in rounds]
    
    # Calculate moving average (window size = 10)
    window = 10
    moving_avg_0 = np.convolve(actions_0, np.ones(window)/window, mode='valid')
    moving_avg_1 = np.convolve(actions_1, np.ones(window)/window, mode='valid')
    
    # Plot
    plt.figure(figsize=(12, 6))
    
    x = range(window-1, len(actions_0))
    plt.plot(x, moving_avg_0, label='Agent 0', linewidth=2, alpha=0.8)
    plt.plot(x, moving_avg_1, label='Agent 1', linewidth=2, alpha=0.8)
    
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50% cooperation')
    
    plt.xlabel('Round')
    plt.ylabel('Cooperation Rate (moving avg)')
    plt.title(f'Cooperation Over Time (window={window})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(-0.05, 1.05)
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Cooperation plot saved to: {output_path}")
    else:
        plt.show()


def plot_cumulative_scores(results: Dict, output_path: str = None):
    """Plot cumulative scores over time"""
    rounds = results['rounds']
    
    scores_0 = [r['agent_0_score'] for r in rounds]
    scores_1 = [r['agent_1_score'] for r in rounds]
    
    plt.figure(figsize=(12, 6))
    
    plt.plot(range(1, len(scores_0) + 1), scores_0, label='Agent 0', linewidth=2)
    plt.plot(range(1, len(scores_1) + 1), scores_1, label='Agent 1', linewidth=2)
    
    # Reference line: if both always cooperated
    optimal = [3 * i for i in range(1, len(scores_0) + 1)]
    plt.plot(range(1, len(optimal) + 1), optimal, 
             label='Optimal (always cooperate)', 
             linestyle='--', color='green', alpha=0.5)
    
    plt.xlabel('Round')
    plt.ylabel('Cumulative Score')
    plt.title('Cumulative Scores Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Scores plot saved to: {output_path}")
    else:
        plt.show()


def analyze_strategy_transitions(results: Dict):
    """Analyze how strategies change over time"""
    rounds = results['rounds']
    
    # Divide into phases
    n = len(rounds)
    early = rounds[:n//3]
    mid = rounds[n//3:2*n//3]
    late = rounds[2*n//3:]
    
    phases = [('Early', early), ('Middle', mid), ('Late', late)]
    
    print("\n" + "="*60)
    print("STRATEGY TRANSITIONS")
    print("="*60)
    
    for phase_name, phase_rounds in phases:
        coop_0 = sum(1 for r in phase_rounds if r['agent_0_action'] == 'COOPERATE')
        coop_1 = sum(1 for r in phase_rounds if r['agent_1_action'] == 'COOPERATE')
        
        mutual_coop = sum(1 for r in phase_rounds 
                         if r['agent_0_action'] == 'COOPERATE' 
                         and r['agent_1_action'] == 'COOPERATE')
        
        mutual_defect = sum(1 for r in phase_rounds 
                           if r['agent_0_action'] == 'DEFECT' 
                           and r['agent_1_action'] == 'DEFECT')
        
        print(f"\n{phase_name} phase (rounds {phase_rounds[0]['round']}-{phase_rounds[-1]['round']}):")
        print(f"  Agent 0 cooperation: {coop_0/len(phase_rounds)*100:.1f}%")
        print(f"  Agent 1 cooperation: {coop_1/len(phase_rounds)*100:.1f}%")
        print(f"  Mutual cooperation: {mutual_coop/len(phase_rounds)*100:.1f}%")
        print(f"  Mutual defection: {mutual_defect/len(phase_rounds)*100:.1f}%")


def print_summary_statistics(results: Dict):
    """Print summary statistics"""
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    print(f"\nGame duration: {results['num_rounds']} rounds")
    print(f"Time elapsed: {results['elapsed_seconds']:.1f} seconds")
    print(f"Average time per round: {results['elapsed_seconds']/results['num_rounds']:.2f} seconds")
    
    print(f"\nAgent 0 ({results['agent_0']['model']}):")
    print(f"  Final score: {results['agent_0']['final_score']}")
    print(f"  Cooperation rate: {results['agent_0']['cooperation_rate']*100:.1f}%")
    print(f"  Average points per round: {results['agent_0']['final_score']/results['num_rounds']:.2f}")
    
    print(f"\nAgent 1 ({results['agent_1']['model']}):")
    print(f"  Final score: {results['agent_1']['final_score']}")
    print(f"  Cooperation rate: {results['agent_1']['cooperation_rate']*100:.1f}%")
    print(f"  Average points per round: {results['agent_1']['final_score']/results['num_rounds']:.2f}")
    
    # Calculate outcome frequencies
    rounds = results['rounds']
    cc = sum(1 for r in rounds if r['agent_0_action'] == 'COOPERATE' and r['agent_1_action'] == 'COOPERATE')
    cd = sum(1 for r in rounds if r['agent_0_action'] == 'COOPERATE' and r['agent_1_action'] == 'DEFECT')
    dc = sum(1 for r in rounds if r['agent_0_action'] == 'DEFECT' and r['agent_1_action'] == 'COOPERATE')
    dd = sum(1 for r in rounds if r['agent_0_action'] == 'DEFECT' and r['agent_1_action'] == 'DEFECT')
    
    print(f"\nOutcome frequencies:")
    print(f"  Both cooperate (C,C): {cc} ({cc/results['num_rounds']*100:.1f}%)")
    print(f"  Agent 0 exploited (C,D): {cd} ({cd/results['num_rounds']*100:.1f}%)")
    print(f"  Agent 1 exploited (D,C): {dc} ({dc/results['num_rounds']*100:.1f}%)")
    print(f"  Both defect (D,D): {dd} ({dd/results['num_rounds']*100:.1f}%)")


def extract_key_reasoning(results: Dict, num_samples: int = 5):
    """Extract sample reasoning from key moments"""
    rounds = results['rounds']
    n = len(rounds)
    
    print("\n" + "="*60)
    print("SAMPLE REASONING AT KEY MOMENTS")
    print("="*60)
    
    # First round
    print(f"\n--- Round 1 (Initial decisions) ---")
    print(f"Agent 0 -> {rounds[0]['agent_0_action']}:")
    print(f"  {rounds[0]['agent_0_reasoning'][:200]}...")
    print(f"Agent 1 -> {rounds[1]['agent_1_action']}:")
    print(f"  {rounds[0]['agent_1_reasoning'][:200]}...")
    
    # Middle round
    mid = n // 2
    print(f"\n--- Round {mid} (Middle of game) ---")
    print(f"Agent 0 -> {rounds[mid-1]['agent_0_action']}:")
    print(f"  {rounds[mid-1]['agent_0_reasoning'][:200]}...")
    print(f"Agent 1 -> {rounds[mid-1]['agent_1_action']}:")
    print(f"  {rounds[mid-1]['agent_1_reasoning'][:200]}...")
    
    # Final round
    print(f"\n--- Round {n} (Final round) ---")
    print(f"Agent 0 -> {rounds[-1]['agent_0_action']}:")
    print(f"  {rounds[-1]['agent_0_reasoning'][:200]}...")
    print(f"Agent 1 -> {rounds[-1]['agent_1_action']}:")
    print(f"  {rounds[-1]['agent_1_reasoning'][:200]}...")
    
    # Reflections
    print("\n" + "="*60)
    print("POST-GAME REFLECTIONS")
    print("="*60)
    print(f"\nAgent 0:")
    print(f"  {results['agent_0']['reflection']}")
    print(f"\nAgent 1:")
    print(f"  {results['agent_1']['reflection']}")


def main():
    parser = argparse.ArgumentParser(description="Analyze LLM IPD game results")
    parser.add_argument(
        "results_file",
        type=str,
        help="Path to results JSON file"
    )
    parser.add_argument(
        "--plots",
        action="store_true",
        help="Generate and save plots"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for plot outputs (default: same as results file)"
    )
    
    args = parser.parse_args()
    
    # Load results
    results = load_game_results(args.results_file)
    
    # Print analyses
    print_summary_statistics(results)
    analyze_strategy_transitions(results)
    extract_key_reasoning(results)
    
    # Generate plots if requested
    if args.plots:
        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            output_dir = Path(args.results_file).parent
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate plots
        base_name = Path(args.results_file).stem
        plot_cooperation_over_time(
            results,
            output_path=output_dir / f"{base_name}_cooperation.png"
        )
        plot_cumulative_scores(
            results,
            output_path=output_dir / f"{base_name}_scores.png"
        )


if __name__ == "__main__":
    main()
