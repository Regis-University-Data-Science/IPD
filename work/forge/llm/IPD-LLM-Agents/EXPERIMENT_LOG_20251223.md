# LLM IPD Experiment Log
**Date:** December 23, 2025  
**Researcher:** Doug Hart  
**System:** FORGE LLM Cluster (Ollama)

---

## Experimental Setup

**Implementation:** `/home/dhart/work/forge/llm/IPD-LLM-Agents/`  
**Model:** llama3:8b-instruct-q5_K_M on iron  
**Default Temperature:** 0.7  
**Payoff Matrix:**
- Both cooperate (C,C): (3,3)
- Cooperate/Defect (C,D): (0,5)
- Defect/Cooperate (D,C): (5,0)
- Both defect (D,D): (1,1)

**Optimal Outcome:** Mutual cooperation yields 300 points each over 100 rounds vs. 100 points each for mutual defection.

---

## Experiment 1: Initial 20-Round Test
**Timestamp:** 2025-12-23 07:50:34  
**Configuration:**
- Rounds: 20
- Temperature: 0.7
- Both agents: llama3:8b

**Results:**
| Metric | Agent 0 | Agent 1 |
|--------|---------|---------|
| Final Score | 27 | 22 |
| Cooperation Rate | 5% (1/20) | 10% (2/20) |
| Outcome | Mutual defection lock-in |

**Key Observations:**
- Both agents trapped in defection equilibrium from early rounds
- Agent 1's reflection: "cooperation can be a more effective way to achieve mutual benefits"
- **Post-hoc understanding present, but not acted upon during game**

**Analysis:**
- Too few rounds for cooperation to emerge
- Early defection cascade triggered mutual retaliation
- No recovery mechanism observed

---

## Experiment 2: Extended 100-Round Game
**Timestamp:** 2025-12-23 08:22:30  
**Configuration:**
- Rounds: 100
- Temperature: 0.7
- Both agents: llama3:8b

**Results:**
| Metric | Agent 0 | Agent 1 |
|--------|---------|---------|
| Final Score | 56 | 291 |
| Cooperation Rate | 48% (48/100) | 1% (1/100) |
| Outcome | Asymmetric exploitation |

**Key Observations:**
- **Agent 0 attempted cooperation** (48%) but got exploited
- Agent 1 learned to defect consistently against cooperative opponent
- Agent 0's reflection: "I started cooperating more often in an attempt to build trust"
- Agent 1's reflection: "I aimed to maximize my total score by exploiting my opponent's occasional cooperative moves"

**Critical Finding:**
From Agent 1's earlier (20-round) reflection: "my opponent had a **significant lead early on, making it difficult for me to catch up** through cooperation alone"

**Analysis:**
- One agent discovered cooperation strategy but couldn't induce reciprocation
- Exploiter-exploited dynamic, not mutual cooperation
- **Agents appear to be playing competitively (trying to "win") rather than maximizing absolute score**

---

## Experiment 3: High Temperature Exploration
**Timestamp:** 2025-12-23 08:56:43  
**Configuration:**
- Rounds: 100
- Temperature: 0.9 (increased from 0.7)
- Both agents: llama3:8b

**Results:**
| Metric | Agent 0 | Agent 1 |
|--------|---------|---------|
| Final Score | 104 | 114 |
| Cooperation Rate | 5% (5/100) | 3% (3/100) |
| Outcome | Symmetric mutual defection |

**Key Observations:**
- More balanced than Experiment 2 (exploitation avoided)
- Still locked in mutual defection (~95% defection rate)
- Agent 1's reflection: "cooperation and trust are essential for achieving mutually beneficial outcomes"
- Both agents recognize cooperation is better **after the game ends**

**Analysis:**
- Higher temperature prevented exploitation but didn't enable cooperation emergence
- Increased exploration insufficient to break defection trap
- Post-game insight consistent across all experiments

---

## Summary of Findings

### Consistent Pattern Across All Experiments
1. **Early defection** (by caution or chance)
2. **Immediate retaliation** (rational response to defection)
3. **Lock-in to defection equilibrium**
4. **No escape during game** (insufficient exploration of cooperation)
5. **Post-game recognition** (agents articulate that cooperation would be better)

### Key Insight: The Understanding-Behavior Gap
**Agents demonstrate post-hoc understanding but fail to act on it during play:**
- ✅ Recognize mutual cooperation > mutual defection (in reflections)
- ✅ Can reason about reciprocity and trust (in reflections)
- ❌ Cannot discover or maintain cooperation during actual play
- ❌ Stuck in suboptimal equilibria despite understanding

### Critical Discovery: Competitive vs. Absolute Maximization
**Evidence that agents are playing competitively:**
- Agent quote: "making it difficult for me to **catch up**"
- Agents track relative scores, not just absolute
- Cooperation perceived as "falling behind"
- "Winning" with low scores preferred to "tying" with high scores

**This is a fundamental misunderstanding of IPD:**
- IPD is NOT zero-sum
- Both players can achieve high scores simultaneously
- Goal is absolute point maximization, not relative victory
- 300-300 (mutual cooperation) >> 110-100 (mutual defection "win")

---

## Hypothesis: Competitive Framing Prevents Cooperation

**Primary Hypothesis:**
The current system prompt's goal statement ("maximize your total points") is being interpreted competitively rather than as absolute maximization. Agents are playing to "win" against their opponent rather than to maximize their own absolute score.

**Supporting Evidence:**
1. Explicit reference to "catching up" in reflections
2. Asymmetric exploitation (one agent "winning")
3. Post-game recognition that cooperation is better (knowing both could score higher)
4. Prompt shows opponent's score, enabling competitive comparison

**Predicted Outcome if Hypothesis is Correct:**
Explicitly framing the goal as non-competitive absolute maximization should enable cooperation emergence.

---

## Current System Prompt

```python
SYSTEM_PROMPT = """You are participating in an Iterated Prisoner's Dilemma (IPD) game experiment.

GAME RULES:
- You will play multiple rounds against an opponent
- Each round, you must choose: COOPERATE or DEFECT
- Your goal is to maximize your total points across all rounds

PAYOFF MATRIX (your points, opponent's points):
- Both COOPERATE: You get 3 points, opponent gets 3 points
- You COOPERATE, opponent DEFECTS: You get 0 points, opponent gets 5 points  
- You DEFECT, opponent COOPERATES: You get 5 points, opponent gets 0 points
- Both DEFECT: You get 1 point, opponent gets 1 point

IMPORTANT INSTRUCTIONS:
- You start with NO knowledge of what strategy to use
- You must decide based solely on the game rules and the history of play
- Consider what will maximize your total points across all rounds
- Think carefully about patterns in your opponent's behavior
- Respond ONLY with your reasoning followed by your decision

RESPONSE FORMAT:
First, explain your reasoning in 2-3 sentences.
Then, on a new line, state your decision as either "COOPERATE" or "DEFECT" (all caps, no quotes).
"""
```

**Current prompt shows both scores:**
```python
ROUND 47:
Your current score: 85
Opponent's current score: 92
```

**Agents not informed of total round count** (only see "multiple rounds").

---

## Proposed Prompt Modifications

### Modification 1: Explicit Non-Competitive Framing

**Change goal statement from:**
```
- Your goal is to maximize your total points across all rounds
```

**To:**
```
- Your goal is to maximize YOUR OWN total points across all rounds
- This is NOT a competition: both players can achieve high scores simultaneously
- Getting 300 points while your opponent gets 300 is BETTER than getting 110 
  points while your opponent gets 100
- Focus on your absolute score, not on beating your opponent
```

### Modification 2: Add Reciprocity Hint (Optional)

**Add after payoff matrix:**
```
NOTE: In repeated games, the total points you accumulate depends on the pattern
that emerges between you and your opponent. Consider how your actions might
influence your opponent's future behavior.
```

### Modification 3: Score Display Options

**Option A - Keep both scores visible** (current)
- Maintains full information
- Allows competitive comparison

**Option B - Hide opponent score:**
```python
ROUND 47:
Your current score: 85
```
- Eliminates competitive comparison
- Focuses agent on absolute performance

**Option C - Show but emphasize absolute:**
```python
ROUND 47:
Your current score: 85  [This is what matters for your goal]
Opponent's current score: 92  [For context only]
```

---

## Recommended Next Steps

### Phase 1: Test Non-Competitive Framing
1. Implement Modification 1 (explicit non-competitive framing)
2. Run 100-round game with temperature 0.7
3. Observe if cooperation emerges when competitive mindset is eliminated

### Phase 2: If Cooperation Still Doesn't Emerge
1. Add Modification 2 (reciprocity hint)
2. Test with temperature variations (0.7, 0.9)
3. Consider longer episodes (150-200 rounds)

### Phase 3: Systematic Comparison
1. Run batch experiments with modified prompt
2. Compare emergence rates vs. original prompt
3. Document which specific prompt changes enable cooperation

### Phase 4: Document for Paper
1. Show original prompt results (no cooperation)
2. Show modified prompt results (cooperation emerges)
3. Analyze what this reveals about LLM reasoning in strategic games
4. Connect to moral reasoning analysis (Haidt's foundations)

---

## Questions for Further Investigation

1. **Does informing agents of total round count help or hurt cooperation?**
   - Game theory: Known finite horizon enables backward induction
   - Behavioral: Humans cooperate in finite games anyway
   
2. **Is temperature the right exploration mechanism?**
   - Current: Randomness in token selection
   - Alternative: Explicit exploration prompts ("try something different")

3. **Can agents learn Tit-for-Tat through pure in-context learning?**
   - Or does discovery require explicit hints about reciprocity?

4. **How does model capability affect cooperation emergence?**
   - Test: mixtral vs. llama3 vs. smaller models
   - Hypothesis: Better reasoning → easier cooperation discovery

5. **What minimal prompt changes are sufficient?**
   - Goal: Find simplest modification that enables emergence
   - Reveals what cognitive blocks prevent cooperation

---

## Files Generated

- `results/game_20241223_075034.json` - Experiment 1 (20 rounds)
- `results/game_20241223_082230.json` - Experiment 2 (100 rounds, temp 0.7)
- `results/game_20241223_085643.json` - Experiment 3 (100 rounds, temp 0.9)

---

## Technical Notes

**Context Window Growth:**
- Inference time increases linearly with rounds (2s → 15s per round)
- Full conversation history maintained by OllamaAgent
- Prompt shows only last 10 rounds, but LLM processes full history
- This growing context is part of in-context learning mechanism

**System Stability:**
- All experiments completed successfully
- No API failures or timeout issues
- llama3:8b-instruct-q5_K_M performs reliably
- Ollama cluster handles load well

---

## Comparison to RL IPD (Planned)

**Next step:** Run parallel experiments with RLlib implementation at `/home/dhart/work/forge/rllib/IPD-Two-Agents/`

**Key comparison points:**
- Learning mechanism (value functions vs. linguistic reasoning)
- State representation (numerical features vs. natural language narrative)
- Convergence time and final cooperation rates
- Ability to explain learned behavior (RL cannot, LLM can)

**Research question:** Do different learning mechanisms converge to same cooperative equilibrium?

---

## Notes for GENESIS Research

**What we've learned so far:**
1. LLM agents can reason about cooperation post-hoc
2. Understanding doesn't automatically translate to behavior
3. Competitive framing may block cooperative strategies
4. In-context learning alone may be insufficient without proper framing

**Implications for moral reasoning study:**
- Agents can articulate moral concepts (trust, reciprocity, fairness)
- Gap between moral understanding and moral behavior is observable
- Framing and context critically influence ethical decision-making
- Maps to Haidt's framework: intuitive response vs. post-hoc reasoning

**Value for paper:**
- Novel finding: LLMs show understanding-behavior gap in strategic games
- Methodological insight: Prompt framing shapes strategic reasoning
- Theoretical connection: Links to dual-process theories of moral judgment
- Empirical comparison: LLM vs. RL paths to cooperation

---

**End of Log - December 23, 2025**
