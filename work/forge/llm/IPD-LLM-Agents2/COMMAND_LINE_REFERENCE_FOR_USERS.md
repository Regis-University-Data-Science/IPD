# Episodic IPD with LLM Agents - Command Line Reference
## IPD-LLM-Agents2: A Tool for Studying Emergent Cooperation

**Version:** 2.0  
**Authors:** Doug Hart & Kellen Sorauf, Regis University  
**Project:** GENESIS - General Emergent Norms, Ethics, and Societies in Silico

---

## Overview

This tool simulates iterated prisoner's dilemma (IPD) games between LLM agents to study how cooperation and moral reasoning emerge from strategic interactions. Agents play multiple episodes, reflect on outcomes, and adjust their strategies over time.

---

## Quick Start

### Basic Usage
```bash
# Run with defaults (5 episodes × 20 rounds = 100 total rounds)
python episodic_ipd_game.py

# Quick test (2 episodes × 10 rounds)
python episodic_ipd_game.py --episodes 2 --rounds 10
```

### Viewing Results
Results are saved as JSON files in the `results/` directory with timestamp filenames.

```bash
# View most recent result
ls -lt results/ | head -5

# Pretty print JSON
cat results/episodic_game_20260119_143052.json | python -m json.tool | less
```

---

## Command Line Options

### Game Structure

**--episodes N**  
Number of distinct periods of play (default: 5)
```bash
python episodic_ipd_game.py --episodes 10
```

**--rounds N**  
Number of rounds within each episode (default: 20)
```bash
python episodic_ipd_game.py --rounds 25
```

**--no-reset**  
Keep full conversation history across episodes (default: reset between episodes)
```bash
python episodic_ipd_game.py --no-reset
```

---

### Memory & Context

**--history-window N**  
Number of recent rounds shown to agents in each decision (default: 10)
```bash
# Short memory - agents see only last 5 rounds
python episodic_ipd_game.py --history-window 5

# Long memory - agents see last 20 rounds
python episodic_ipd_game.py --history-window 20

# Full history - agents see all rounds
python episodic_ipd_game.py --history-window 999
```

---

### LLM Configuration

**--temperature T**  
Sampling temperature 0.0-2.0 (default: 0.7)  
Lower = more deterministic, Higher = more exploratory
```bash
# Very deterministic
python episodic_ipd_game.py --temperature 0.3

# More exploratory
python episodic_ipd_game.py --temperature 1.2
```

**--model-0, --model-1**  
Specify LLM model for each agent (default: llama3:8b-instruct-q5_K_M)
```bash
# Use different models
python episodic_ipd_game.py \
  --model-0 "llama3:8b-instruct-q5_K_M" \
  --model-1 "mixtral:7b-instruct-v0.3-q5_K_M"
```

**--host-0, --host-1**  
Ollama server hostname for each agent (default: iron)
```bash
# Distribute across servers
python episodic_ipd_game.py --host-0 iron --host-1 platinum
```

---

### Advanced LLM Parameters (High-Risk)

**--decision-tokens N**  
Max tokens for decision responses (default: 256)
```bash
python episodic_ipd_game.py --decision-tokens 512
```

**--reflection-tokens N**  
Max tokens for reflection responses (default: 1024)
```bash
python episodic_ipd_game.py --reflection-tokens 2048
```

**--http-timeout N**  
HTTP request timeout in seconds (default: 60)
```bash
python episodic_ipd_game.py --http-timeout 120
```

**--force-retries N**  
Number of retries for ambiguous decisions (default: 2)
```bash
python episodic_ipd_game.py --force-retries 3
```

---

### Prompts & Reflection

**--system-prompt FILE**  
Path to system prompt file (default: system_prompt.txt)
```bash
python episodic_ipd_game.py --system-prompt my_custom_prompt.txt
```

**--reflection-template FILE**  
Path to reflection template (default: reflection_prompt_template.txt)
```bash
python episodic_ipd_game.py --reflection-template my_reflection.txt
```

**--reflection-type TYPE**  
Preset reflection verbosity: minimal | standard | detailed (default: standard)
```bash
python episodic_ipd_game.py --reflection-type detailed
```

---

### Output Control

**--output FILE**  
Save results to specific JSON file
```bash
python episodic_ipd_game.py --output results/my_experiment.json
```

**--quiet**  
Reduce console output (results still saved)
```bash
python episodic_ipd_game.py --quiet
```

---

## Common Usage Patterns

### 1. Classic IPD (Single Long Game)
```bash
# Replaces traditional IPD: 1 episode × 100 rounds, no context reset
python episodic_ipd_game.py --episodes 1 --rounds 100 --no-reset
```

### 2. Testing Cooperation Emergence
```bash
# Observe how cooperation develops over many short episodes
python episodic_ipd_game.py --episodes 10 --rounds 10
```

### 3. Memory Window Experiment
```bash
# Compare short vs. long memory effects
python episodic_ipd_game.py --history-window 5 --output results/short_memory.json
python episodic_ipd_game.py --history-window 20 --output results/long_memory.json
```

### 4. Temperature Exploration
```bash
# Test how randomness affects cooperation
python episodic_ipd_game.py --temperature 0.3 --output results/deterministic.json
python episodic_ipd_game.py --temperature 1.2 --output results/exploratory.json
```

### 5. Cross-Model Comparison
```bash
# Different models playing against each other
python episodic_ipd_game.py \
  --model-0 "llama3:8b-instruct-q5_K_M" \
  --model-1 "mistral:7b-instruct-v0.3-q5_K_M" \
  --output results/llama_vs_mistral.json
```

### 6. Custom Prompt Testing
```bash
# Test different framings
cp system_prompt.txt cooperative_prompt.txt
# Edit cooperative_prompt.txt to emphasize mutual benefit

python episodic_ipd_game.py \
  --system-prompt cooperative_prompt.txt \
  --output results/cooperative_framing.json
```

---

## Batch Experiments

### Script: Compare Memory Windows
```bash
#!/bin/bash
# File: compare_windows.sh

for window in 3 5 10 15 20; do
  echo "Testing window size: $window"
  python episodic_ipd_game.py \
    --episodes 5 \
    --rounds 25 \
    --history-window $window \
    --output results/window_${window}.json \
    --quiet
done

echo "Experiments complete!"
```

### Script: Temperature Sweep
```bash
#!/bin/bash
# File: temperature_sweep.sh

for temp in 0.3 0.5 0.7 1.0 1.5; do
  echo "Testing temperature: $temp"
  python episodic_ipd_game.py \
    --episodes 5 \
    --rounds 20 \
    --temperature $temp \
    --output results/temp_${temp}.json \
    --quiet
done
```

### Script: Episode Structure Comparison
```bash
#!/bin/bash
# File: episode_structures.sh

# Many short episodes (more learning opportunities)
python episodic_ipd_game.py --episodes 20 --rounds 5 \
  --output results/struct_20x5.json --quiet

# Moderate structure
python episodic_ipd_game.py --episodes 10 --rounds 10 \
  --output results/struct_10x10.json --quiet

# Few long episodes
python episodic_ipd_game.py --episodes 5 --rounds 20 \
  --output results/struct_5x20.json --quiet

# Single continuous game
python episodic_ipd_game.py --episodes 1 --rounds 100 --no-reset \
  --output results/struct_1x100.json --quiet
```

---

## Understanding Results

### JSON Output Structure
```json
{
  "timestamp": "2026-01-19T14:30:52",
  "hostname": "platinum",
  "prompts": {
    "system_prompt": "You are participating in...",
    "reflection_template": "PERIOD {episode_num}..."
  },
  "config": {
    "num_episodes": 5,
    "rounds_per_episode": 20,
    "total_rounds": 100,
    "history_window_size": 10,
    "temperature": 0.7,
    "decision_token_limit": 256,
    "reflection_token_limit": 1024,
    "http_timeout": 60,
    "force_decision_retries": 2
  },
  "elapsed_seconds": 285.4,
  "agent_0": {
    "total_score": 275,
    "total_cooperations": 68,
    "overall_cooperation_rate": 0.68
  },
  "agent_1": {
    "total_score": 280,
    "total_cooperations": 72,
    "overall_cooperation_rate": 0.72
  },
  "episodes": [
    {
      "episode": 1,
      "rounds": [ /* detailed round data */ ],
      "agent_0": {
        "episode_score": 55,
        "cooperations": 14,
        "cooperation_rate": 0.70,
        "reflection": "..."
      }
    }
  ]
}
```

### Key Metrics to Analyze
- **Cooperation rate**: Percentage of COOPERATE choices
- **Episode scores**: Points earned per episode
- **Cooperation trajectory**: Does cooperation increase over episodes?
- **Agent reflections**: How do agents explain their strategies?

---

## Analyzing Results

### Extract Cooperation Rates
```bash
# Using jq (JSON query tool)
cat results/game.json | jq '.agent_0.overall_cooperation_rate, .agent_1.overall_cooperation_rate'
```

### Compare Experiments
```python
import json
import pandas as pd

# Load multiple results
files = ['results/window_5.json', 'results/window_10.json', 'results/window_20.json']
data = []

for f in files:
    with open(f) as file:
        result = json.load(file)
        data.append({
            'window': result['config']['history_window_size'],
            'agent_0_coop': result['agent_0']['overall_cooperation_rate'],
            'agent_1_coop': result['agent_1']['overall_cooperation_rate']
        })

df = pd.DataFrame(data)
print(df)
```

---

## Typical Execution Times

On FORGE cluster (llama3:8b-instruct-q5_K_M):
- **1 round**: ~2-3 seconds (2 LLM calls)
- **1 episode (20 rounds)**: ~50-60 seconds
- **5 episodes × 20 rounds**: ~5-6 minutes
- **10 episodes × 20 rounds**: ~10-12 minutes

---

## Troubleshooting

### Problem: Ambiguous Responses
**Symptom:** "⚠️ agent_X response ambiguous, defaulting to DEFECT"

**Solutions:**
```bash
# Increase token limit
python episodic_ipd_game.py --decision-tokens 512

# Increase retry attempts
python episodic_ipd_game.py --force-retries 3

# Check system prompt clarity
cat system_prompt.txt
```

### Problem: Slow Execution
**Symptom:** Takes much longer than expected

**Solutions:**
```bash
# Use quiet mode
python episodic_ipd_game.py --quiet

# Reduce reflection verbosity
python episodic_ipd_game.py --reflection-type minimal

# Check server load
ssh iron "htop"
```

### Problem: Model Not Found
**Symptom:** Error about model not available

**Solution:**
```bash
# Check available models
ssh iron "ollama list"

# Pull model if needed
ssh iron "ollama pull llama3:8b-instruct-q5_K_M"
```

### Problem: Timeout Errors
**Symptom:** HTTP timeout exceptions

**Solution:**
```bash
# Increase timeout
python episodic_ipd_game.py --http-timeout 120

# Check network connectivity
ping iron
```

---

## Best Practices

### For Reproducibility
Always specify key parameters explicitly:
```bash
python episodic_ipd_game.py \
  --episodes 5 \
  --rounds 20 \
  --history-window 10 \
  --temperature 0.7 \
  --model-0 "llama3:8b-instruct-q5_K_M" \
  --model-1 "llama3:8b-instruct-q5_K_M" \
  --output results/baseline_$(date +%Y%m%d_%H%M%S).json
```

### For Experiments
- Use descriptive output filenames
- Run pilot tests with `--episodes 1 --rounds 5` first
- Use `--quiet` for batch jobs
- Save experiment parameters in a separate log

### For Teaching/Demos
- Use verbose output (don't use --quiet)
- Use `--reflection-type detailed` to show agent thinking
- Run short experiments (2-3 episodes × 10 rounds)

---

## Parameter Quick Reference Card

```
# GAME STRUCTURE
--episodes N              Number of learning periods (default: 5)
--rounds N                Rounds per episode (default: 20)
--no-reset                Keep full conversation history

# MEMORY
--history-window N        Recent rounds shown to agents (default: 10)

# LLM BASIC
--temperature T           0.0-2.0, higher = more random (default: 0.7)
--model-0 MODEL          Model for agent 0
--model-1 MODEL          Model for agent 1
--host-0 HOST            Server for agent 0 (default: iron)
--host-1 HOST            Server for agent 1 (default: iron)

# LLM ADVANCED (High-Risk)
--decision-tokens N       Decision response limit (default: 256)
--reflection-tokens N     Reflection response limit (default: 1024)
--http-timeout N          Request timeout seconds (default: 60)
--force-retries N         Ambiguity retry attempts (default: 2)

# PROMPTS
--system-prompt FILE      System prompt file (default: system_prompt.txt)
--reflection-template FILE Reflection template (default: reflection_prompt_template.txt)
--reflection-type TYPE    minimal|standard|detailed (default: standard)

# OUTPUT
--output FILE             Result JSON path
--quiet                   Reduce console output
```

---

## Research Design Considerations

### What to Vary
**Independent Variables:**
- History window size (memory capacity)
- Temperature (exploration vs. exploitation)
- Episode structure (learning opportunities)
- System prompt framing (goal interpretation)
- Model architecture (reasoning capabilities)

**Dependent Variables:**
- Cooperation rate (overall and by episode)
- Score trajectories
- Strategy evolution
- Moral reasoning patterns

### Recommended Comparisons
1. **Memory Effects**: windows of 3, 5, 10, 15, 20
2. **Learning Dynamics**: structures of 20×5, 10×10, 5×20, 1×100
3. **Exploration**: temperatures of 0.3, 0.5, 0.7, 1.0, 1.5
4. **Framing**: cooperative, competitive, neutral prompts
5. **Architecture**: different model comparisons

---

## Example Research Workflow

### Day 1: Baseline
```bash
# Establish baseline with default settings
python episodic_ipd_game.py --output results/baseline_001.json
python episodic_ipd_game.py --output results/baseline_002.json
python episodic_ipd_game.py --output results/baseline_003.json
```

### Day 2: Memory Experiment
```bash
# Test memory window effects
for w in 3 5 10 15 20; do
  for rep in 1 2 3; do
    python episodic_ipd_game.py \
      --history-window $w \
      --output results/memory_w${w}_rep${rep}.json \
      --quiet
  done
done
```

### Day 3: Temperature Experiment
```bash
# Test exploration effects
for t in 0.3 0.5 0.7 1.0 1.5; do
  for rep in 1 2 3; do
    python episodic_ipd_game.py \
      --temperature $t \
      --output results/temp_t${t}_rep${rep}.json \
      --quiet
  done
done
```

### Day 4: Analysis
```python
# Aggregate and analyze results
import json
import pandas as pd
import matplotlib.pyplot as plt

# Load and analyze (example code structure)
# ... your analysis here ...
```

---

## Getting Help

### Check Configuration
```bash
python episodic_ipd_game.py --help
```

### View Documentation
```bash
cat README.md
cat IMPLEMENTATION_GUIDE.md
cat HARDCODED_PARAMETERS.md
```

### Check System Status
```bash
# Check available models
ssh iron "ollama list"

# Check cluster status
./status-cluster.sh

# Check disk space
df -h results/
```

---

## Citation

If you use this tool in research, please cite:

```
Hart, D., & Sorauf, K. (2026). GENESIS: Studying Emergent Moral Foundations 
in LLM Agents through Iterated Prisoner's Dilemma. Regis University.
```

---

## Contact

**Doug Hart**: douglas.hart@regis.edu  
**Kellen Sorauf**: kellen.sorauf@regis.edu

**Project Location**: `/home/dhart/work/forge/llm/IPD-LLM-Agents2` on platinum server

---

## Version History

**v2.0** (January 2026)
- Added configurable token limits and timeouts
- Added forced decision retry mechanism
- Added hostname and prompts to JSON output
- Externalized prompts to text files
- Added command-line history window control

**v1.0** (December 2025)
- Initial episodic IPD implementation
- Multiple episodes with reflection
- Context management options
