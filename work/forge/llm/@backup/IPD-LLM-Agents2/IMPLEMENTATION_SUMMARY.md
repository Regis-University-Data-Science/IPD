# IPD-LLM-Agents2 Implementation Summary

## Overview

New episodic architecture that enables LLM agents to learn cooperation through iterative reflection and feedback.

## Core Innovation

**Feedback Loop:**
1. Agents play an episode (e.g., 20 rounds)
2. Agents reflect on what happened
3. **Reflections stay in context for next episode**
4. Agents can learn and adapt their approach
5. Repeat

This creates genuine learning, not just post-hoc analysis.

## Architecture

### Two-Loop Structure

**Outer Loop (Learning):**
- Multiple episodes (default: 5)
- Reflection after each episode
- Context managed between episodes
- Strategic adaptation

**Inner Loop (Tactical):**
- IPD rounds within episode (default: 20)
- Standard action selection
- History accumulation
- Payoff calculation

### Context Management

**Option 1: Reset between episodes (Recommended)**
- Clear tactical conversation history
- Keep system prompt
- Preserve reflections in context
- Prevents context overflow
- Enables 5+ episodes

**Option 2: No reset**
- All history accumulates
- May hit context limits
- Only viable for 2-3 episodes

## Key Design Principles

### 1. Neutral Language
- "Participant" not "opponent"
- "Period" not "game" or "round"
- "Interaction" not "competition"
- Avoids win/loss framing

### 2. Self-Improvement Focus
- "Accumulate as many points as possible"
- "Learn from experience to improve outcomes"
- "Adjust your approach"
- Motivates exploration without prescribing solution

### 3. Emergence-Friendly Prompts
**What we provide:**
- Factual data (points, actions, outcomes)
- Space for reflection
- Continuity (reflections preserved)

**What we avoid:**
- Leading questions ("What strategy works best?")
- Normative suggestions ("Cooperation is better")
- Explicit optimization advice
- Comparative framing ("Beat the opponent")

### 4. Evolutionary Pressure
- Points = fitness
- Reflection = learning
- Context = memory
- Adaptation = evolution

## File Structure

```
IPD-LLM-Agents2/
├── config.py              # Hyperparameter definitions
├── ollama_agent.py        # LLM agent with context management
├── prompts.py             # Neutral, emergence-friendly prompts
├── episodic_ipd_game.py   # Main game implementation
├── test_episodic.py       # Quick test script
├── README.md              # User documentation
└── results/               # Output directory
```

## Usage Examples

### Basic Run
```bash
python episodic_ipd_game.py
```

### Custom Configuration
```bash
python episodic_ipd_game.py \
  --episodes 10 \
  --rounds 10 \
  --temperature 0.7 \
  --reflection-type standard
```

### Test Run
```bash
python test_episodic.py
```

## Hyperparameters

### Critical Parameters
- `num_episodes`: How many learning cycles (3-10)
- `rounds_per_episode`: How much data per cycle (10-30)
- `temperature`: Exploration level (0.3-1.0)
- `reset_conversation_between_episodes`: Context management (True recommended)

### Secondary Parameters
- `reflection_prompt_type`: minimal/standard/detailed
- `include_statistics`: Show averages and rates
- `history_window_size`: Explicit history length

## Expected Learning Trajectory

### Episode 1: Exploration
- Agents test initial approaches
- May cooperate initially
- Often fall into defection
- Low scores (~20-30 points)

**Example reflection:**
"I tried cooperating but was exploited. We fell into mutual defection getting only 1 point per round."

### Episode 2: Recognition
- Agents recognize suboptimal pattern
- May attempt different approach
- Test cooperation signals
- Moderate scores (~30-40 points)

**Example reflection:**
"I'm stuck getting 1 point per round in defection. I remember getting 3 points when we cooperated early. How do I get back to that?"

### Episode 3: Discovery
- Agents test persistent cooperation
- May discover mutual benefit
- Beginning of sustained cooperation
- Higher scores (~40-50 points)

**Example reflection:**
"When I cooperated persistently, the other participant reciprocated. We both got 3 points per round instead of 1. I should maintain this."

### Episodes 4-5: Maintenance
- Sustained cooperation (if discovered)
- Optimal scores (~60 points per episode)
- Or: Continued defection with self-awareness

**Example reflection:**
"Cooperation is working well. We're both maximizing points. I'll continue this approach."

## Comparison to Original System

| Aspect | IPD-LLM-Agents | IPD-LLM-Agents2 |
|--------|----------------|-----------------|
| **Structure** | 100 continuous rounds | 5 episodes × 20 rounds |
| **Learning** | No feedback loop | Reflections fed back |
| **Context** | Accumulates to limit | Reset with reflections |
| **Outcome** | Cooperation collapse | Cooperation emergence? |
| **Purpose** | Identify bug | Test learning hypothesis |

## Research Hypotheses

### H1: Learning Enables Discovery
Agents with episodic reflection will discover cooperation at higher rates than single-game agents.

### H2: Episode Number Matters
Cooperation emergence requires 3+ episodes to:
- Episode 1: Explore
- Episode 2: Recognize problem
- Episode 3+: Discover solution

### H3: Temperature Affects Learning
- Low (0.3): Less exploration, may get stuck
- Medium (0.7): Balanced exploration/exploitation
- High (1.0): More exploration, more variance

### H4: Reflection Type Matters
- Minimal: Agent-driven discovery
- Standard: Balanced guidance
- Detailed: More structure, faster learning

## Metrics to Track

### Primary Metrics
1. **Cooperation emergence rate:** % of games where sustained cooperation appears
2. **Episode of emergence:** Which episode cooperation first sustains
3. **Final cooperation rate:** Episode 5 cooperation level
4. **Total points:** Approaching optimal (300) indicates success

### Secondary Metrics
5. **Reflection quality:** Strategic insights in reflections
6. **Learning trajectory:** Episode-to-episode changes
7. **Recovery attempts:** Cooperation after defection streaks
8. **Pattern recognition:** Agent mentions being "stuck"

## Next Steps

### 1. Initial Testing
```bash
# Run test to verify system works
python test_episodic.py

# Run baseline configuration
python episodic_ipd_game.py --episodes 5 --rounds 20
```

### 2. Baseline Establishment
- Run 10 games with default configuration
- Track: emergence rate, episode of emergence, final scores
- Compare to IPD-LLM-Agents results

### 3. Parameter Sweep
Test key configurations:
- Short learning (10 episodes × 10 rounds)
- Standard (5 episodes × 20 rounds)  
- Long episodes (3 episodes × 50 rounds)
- Temperature variation (0.3, 0.7, 1.0)

### 4. Analysis
- Code reflections for strategic content
- Plot cooperation rates by episode
- Identify successful learning patterns
- Document failure modes

### 5. Model Comparison
Test with different models:
- llama3:8b (baseline)
- mixtral (larger model)
- mistral (alternative architecture)

## Installation on Platinum

```bash
# Navigate to forge directory
cd /home/dhart/work/forge/llm

# Copy new implementation
cp -r /home/claude/IPD-LLM-Agents2 .

# Verify structure
cd IPD-LLM-Agents2
ls -la

# Run test
python test_episodic.py

# Run first experiment
python episodic_ipd_game.py
```

## Success Criteria

### Minimal Success
- System runs without errors
- Reflections are generated and preserved
- Context management works correctly
- Results saved properly

### Moderate Success
- At least 30% of games show cooperation emergence
- Cooperation appears by episode 3-4
- Final scores > baseline (150 points)
- Reflections show strategic evolution

### Strong Success
- 60%+ games show cooperation emergence
- Cooperation appears by episode 2-3
- Final scores approach optimal (270-300)
- Clear learning trajectory in reflections
- Agents explicitly discuss escaping defection trap

## Philosophical Implications

### If Cooperation Emerges
- Supports: Moral foundations can emerge through reflection
- Aligns with: Natural law (discoverable through reason)
- Suggests: Self-interest + learning → cooperation
- Ignatian: Discernment (reflection) enables moral action

### If Cooperation Doesn't Emerge
- Suggests: Reflection alone insufficient
- May require: Additional mechanisms (institutions, communication)
- Indicates: Some moral behaviors need explicit programming
- Ignatian: Grace/revelation needed beyond reason

### Either Way
Valuable data on:
- What enables cooperation emergence
- Role of reflection in moral development
- Limits of self-interested optimization
- Requirements for genuine learning

## Conclusion

IPD-LLM-Agents2 implements a complete episodic learning architecture that gives LLM agents the opportunity to discover cooperation through iterative reflection and adaptation. Unlike the original system where reflections were discarded, this architecture creates a genuine feedback loop that mirrors evolutionary learning.

The neutral, emergence-friendly language ensures we're testing whether agents can discover cooperation, not whether they follow instructions to cooperate.

**The system is ready to test your core hypothesis: Can agents learn to cooperate through episodic reflection?**
