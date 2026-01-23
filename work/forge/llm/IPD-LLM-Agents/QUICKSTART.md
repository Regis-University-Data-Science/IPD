# Quick Start Guide: LLM IPD Experiments

## Setup (First Time Only)

1. **Install dependencies:**
```bash
cd /home/dhart/work/forge/llm/IPD-LLM-Agents
pip install -r requirements.txt
```

2. **Verify Ollama services are running:**
```bash
cd /home/dhart/work/forge/llm
./status-cluster.sh
```

If services are not running:
```bash
./start-cluster.sh
```

3. **Test connectivity:**
```bash
cd /home/dhart/work/forge/llm/IPD-LLM-Agents
python test_connection.py
```

You should see "✅ All tests passed! System is ready."

## Running Your First Experiment

### Basic 100-round game (both agents use llama3 on iron)
```bash
python ipd_llm_game.py
```

Expected runtime: ~10-15 minutes (about 6-9 seconds per round)

### What you'll see:
```
================================================================================
Starting IPD Game: 100 rounds
Agent 0: llama3:8b-instruct-q5_K_M
Agent 1: llama3:8b-instruct-q5_K_M
================================================================================

--- Round 1/100 ---
  Agent 0: COOPERATE (payoff: 0, total: 0)
  Agent 1: DEFECT (payoff: 5, total: 5)

--- Round 2/100 ---
  ...

  Progress: Round 10/100
  Agent 0 cooperation rate: 45.0%
  Agent 1 cooperation rate: 60.0%

...

================================================================================
GAME SUMMARY
================================================================================
Total rounds: 100
...
```

### Results will be saved to:
```
results/game_YYYYMMDD_HHMMSS.json
```

## Analyzing Results

### View summary and key reasoning:
```bash
python analyze_results.py results/game_20241222_120000.json
```

### Generate plots:
```bash
python analyze_results.py results/game_20241222_120000.json --plots
```

This creates:
- `results/game_20241222_120000_cooperation.png`
- `results/game_20241222_120000_scores.png`

## Common Experiments

### 1. Short test run (20 rounds)
```bash
python ipd_llm_game.py --rounds 20
```
Good for testing; runs in ~2-3 minutes

### 2. Longer game (200 rounds)
```bash
python ipd_llm_game.py --rounds 200
```
Better for seeing full convergence; ~25-30 minutes

### 3. Different models (mixtral vs llama3)
```bash
python ipd_llm_game.py \
  --model-0 mixtral-multi \
  --host-0 nickel \
  --model-1 llama3:8b-instruct-q5_K_M \
  --host-1 iron \
  --rounds 100
```

### 4. Lower temperature (more deterministic)
```bash
python ipd_llm_game.py --temperature 0.3
```

### 5. Quiet mode (for batch processing)
```bash
python ipd_llm_game.py --quiet --output experiment_01.json
```

## What to Look For

### 1. Emergence of Cooperation
Check the cooperation rate plots. You should see:
- Early phase: Mixed behavior (maybe 30-60% cooperation)
- Middle phase: Increasing cooperation
- Late phase: High mutual cooperation (ideally >80%)

### 2. Agent Reasoning
Look at the sample reasoning in analysis output:
- Do agents reference opponent's past actions?
- Do they mention maximizing total points?
- Do they talk about establishing patterns or trust?

### 3. Post-Game Reflections
The reflections should explain:
- "Cooperation yields higher cumulative rewards"
- Recognition of reciprocity patterns
- Strategic reasoning about long-term vs. short-term gains

## Troubleshooting

### "Connection refused" errors
```bash
# Check Ollama services
cd /home/dhart/work/forge/llm
./status-cluster.sh

# Restart if needed
./start-cluster.sh
```

### Agent responses are ambiguous
- Try lowering temperature: `--temperature 0.3`
- Check if model is loaded properly on the specified host

### Out of memory errors
- Use lighter models (phi3-mini, mistral:7b)
- Reduce number of rounds
- Run one agent at a time on different hosts

## Next Steps

Once you have successful emergence:

1. **Run multiple trials** (5-10 games) to ensure consistency
2. **Compare different model pairs** (mixtral vs llama3, etc.)
3. **Analyze moral language** in reflections (fairness, reciprocity, trust)
4. **Compare to RL results** from `/work/forge/rllib/IPD-Two-Agents/`

## For GENESIS Research

Document:
- Cooperation rate convergence patterns
- Time to emergence (which round cooperation stabilizes)
- Agent explanations mapped to Haidt's moral foundations
- Comparison between LLM reasoning and RL value functions
