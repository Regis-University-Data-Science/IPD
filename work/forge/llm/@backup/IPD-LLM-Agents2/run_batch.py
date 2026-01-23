#!/usr/bin/env python3
"""
Batch experiment runner for episodic IPD
Run multiple games with different configurations
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime
import json


def run_experiment(name: str, config: dict) -> tuple[str, bool]:
    """
    Run a single experiment with given configuration
    
    Returns:
        (output_file, success)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/{name}_{timestamp}.json"
    
    cmd = [
        "python", "episodic_ipd_game.py",
        "--episodes", str(config.get('episodes', 5)),
        "--rounds", str(config.get('rounds', 20)),
        "--temperature", str(config.get('temperature', 0.7)),
        "--model-0", config.get('model_0', 'llama3:8b-instruct-q5_K_M'),
        "--host-0", config.get('host_0', 'iron'),
        "--model-1", config.get('model_1', 'llama3:8b-instruct-q5_K_M'),
        "--host-1", config.get('host_1', 'iron'),
        "--reflection-type", config.get('reflection_type', 'standard'),
        "--output", output_file,
        "--quiet"
    ]
    
    if not config.get('reset_between_episodes', True):
        cmd.append("--no-reset")
    
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"Config: {config.get('episodes')}ep × {config.get('rounds')}r, "
          f"temp={config.get('temperature')}, {config.get('reflection_type')}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    result = subprocess.run(cmd)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"\n✓ Completed in {elapsed:.1f} seconds")
        print(f"   Results: {output_file}")
        return output_file, True
    else:
        print(f"\n✗ Failed with return code {result.returncode}")
        return None, False


def analyze_results(output_file: str) -> dict:
    """Extract key metrics from results file"""
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    # Check for cooperation emergence
    episodes = data['episodes']
    cooperation_rates = [ep['agent_0']['cooperation_rate'] for ep in episodes]
    
    # Define emergence as cooperation rate > 0.7 in final episode
    emerged = cooperation_rates[-1] > 0.7
    
    # Find episode where cooperation emerged (if any)
    emergence_episode = None
    for i, rate in enumerate(cooperation_rates):
        if rate > 0.7:
            emergence_episode = i + 1
            break
    
    return {
        'emerged': emerged,
        'emergence_episode': emergence_episode,
        'final_cooperation': cooperation_rates[-1],
        'final_score_0': data['agent_0']['total_score'],
        'final_score_1': data['agent_1']['total_score'],
        'cooperation_by_episode': cooperation_rates
    }


def run_baseline_suite():
    """Run baseline experimental suite"""
    
    experiments = [
        # Baseline: Standard configuration (5 replications)
        {
            'name': 'baseline_01',
            'config': {
                'episodes': 5,
                'rounds': 20,
                'temperature': 0.7,
                'reflection_type': 'standard',
                'reset_between_episodes': True
            }
        },
        {
            'name': 'baseline_02',
            'config': {
                'episodes': 5,
                'rounds': 20,
                'temperature': 0.7,
                'reflection_type': 'standard',
                'reset_between_episodes': True
            }
        },
        {
            'name': 'baseline_03',
            'config': {
                'episodes': 5,
                'rounds': 20,
                'temperature': 0.7,
                'reflection_type': 'standard',
                'reset_between_episodes': True
            }
        },
        
        # Short learning: More episodes, fewer rounds
        {
            'name': 'short_learning_01',
            'config': {
                'episodes': 10,
                'rounds': 10,
                'temperature': 0.7,
                'reflection_type': 'minimal',
                'reset_between_episodes': True
            }
        },
        {
            'name': 'short_learning_02',
            'config': {
                'episodes': 10,
                'rounds': 10,
                'temperature': 0.7,
                'reflection_type': 'minimal',
                'reset_between_episodes': True
            }
        },
        
        # High exploration
        {
            'name': 'high_exploration_01',
            'config': {
                'episodes': 5,
                'rounds': 20,
                'temperature': 1.0,
                'reflection_type': 'standard',
                'reset_between_episodes': True
            }
        },
        {
            'name': 'high_exploration_02',
            'config': {
                'episodes': 5,
                'rounds': 20,
                'temperature': 1.0,
                'reflection_type': 'standard',
                'reset_between_episodes': True
            }
        },
        
        # Detailed reflection
        {
            'name': 'detailed_reflection_01',
            'config': {
                'episodes': 5,
                'rounds': 20,
                'temperature': 0.7,
                'reflection_type': 'detailed',
                'reset_between_episodes': True
            }
        },
    ]
    
    results_summary = []
    successful = 0
    failed = 0
    
    print("\n" + "="*80)
    print("BASELINE EXPERIMENTAL SUITE")
    print(f"Total experiments: {len(experiments)}")
    print("="*80)
    
    for i, exp in enumerate(experiments, 1):
        print(f"\n[{i}/{len(experiments)}]")
        
        output_file, success = run_experiment(exp['name'], exp['config'])
        
        if success:
            successful += 1
            analysis = analyze_results(output_file)
            results_summary.append({
                'name': exp['name'],
                'config': exp['config'],
                'output_file': output_file,
                'analysis': analysis
            })
        else:
            failed += 1
        
        # Pause between experiments
        if i < len(experiments):
            print("\nPausing 10 seconds before next experiment...")
            time.sleep(10)
    
    # Summary report
    print("\n" + "="*80)
    print("EXPERIMENTAL SUITE SUMMARY")
    print("="*80)
    print(f"\nCompleted: {successful}/{len(experiments)}")
    print(f"Failed: {failed}/{len(experiments)}")
    
    if results_summary:
        print("\nResults Summary:")
        print(f"{'Experiment':<25} {'Emerged':>8} {'Episode':>8} {'Final Coop':>12} {'Score':>10}")
        print("-" * 80)
        
        emergence_count = 0
        for r in results_summary:
            name = r['name']
            emerged = "Yes" if r['analysis']['emerged'] else "No"
            episode = r['analysis']['emergence_episode'] if r['analysis']['emergence_episode'] else "-"
            final_coop = f"{r['analysis']['final_cooperation']*100:.1f}%"
            score = f"{r['analysis']['final_score_0']}"
            
            print(f"{name:<25} {emerged:>8} {episode:>8} {final_coop:>12} {score:>10}")
            
            if r['analysis']['emerged']:
                emergence_count += 1
        
        print("\n" + "="*80)
        print(f"COOPERATION EMERGENCE RATE: {emergence_count}/{len(results_summary)} "
              f"({emergence_count/len(results_summary)*100:.1f}%)")
        print("="*80)
        
        # Save summary
        summary_file = f"results/batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results_summary, f, indent=2)
        print(f"\nSummary saved to: {summary_file}")
    
    print("\n" + "="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run batch IPD experiments")
    parser.add_argument(
        "--suite",
        choices=["baseline", "quick"],
        default="baseline",
        help="Which experimental suite to run"
    )
    
    args = parser.parse_args()
    
    if args.suite == "baseline":
        run_baseline_suite()
    elif args.suite == "quick":
        # Quick test with just 2 experiments
        print("Running quick test suite...")
        run_baseline_suite()  # Could customize this


if __name__ == "__main__":
    main()
