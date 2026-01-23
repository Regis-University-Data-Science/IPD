#!/usr/bin/env python3
"""
Run multiple IPD experiments for statistical analysis
"""

import subprocess
import time
from pathlib import Path
from datetime import datetime
import json


def run_experiment(
    experiment_name: str,
    rounds: int = 100,
    model_0: str = "llama3:8b-instruct-q5_K_M",
    host_0: str = "iron",
    model_1: str = "llama3:8b-instruct-q5_K_M",
    host_1: str = "iron",
    temperature: float = 0.7
):
    """Run a single experiment"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/{experiment_name}_{timestamp}.json"
    
    cmd = [
        "python", "ipd_llm_game.py",
        "--rounds", str(rounds),
        "--model-0", model_0,
        "--host-0", host_0,
        "--model-1", model_1,
        "--host-1", host_1,
        "--temperature", str(temperature),
        "--output", output_file,
        "--quiet"
    ]
    
    print(f"\n{'='*80}")
    print(f"Running: {experiment_name}")
    print(f"Config: {model_0} vs {model_1}, {rounds} rounds, temp={temperature}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    result = subprocess.run(cmd)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"\n✅ Completed in {elapsed:.1f} seconds")
        print(f"   Results: {output_file}")
        return output_file, True
    else:
        print(f"\n❌ Failed with return code {result.returncode}")
        return None, False


def run_batch_experiments():
    """Run a batch of experiments for GENESIS research"""
    
    experiments = [
        # Baseline: Same model, multiple runs
        {
            "name": "baseline_run1",
            "rounds": 100,
            "model_0": "llama3:8b-instruct-q5_K_M",
            "host_0": "iron",
            "model_1": "llama3:8b-instruct-q5_K_M",
            "host_1": "iron",
            "temperature": 0.7
        },
        {
            "name": "baseline_run2",
            "rounds": 100,
            "model_0": "llama3:8b-instruct-q5_K_M",
            "host_0": "iron",
            "model_1": "llama3:8b-instruct-q5_K_M",
            "host_1": "iron",
            "temperature": 0.7
        },
        {
            "name": "baseline_run3",
            "rounds": 100,
            "model_0": "llama3:8b-instruct-q5_K_M",
            "host_0": "iron",
            "model_1": "llama3:8b-instruct-q5_K_M",
            "host_1": "iron",
            "temperature": 0.7
        },
        
        # Temperature variation
        {
            "name": "low_temp",
            "rounds": 100,
            "model_0": "llama3:8b-instruct-q5_K_M",
            "host_0": "iron",
            "model_1": "llama3:8b-instruct-q5_K_M",
            "host_1": "iron",
            "temperature": 0.3
        },
        {
            "name": "high_temp",
            "rounds": 100,
            "model_0": "llama3:8b-instruct-q5_K_M",
            "host_0": "iron",
            "model_1": "llama3:8b-instruct-q5_K_M",
            "host_1": "iron",
            "temperature": 1.0
        },
        
        # Heterogeneous models
        {
            "name": "mixtral_vs_llama3",
            "rounds": 100,
            "model_0": "mixtral-multi",
            "host_0": "nickel",
            "model_1": "llama3:8b-instruct-q5_K_M",
            "host_1": "iron",
            "temperature": 0.7
        },
        {
            "name": "mistral_vs_llama3",
            "rounds": 100,
            "model_0": "mistral:7b-instruct-q5_K_M",
            "host_0": "copper",
            "model_1": "llama3:8b-instruct-q5_K_M",
            "host_1": "iron",
            "temperature": 0.7
        },
    ]
    
    results_summary = []
    successful = 0
    failed = 0
    
    print("\n" + "="*80)
    print("BATCH EXPERIMENT RUN FOR GENESIS")
    print(f"Total experiments: {len(experiments)}")
    print("="*80)
    
    for i, exp_config in enumerate(experiments, 1):
        print(f"\n[{i}/{len(experiments)}] Starting: {exp_config['name']}")
        
        output_file, success = run_experiment(**exp_config)
        
        if success:
            successful += 1
            # Load results to get cooperation rate
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            results_summary.append({
                "experiment": exp_config['name'],
                "output_file": output_file,
                "cooperation_rate_0": data['agent_0']['cooperation_rate'],
                "cooperation_rate_1": data['agent_1']['cooperation_rate'],
                "final_score_0": data['agent_0']['final_score'],
                "final_score_1": data['agent_1']['final_score'],
            })
        else:
            failed += 1
        
        # Pause between experiments to avoid overloading
        if i < len(experiments):
            print("\nPausing 10 seconds before next experiment...")
            time.sleep(10)
    
    # Summary report
    print("\n" + "="*80)
    print("BATCH EXPERIMENT SUMMARY")
    print("="*80)
    print(f"\nCompleted: {successful}/{len(experiments)}")
    print(f"Failed: {failed}/{len(experiments)}")
    
    if results_summary:
        print("\nResults Summary:")
        print(f"{'Experiment':<25} {'Coop-0':>8} {'Coop-1':>8} {'Score-0':>9} {'Score-1':>9}")
        print("-" * 80)
        for r in results_summary:
            print(f"{r['experiment']:<25} "
                  f"{r['cooperation_rate_0']*100:>7.1f}% "
                  f"{r['cooperation_rate_1']*100:>7.1f}% "
                  f"{r['final_score_0']:>9.0f} "
                  f"{r['final_score_1']:>9.0f}")
        
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
        "--batch",
        action="store_true",
        help="Run full batch of experiments"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick test batch (3 short experiments)"
    )
    
    args = parser.parse_args()
    
    if args.batch:
        run_batch_experiments()
    elif args.quick:
        # Quick test batch
        print("Running quick test batch (3 experiments, 20 rounds each)...")
        for i in range(3):
            run_experiment(
                experiment_name=f"quick_test_{i+1}",
                rounds=20,
                model_0="llama3:8b-instruct-q5_K_M",
                host_0="iron",
                model_1="llama3:8b-instruct-q5_K_M",
                host_1="iron",
                temperature=0.7
            )
            if i < 2:
                time.sleep(5)
    else:
        print("Usage:")
        print("  python run_batch.py --batch      # Run full experiment batch")
        print("  python run_batch.py --quick      # Run quick test (3x20 rounds)")


if __name__ == "__main__":
    main()
