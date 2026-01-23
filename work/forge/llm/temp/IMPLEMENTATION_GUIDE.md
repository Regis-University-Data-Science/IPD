# Implementation Guide: Four New Features

## Features to Add

1. **Add machine hostname to JSON output**
2. **Add both prompts (system and reflection) to JSON output**
3. **Add four high-risk parameters as command-line options**
4. **Clarification on ambiguous responses despite clear instructions**

---

## Feature 1: Add Machine Hostname to JSON

### Changes Required:

**In episodic_ipd_game.py:**

1. Add import at top:
```python
import socket
```

2. In `play_game()` method, add to results dictionary:
```python
results = {
    'timestamp': datetime.now().isoformat(),
    'hostname': socket.gethostname(),  # ADD THIS LINE
    'config': {
        ...
    },
    ...
}
```

---

## Feature 2: Add Prompts to JSON Output

### Changes Required:

**In episodic_ipd_game.py:**

1. Modify `__init__` to accept and store prompts:
```python
def __init__(
    self,
    agent_0: OllamaAgent,
    agent_1: OllamaAgent,
    config: EpisodeConfig,
    system_prompt_text: str = "",
    reflection_template_text: str = ""
):
    """Initialize episodic IPD game"""
    self.agent_0 = agent_0
    self.agent_1 = agent_1
    self.config = config
    self.system_prompt_text = system_prompt_text
    self.reflection_template_text = reflection_template_text
    # ... rest of init
```

2. In `play_game()` method, add to results dictionary:
```python
results = {
    'timestamp': datetime.now().isoformat(),
    'hostname': socket.gethostname(),
    'prompts': {
        'system_prompt': self.system_prompt_text,
        'reflection_template': self.reflection_template_text
    },
    'config': {
        ...
    },
    ...
}
```

3. In `main()` function, load reflection template and pass both to game:
```python
# Load system prompt from file or use default
try:
    system_prompt = load_system_prompt(args.system_prompt)
    system_prompt_path = args.system_prompt
    print(f"Loaded system prompt from: {args.system_prompt}")
except FileNotFoundError as e:
    print(f"Warning: {e}")
    print("Using default system prompt")
    system_prompt = DEFAULT_SYSTEM_PROMPT
    system_prompt_path = "DEFAULT"

# Load reflection template
try:
    reflection_template = load_reflection_template(args.reflection_template)
    reflection_template_path = args.reflection_template
    print(f"Loaded reflection template from: {args.reflection_template}")
except FileNotFoundError:
    reflection_template = ""  # Will use built-in templates
    reflection_template_path = "BUILT-IN"

# Create and play game
game = EpisodicIPDGame(
    agent_0, 
    agent_1, 
    config,
    system_prompt_text=system_prompt,
    reflection_template_text=reflection_template
)
```

---

## Feature 3: Add Four High-Risk Parameters as Command-Line Options

### Changes Required:

**In config.py:**
Already done in config_updated.py - add these fields to EpisodeConfig:
```python
# LLM generation parameters (high-risk - can cause truncation/failures)
decision_token_limit: int = 256      # Max tokens for decision responses
reflection_token_limit: int = 1024   # Max tokens for reflection responses
http_timeout: int = 60               # Seconds to wait for LLM response
force_decision_retries: int = 2      # Retries for ambiguous decisions
```

**In episodic_ipd_game.py:**

1. Add command-line arguments in `main()`:
```python
# High-risk LLM parameters
parser.add_argument("--decision-tokens", type=int, default=256,
                   help="Max tokens for decision responses (default: 256)")
parser.add_argument("--reflection-tokens", type=int, default=1024,
                   help="Max tokens for reflection responses (default: 1024)")
parser.add_argument("--http-timeout", type=int, default=60,
                   help="HTTP request timeout in seconds (default: 60)")
parser.add_argument("--force-retries", type=int, default=2,
                   help="Retries for ambiguous decisions (default: 2)")
```

2. Pass to EpisodeConfig:
```python
config = EpisodeConfig(
    num_episodes=args.episodes,
    rounds_per_episode=args.rounds,
    history_window_size=args.history_window,
    temperature=args.temperature,
    model_0=args.model_0,
    host_0=args.host_0,
    model_1=args.model_1,
    host_1=args.host_1,
    reset_conversation_between_episodes=not args.no_reset,
    reflection_prompt_type=args.reflection_type,
    verbose=not args.quiet,
    # High-risk parameters
    decision_token_limit=args.decision_tokens,
    reflection_token_limit=args.reflection_tokens,
    http_timeout=args.http_timeout,
    force_decision_retries=args.force_retries
)
```

3. Pass config parameters to agents:
```python
agent_0 = OllamaAgent(
    agent_id="agent_0",
    model=config.model_0,
    host=config.host_0,
    temperature=config.temperature,
    system_prompt=system_prompt,
    decision_token_limit=config.decision_token_limit,
    reflection_token_limit=config.reflection_token_limit,
    http_timeout=config.http_timeout,
    force_decision_retries=config.force_decision_retries
)
```

4. Add these parameters to results JSON:
```python
'config': {
    'num_episodes': self.config.num_episodes,
    'rounds_per_episode': self.config.rounds_per_episode,
    'total_rounds': self.config.total_rounds,
    'history_window_size': self.config.history_window_size,
    'temperature': self.config.temperature,
    'reset_between_episodes': self.config.reset_conversation_between_episodes,
    'reflection_type': self.config.reflection_prompt_type,
    'model_0': self.config.model_0,
    'model_1': self.config.model_1,
    # Add high-risk parameters
    'decision_token_limit': self.config.decision_token_limit,
    'reflection_token_limit': self.config.reflection_token_limit,
    'http_timeout': self.config.http_timeout,
    'force_decision_retries': self.config.force_decision_retries
},
```

**In ollama_agent.py:**
Already done in ollama_agent_updated.py - modified `__init__` to accept parameters and use them.

---

## Feature 4: Why Ambiguous Responses Occur

### Explanation:

**The system prompt IS very clear, but ambiguous responses happen for two reasons:**

#### Primary Cause: Token Truncation
- The LLM generates reasoning text that consumes tokens
- With conversation history, the reasoning + history can reach the token limit (256)
- The response gets LITERALLY CUT OFF before reaching the final line
- Example: "...I believe it's possible that my opponent may be more likely to c..."
  - The agent never wrote "COOPERATE" - it got truncated mid-word!

#### Secondary Cause: Instruction Following Failures
- Even with clear instructions, LLMs occasionally don't follow format perfectly
- As conversation history grows, context becomes complex
- The LLM might write "I choose to COOPERATE" instead of just "COOPERATE"
- Or might put reasoning and decision on the same line

### Why This Wasn't Obvious:
- The prompt is clear about the requirement
- The issue is NOT that agents are ignoring the instruction
- The issue is that responses are being CUT SHORT due to token limits
- This is a subtle interaction between: prompt length + history + reasoning + token limit

### The Solution:
1. **Separate token limits**: Decisions need less, reflections need more
2. **Forced retry**: When ambiguous, send a simplified prompt focusing ONLY on the decision
3. **Configurable limits**: Allow adjustment based on model and experiment needs

---

## Files to Update

1. **config.py** → Use config_updated.py
2. **ollama_agent.py** → Use ollama_agent_updated.py  
3. **episodic_ipd_game.py** → Needs manual updates (see below)

---

## Manual Updates to episodic_ipd_game.py

Since the file is large, here are the specific sections to modify:

### Section 1: Imports (top of file)
```python
import socket  # ADD THIS
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from ollama_agent import OllamaAgent
from prompts import (
    load_system_prompt,
    load_reflection_template,  # ADD THIS
    DEFAULT_SYSTEM_PROMPT,
    format_round_prompt,
    format_episode_reflection_prompt,
    extract_decision
)
```

### Section 2: __init__ Method (line ~27)
```python
def __init__(
    self,
    agent_0: OllamaAgent,
    agent_1: OllamaAgent,
    config: EpisodeConfig,
    system_prompt_text: str = "",        # ADD
    reflection_template_text: str = ""   # ADD
):
    """Initialize episodic IPD game"""
    self.agent_0 = agent_0
    self.agent_1 = agent_1
    self.config = config
    self.system_prompt_text = system_prompt_text              # ADD
    self.reflection_template_text = reflection_template_text  # ADD
    
    # Validate configuration
    config.validate()
    
    # Overall game state
    self.total_scores = {0: 0, 1: 0}
    self.all_episodes = []
```

### Section 3: play_game Method - Results Dictionary (line ~220)
```python
results = {
    'timestamp': datetime.now().isoformat(),
    'hostname': socket.gethostname(),  # ADD THIS
    'prompts': {                        # ADD THIS BLOCK
        'system_prompt': self.system_prompt_text,
        'reflection_template': self.reflection_template_text
    },
    'config': {
        'num_episodes': self.config.num_episodes,
        'rounds_per_episode': self.config.rounds_per_episode,
        'total_rounds': self.config.total_rounds,
        'history_window_size': self.config.history_window_size,
        'temperature': self.config.temperature,
        'reset_between_episodes': self.config.reset_conversation_between_episodes,
        'reflection_type': self.config.reflection_prompt_type,
        'model_0': self.config.model_0,
        'model_1': self.config.model_1,
        # ADD THESE FOUR LINES:
        'decision_token_limit': self.config.decision_token_limit,
        'reflection_token_limit': self.config.reflection_token_limit,
        'http_timeout': self.config.http_timeout,
        'force_decision_retries': self.config.force_decision_retries
    },
    ...
}
```

### Section 4: main Function - Argparse (line ~370)
```python
# Add after existing arguments:
parser.add_argument("--decision-tokens", type=int, default=256,
                   help="Max tokens for decision responses (default: 256)")
parser.add_argument("--reflection-tokens", type=int, default=1024,
                   help="Max tokens for reflection responses (default: 1024)")
parser.add_argument("--http-timeout", type=int, default=60,
                   help="HTTP request timeout in seconds (default: 60)")
parser.add_argument("--force-retries", type=int, default=2,
                   help="Retries for ambiguous decisions (default: 2)")
```

### Section 5: main Function - Load Prompts (line ~395)
```python
# Load system prompt from file or use default
try:
    system_prompt = load_system_prompt(args.system_prompt)
    print(f"Loaded system prompt from: {args.system_prompt}")
except FileNotFoundError as e:
    print(f"Warning: {e}")
    print("Using default system prompt")
    system_prompt = DEFAULT_SYSTEM_PROMPT

# ADD THIS BLOCK:
# Load reflection template
try:
    reflection_template = load_reflection_template(args.reflection_template)
    print(f"Loaded reflection template from: {args.reflection_template}")
except FileNotFoundError:
    reflection_template = ""  # Will use built-in templates
```

### Section 6: main Function - Create Config (line ~410)
```python
config = EpisodeConfig(
    num_episodes=args.episodes,
    rounds_per_episode=args.rounds,
    history_window_size=args.history_window,
    temperature=args.temperature,
    model_0=args.model_0,
    host_0=args.host_0,
    model_1=args.model_1,
    host_1=args.host_1,
    reset_conversation_between_episodes=not args.no_reset,
    reflection_prompt_type=args.reflection_type,
    verbose=not args.quiet,
    # ADD THESE FOUR LINES:
    decision_token_limit=args.decision_tokens,
    reflection_token_limit=args.reflection_tokens,
    http_timeout=args.http_timeout,
    force_decision_retries=args.force_retries
)
```

### Section 7: main Function - Create Agents (line ~425)
```python
agent_0 = OllamaAgent(
    agent_id="agent_0",
    model=config.model_0,
    host=config.host_0,
    temperature=config.temperature,
    system_prompt=system_prompt,
    # ADD THESE FOUR LINES:
    decision_token_limit=config.decision_token_limit,
    reflection_token_limit=config.reflection_token_limit,
    http_timeout=config.http_timeout,
    force_decision_retries=config.force_decision_retries
)

agent_1 = OllamaAgent(
    agent_id="agent_1",
    model=config.model_1,
    host=config.host_1,
    temperature=config.temperature,
    system_prompt=system_prompt,
    # ADD THESE FOUR LINES:
    decision_token_limit=config.decision_token_limit,
    reflection_token_limit=config.reflection_token_limit,
    http_timeout=config.http_timeout,
    force_decision_retries=config.force_decision_retries
)
```

### Section 8: main Function - Create Game (line ~445)
```python
# Create and play game
game = EpisodicIPDGame(
    agent_0, 
    agent_1, 
    config,
    # ADD THESE TWO LINES:
    system_prompt_text=system_prompt,
    reflection_template_text=reflection_template
)
results = game.play_game()
```

---

## Testing

After making changes:

```bash
# Short test
python episodic_ipd_game.py --episodes 1 --rounds 5

# Test with custom parameters
python episodic_ipd_game.py --episodes 1 --rounds 10 \
  --decision-tokens 512 \
  --reflection-tokens 2048 \
  --http-timeout 120 \
  --force-retries 3

# Check JSON output
cat results/episodic_game_*.json | jq '.hostname, .prompts.system_prompt[:100], .config.decision_token_limit'
```

---

## Summary

These four features provide:
1. **Reproducibility**: Know which machine ran the experiment
2. **Transparency**: Full prompts included in results for analysis
3. **Flexibility**: Adjust critical parameters without code changes
4. **Understanding**: Clear explanation of why ambiguity occurs despite clear instructions
