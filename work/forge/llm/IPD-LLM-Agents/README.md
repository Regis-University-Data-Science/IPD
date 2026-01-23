# LLM-Based Iterated Prisoner's Dilemma

## Overview

This implementation explores whether cooperation can emerge between LLM agents through in-context learning in an Iterated Prisoner's Dilemma (IPD) game. Unlike traditional RL approaches where agents learn through weight updates and value functions, LLM agents reason about game history using natural language.

## Theoretical Foundation

### The Game
- Two agents play IPD for a fixed number of rounds (default: 100)
- Each round, agents simultaneously choose: COOPERATE or DEFECT
- Payoff matrix:
  - Both cooperate: (3, 3)
  - One defects: (5, 0) for defector, (0, 5) for cooperator
  - Both defect: (1, 1)

### Learning Mechanism
**Traditional RL agents:**
- Learn through Q-value updates and policy gradients
- State = numerical feature vector (history)
- Optimization through backpropagation

**LLM agents:**
- "Learn" through in-context reasoning about conversation history
- State = full narrative of past interactions
- Decision-making through linguistic reasoning

### Research Questions
1. Does cooperation emerge from naive LLM agents?
2. Can agents articulate why they cooperate (reward maximization)?
3. What moral reasoning appears in their explanations?
4. How does this compare to RL-learned cooperation?

## Architecture

```
ollama_agent.py      - Wrapper for Ollama API calls
prompts.py           - System prompts and response parsing
ipd_llm_game.py      - Main game orchestration
analyze_results.py   - Post-game analysis and visualization
```

### Key Design Decisions

**In-Context Learning:**
- Each agent maintains full conversation history
- History includes: actions, outcomes, and previous reasoning
- Agents see up to last 10 rounds in each prompt (or all if <10)

**Naive Initialization:**
- System prompt explains game rules and payoff matrix
- No pre-programmed strategies (no "always cooperate" or "tit-for-tat")
- Goal: "maximize your total points across all rounds"

**Response Format:**
- Agents must explain reasoning (2-3 sentences)
- Then state decision: "COOPERATE" or "DEFECT"
- Reasoning is logged for later analysis

## Installation

Required Python packages:
```bash
pip install requests matplotlib numpy
```

## Usage

### Basic Game (two llama3 agents on iron)
```bash
cd /home/dhart/work/forge/llm/IPD-LLM-Agents
python ipd_llm_game.py --rounds 100
```

### Custom Configuration
```bash
# Different models
python ipd_llm_game.py \
  --model-0 llama3:8b-instruct-q5_K_M \
  --host-0 iron \
  --model-1 mixtral-multi \
  --host-1 nickel \
  --rounds 150

# Lower temperature (more deterministic)
python ipd_llm_game.py --temperature 0.3

# Quiet mode (less verbose)
python ipd_llm_game.py --quiet

# Custom output file
python ipd_llm_game.py --output my_experiment.json
```

### Analyze Results
```bash
# Basic analysis
python analyze_results.py results/game_20241222_120000.json

# Generate plots
python analyze_results.py results/game_20241222_120000.json --plots

# Save plots to specific directory
python analyze_results.py results/game_20241222_120000.json \
  --plots --output-dir analysis_plots/
```

## Expected Behavior

### Hypothesis
Cooperation should emerge over time because:
1. Mutual cooperation (3,3) yields higher cumulative rewards than mutual defection (1,1)
2. LLM agents can reason about patterns in opponent behavior
3. In-context learning allows agents to discover this through experience

### Success Criteria
- **Emergence**: Cooperation rate increases over rounds
- **Convergence**: Late-game shows sustained mutual cooperation
- **Explanation**: Agents articulate reward-based reasoning

### Possible Outcomes

**Scenario 1: Successful Emergence**
- Early rounds: Mixed or defective behavior
- Middle rounds: Increasing cooperation
- Late rounds: High mutual cooperation (>70%)
- Reflections: "Cooperation yields more points over time"

**Scenario 2: Partial Emergence**
- Cooperation increases but doesn't fully stabilize
- Agents recognize pattern but remain cautious
- Reflections mix reward maximization with trust concerns

**Scenario 3: Defection Trap**
- Agents remain stuck in mutual defection
- Unable to escape through in-context reasoning alone
- May indicate need for temperature tuning or longer history

## Output Files

### Game Results (JSON)
```json
{
  "timestamp": "2024-12-22T12:00:00",
  "num_rounds": 100,
  "agent_0": {
    "model": "llama3:8b-instruct-q5_K_M",
    "final_score": 285,
    "cooperation_rate": 0.95,
    "reflection": "..."
  },
  "agent_1": { ... },
  "rounds": [
    {
      "round": 1,
      "agent_0_action": "COOPERATE",
      "agent_0_reasoning": "...",
      "agent_0_payoff": 3,
      ...
    }
  ]
}
```

### Analysis Outputs
- Summary statistics (scores, cooperation rates, outcome frequencies)
- Strategy transitions (early/middle/late game)
- Sample reasoning from key moments
- Post-game reflections

### Plots (if --plots enabled)
- `*_cooperation.png`: Moving average of cooperation rate over time
- `*_scores.png`: Cumulative scores with optimal baseline

## Comparison to RL IPD

### Similarities
- Same MDP formulation (states, actions, payoffs)
- Same episode length and game rules
- Both should converge to cooperation

### Differences
| Aspect | RL Agents | LLM Agents |
|--------|-----------|------------|
| Learning | Weight updates via backprop | In-context reasoning |
| State representation | Numerical features | Natural language narrative |
| Exploration | Epsilon-greedy, temperature | Implicit in LLM sampling |
| Explanation | Not available | Natural language reasoning |
| Training time | Hours/GPUs | Immediate (no training) |
| Memory | Fixed state features | Full conversation history |

## Next Steps for GENESIS

1. **Run baseline experiments:**
   - Multiple games with same configuration
   - Measure emergence frequency and convergence time
   - Collect agent explanations

2. **Compare to RL results:**
   - Use RLlib IPD implementation in `/work/forge/rllib/IPD-Two-Agents/`
   - Document differences in learning curves
   - Compare final cooperation rates

3. **Moral reasoning analysis:**
   - Extract language patterns from reflections
   - Map to Haidt's moral foundations (reciprocity, fairness)
   - Show emergence + explanation capability

4. **Heterogeneous experiments:**
   - Different models (mixtral vs llama3)
   - Different temperatures (exploration effects)
   - Asymmetric information or payoffs

## Available Models

From cluster configuration (`/work/forge/llm/load-model.sh`):
- nickel: mixtral-multi (strongest reasoning)
- zinc: codellama-multi (code-focused)
- copper: mistral:7b-instruct-q5_K_M
- iron: llama3:8b-instruct-q5_K_M
- platinum: phi3-mini-utility (lightweight)

## Notes

- **Context window limits**: With 100 rounds, full history stays manageable. For longer games, may need summarization.
- **Temperature effects**: Higher temperature (0.7-1.0) enables exploration; lower (0.1-0.3) makes agents more deterministic.
- **Robustness**: Error handling includes retries for API failures and defaults to DEFECT on ambiguous responses.
- **Parallelization**: Currently sequential. Could run multiple games in parallel for statistical analysis.

## References

This implementation is part of the GENESIS research program investigating emergent moral behavior in AI systems.

Related work:
- RLlib IPD: `/work/forge/rllib/IPD-Two-Agents/`
- FORGE infrastructure: `/work/forge/llm/`
- Research context: Evolution of cooperation, Haidt's moral foundations theory
