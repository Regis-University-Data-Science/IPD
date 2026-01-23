# Episodic IPD with Externalized Prompts and Configurable History Window

## Changes Summary

This update adds two major improvements to the IPD-LLM-Agents2 codebase:

1. **Command-line configurable history window** - Control how many rounds of history agents see
2. **Externalized prompts** - Edit prompts in text files without modifying Python code

## New Files

### 1. `system_prompt.txt`
The system prompt that defines the agent's role and response format. Edit this file to modify how agents are instructed to play the game.

### 2. `reflection_prompt_template.txt`
Template for the reflection prompt shown to agents at the end of each episode. Uses Python format strings with these variables:
- `{episode_num}` - Episode number
- `{rounds_in_episode}` - Number of rounds in the episode
- `{my_score}` - Agent's score this episode
- `{opp_score}` - Opponent's score this episode
- `{my_avg}` - Agent's average points per round
- `{my_cooperations}` - Number of times agent cooperated
- `{my_defections}` - Number of times agent defected
- `{opp_cooperations}` - Number of times opponent cooperated
- `{opp_defections}` - Number of times opponent defected
- `{round_history}` - Full history of rounds in the episode

### 3. Updated Python Files
- `prompts_updated.py` - New version with functions to load external prompts
- `episodic_ipd_game_updated.py` - New version with command-line history window parameter

## Usage

### Basic Usage (same as before)
```bash
python episodic_ipd_game_updated.py --episodes 5 --rounds 20
```

### New: Control History Window Size
```bash
# Show only last 5 rounds
python episodic_ipd_game_updated.py --history-window 5

# Show last 20 rounds
python episodic_ipd_game_updated.py --history-window 20

# Show full history (use large number)
python episodic_ipd_game_updated.py --history-window 999
```

### New: Use Custom Prompt Files
```bash
# Use custom system prompt
python episodic_ipd_game_updated.py --system-prompt my_custom_prompt.txt

# Use custom reflection template
python episodic_ipd_game_updated.py --reflection-template my_reflection.txt
```

### Combined Example
```bash
python episodic_ipd_game_updated.py \
  --episodes 10 \
  --rounds 25 \
  --history-window 15 \
  --temperature 0.8 \
  --system-prompt custom_system.txt \
  --reflection-template custom_reflection.txt \
  --output results/my_experiment.json
```

## Experimentation Ideas

### Test Different History Window Sizes
```bash
# Short memory
python episodic_ipd_game_updated.py --history-window 3 --output results/window_3.json

# Medium memory (default)
python episodic_ipd_game_updated.py --history-window 10 --output results/window_10.json

# Long memory
python episodic_ipd_game_updated.py --history-window 20 --output results/window_20.json

# Full history
python episodic_ipd_game_updated.py --history-window 999 --output results/window_full.json
```

### Test Different Prompts
Create variations of `system_prompt.txt` with different instructions:
- More emphasis on cooperation
- More emphasis on maximizing points
- Different language complexity
- Different ethical framing

Then run:
```bash
python episodic_ipd_game_updated.py --system-prompt cooperative_prompt.txt
python episodic_ipd_game_updated.py --system-prompt competitive_prompt.txt
```

## Implementation Details

### Fallback Behavior
- If prompt files are not found, the system uses default prompts built into the code
- A warning is printed when falling back to defaults

### File Locations
- By default, looks for `system_prompt.txt` and `reflection_prompt_template.txt` in the current directory
- You can specify paths to files anywhere using `--system-prompt` and `--reflection-template`

### History Window Limits
- Minimum: 1 round (agents see only the most recent interaction)
- Maximum: Unlimited (but practically limited by LLM context window ~8192 tokens)
- Recommended: 10-20 for optimal performance

## Migration from Old Code

To use these new features in your existing IPD-LLM-Agents2 directory:

1. Copy the new files:
   - `system_prompt.txt`
   - `reflection_prompt_template.txt`
   - Replace `prompts.py` with `prompts_updated.py` (rename it to `prompts.py`)
   - Replace `episodic_ipd_game.py` with `episodic_ipd_game_updated.py` (rename it)

2. Run as before, now with optional new parameters:
   ```bash
   python episodic_ipd_game.py --history-window 15
   ```

## Notes

- The history window only affects what agents SEE in their prompts during gameplay
- It does NOT affect the game state or scoring
- All rounds are still tracked internally and saved in results
- The reflection prompt at the end of each episode shows the FULL episode history regardless of window size
