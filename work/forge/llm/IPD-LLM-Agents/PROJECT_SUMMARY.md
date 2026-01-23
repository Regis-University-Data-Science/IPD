# LLM IPD Implementation - Project Summary

## What We Built

A complete system for studying emergent cooperation in LLM agents playing Iterated Prisoner's Dilemma, designed to complement your existing RLlib IPD implementation.

## Directory Structure

```
/home/dhart/work/forge/llm/IPD-LLM-Agents/
├── README.md                 # Full documentation
├── QUICKSTART.md            # Quick start guide
├── requirements.txt         # Python dependencies
├── ollama_agent.py          # Ollama API wrapper
├── prompts.py               # System prompts and parsing
├── ipd_llm_game.py          # Main game orchestration
├── analyze_results.py       # Analysis and visualization
├── test_connection.py       # Connectivity testing
├── run_batch.py            # Batch experiment runner
└── results/                # Output directory (created at runtime)
```

## Core Components

### 1. OllamaAgent (`ollama_agent.py`)
- Wraps Ollama API for LLM inference
- Maintains conversation history (in-context learning)
- Handles retries and error recovery
- Configurable temperature for exploration

### 2. Prompts (`prompts.py`)
- System prompt explaining IPD rules with no pre-programmed strategy
- History formatting (shows last 10 rounds)
- Decision extraction from LLM responses
- Post-game reflection prompts

### 3. Game Engine (`ipd_llm_game.py`)
- Orchestrates two-agent IPD game
- Logs all decisions and reasoning
- Calculates payoffs and maintains scores
- Saves complete game history to JSON

### 4. Analysis Tools (`analyze_results.py`)
- Summary statistics (scores, cooperation rates)
- Strategy transitions (early/middle/late phases)
- Sample reasoning extraction
- Visualization (cooperation and score plots)

### 5. Testing (`test_connection.py`)
- Verifies Ollama connectivity
- Tests decision extraction logic
- Validates basic agent functionality

### 6. Batch Processing (`run_batch.py`)
- Runs multiple experiments automatically
- Varies configurations (models, temperature)
- Generates summary reports

## Key Design Decisions

### Theoretical Foundation
- **MDP formulation**: State includes agent's view of interaction history
- **In-context learning**: LLMs "learn" through reasoning about conversation history
- **Naive initialization**: No pre-programmed strategies, just game rules

### Practical Choices
- **Default model**: llama3:8b on iron (good reasoning, accessible)
- **Episode length**: 100 rounds (enough for emergence, manageable context)
- **Temperature**: 0.7 (balanced exploration/exploitation)
- **History window**: Last 10 rounds visible in prompts
- **Output format**: JSON with full round details and reasoning

## How It Works

### Game Flow
1. Initialize two OllamaAgent instances with system prompt
2. For each round:
   - Format prompt with history and current scores
   - Get decision + reasoning from each agent
   - Calculate payoffs based on joint action
   - Update scores and conversation histories
3. After game:
   - Request reflections from both agents
   - Save complete results to JSON

### Learning Mechanism
- Agents don't update weights (no traditional "learning")
- Instead: reason about accumulated history in context window
- Should discover cooperation yields higher cumulative rewards
- Articulate this understanding in natural language

## Expected Outcomes

### Success Pattern
```
Rounds 1-30:   Mixed behavior, exploring strategies
Rounds 31-70:  Cooperation increasing as pattern emerges
Rounds 71-100: Stable mutual cooperation (>80%)
```

### Agent Explanations
Should reference:
- "Cooperation yields more points over time"
- "Opponent reciprocates cooperation"
- "Mutual cooperation is optimal strategy"

## Comparison to RL IPD

| Aspect | Your RL Implementation | This LLM Implementation |
|--------|------------------------|-------------------------|
| Location | `/work/forge/rllib/IPD-Two-Agents/` | `/work/forge/llm/IPD-LLM-Agents/` |
| Learning | PPO with value functions | In-context reasoning |
| State | Numerical feature vector | Natural language narrative |
| Training | Hours on GPU cluster | Immediate (no training) |
| Explanation | Not available | Built-in via language |
| Infrastructure | Ray RLlib cluster | Ollama LLM cluster |

## Next Steps for Research

### Phase 1: Validation (Now)
1. Run `test_connection.py` to verify setup
2. Execute single game: `python ipd_llm_game.py --rounds 100`
3. Analyze results to confirm emergence

### Phase 2: Baseline Data
1. Run multiple trials: `python run_batch.py --batch`
2. Document cooperation emergence patterns
3. Collect agent explanations for analysis

### Phase 3: Comparative Analysis
1. Run RL experiments from `/work/forge/rllib/IPD-Two-Agents/`
2. Compare learning curves (RL vs LLM)
3. Document differences in convergence

### Phase 4: Moral Reasoning
1. Extract language patterns from LLM reflections
2. Map to Haidt's moral foundations
3. Show emergent behavior + moral explanation

### Phase 5: Paper (Ignition AI)
1. Present both RL and LLM approaches
2. Show cooperation emerges from different mechanisms
3. Demonstrate LLMs can explain learned cooperation
4. Connect to moral foundations theory

## Integration with GENESIS

This LLM IPD implementation is Track 2 of your GENESIS research:

**Track 1 (RL baseline)**: 
- Already exists in `/work/forge/rllib/IPD-Two-Agents/`
- Standard MDP formulation
- Learn through value functions

**Track 2 (LLM agents)**: 
- This implementation
- Same game, different learning mechanism
- Can explain reasoning

**Research Question**: Can linguistic reasoning about narrative history produce the same emergent cooperation as numerical optimization over compact features?

**Novel Contribution**: Showing that LLMs bridge learned behavior and moral reasoning - they both discover cooperation AND explain it.

## Resources Available

Your infrastructure supports this perfectly:
- **LLM cluster**: 5 machines with Ollama services
- **Models**: llama3, mixtral, mistral, phi3, codellama
- **Management**: Unified scripts in `/work/forge/llm/`
- **Compute**: Can run many experiments in parallel

## Documentation

- **README.md**: Complete technical documentation
- **QUICKSTART.md**: Step-by-step usage guide
- **This file**: Project overview and research context

All documentation is in `/home/dhart/work/forge/llm/IPD-LLM-Agents/`

## Status

✅ Complete and ready to run
✅ Tested design pattern
✅ Integrated with your FORGE infrastructure
✅ Documented for research use

Ready for experimental validation!
