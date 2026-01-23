# IPD-LLM-Agents2: Episodic Architecture

Episodic Iterated Prisoner's Dilemma with LLM agents that learn through reflection.

## Key Differences from IPD-LLM-Agents

### Architecture
- **Outer loop:** Multiple episodes (e.g., 5 episodes of 20 rounds each)
- **Inner loop:** Standard IPD rounds within each episode
- **Learning mechanism:** Reflection after each episode, fed back into context

### Key Features
1. **Episodic structure:** Game divided into periods with reflection between
2. **Context management:** Optional reset between episodes (keeps reflections, clears tactical history)
3. **Neutral language:** "Participant" not "opponent", "interaction" not "game"
4. **Self-improvement framing:** Agents motivated to maximize their own points
5. **Learning opportunity:** Agents can discover cooperation through iterative reflection

## Files

- `config.py` - Hyperparameter configuration
- `ollama_agent.py` - LLM agent wrapper with reflection context management
- `prompts.py` - Neutral, emergence-friendly prompts
- `episodic_ipd_game.py` - Main game implementation

## Usage

### Basic Run
```bash
python episodic_ipd_game.py
```

### Custom Configuration
```bash
python episodic_ipd_game.py \
  --episodes 5 \
  --rounds 20 \
  --temperature 0.7 \
  --model-0 llama3:8b-instruct-q5_K_M \
  --host-0 iron \
  --reflection-type standard
```

### Arguments
- `--episodes`: Number of learning periods (default: 5)
- `--rounds`: Rounds per episode (default: 20)
- `--temperature`: LLM sampling temperature (default: 0.7)
- `--model-0`, `--model-1`: Model names
- `--host-0`, `--host-1`: Ollama server hosts
- `--no-reset`: Don't reset context between episodes (not recommended)
- `--reflection-type`: minimal, standard, or detailed
- `--output`: Custom output file path
- `--quiet`: Reduce output verbosity

## Hyperparameters

Key configurable parameters (see `config.py`):

### Episode Structure
- `num_episodes`: Number of learning periods
- `rounds_per_episode`: Length of each period
- `total_rounds`: Automatically computed

### Context Management
- `reset_conversation_between_episodes`: Clear tactical history between episodes
- `history_window_size`: Rounds shown explicitly in prompts

### Agent Parameters
- `temperature`: Sampling randomness (0.0-2.0)
- `model_0`, `model_1`: LLM models to use
- `host_0`, `host_1`: Ollama server endpoints

### Reflection Parameters
- `reflection_prompt_type`: minimal/standard/detailed
- `include_statistics`: Show cooperation rates, averages
- `show_other_agent_score`: Display other participant's points

## Predefined Configurations

```python
from config import BASELINE_CONFIG, SHORT_LEARNING_CONFIG, HIGH_EXPLORATION_CONFIG

# Use predefined config
config = BASELINE_CONFIG
```

## Expected Behavior

### Episode 1
- Agents explore, test cooperation
- May get stuck in mutual defection
- Reflect on outcomes

### Episodes 2-3
- Agents try different approaches based on reflections
- May discover that escaping defection trap increases points
- Experimentation with cooperation signals

### Episodes 4-5
- If learning successful: sustained cooperation
- If learning fails: continued defection with recognition it's suboptimal

## Output Format

JSON file containing:
- Configuration used
- Episode-by-episode results
- Round-by-round actions and reasoning
- Agent reflections after each episode
- Overall statistics

## Research Questions

1. Can agents discover cooperation through episodic reflection?
2. What episode does cooperation typically emerge (if at all)?
3. How do different hyperparameters affect learning?
4. Do reflections show strategic evolution over episodes?

## Next Steps

1. Run baseline experiments (10 games with default config)
2. Compare to non-episodic results from IPD-LLM-Agents
3. Vary hyperparameters systematically
4. Analyze reflection content for learning patterns

## Context Window Management

With `reset_conversation_between_episodes=True`:
- Tactical rounds cleared after each episode (~20 rounds × 200 tokens = 4K)
- Reflections preserved (5 reflections × 200 tokens = 1K)
- System prompt maintained (300 tokens)
- Total context: ~5.3K tokens (well within 8K limit)

Without reset:
- All history accumulates
- May hit context limits around episode 3-4
- Not recommended for >3 episodes

## Installation

Requires:
- Python 3.8+
- Ollama running on specified hosts
- requests library: `pip install requests --break-system-packages`

## Comparison to Original

| Feature | IPD-LLM-Agents | IPD-LLM-Agents2 |
|---------|----------------|-----------------|
| Structure | Single 100-round game | 5 episodes of 20 rounds |
| Learning | Post-game reflection only | After each episode |
| Context | Accumulates continuously | Reset with reflections kept |
| Feedback | No learning loop | Reflections fed back |
| Expected | Cooperation collapse | Cooperation emergence |
