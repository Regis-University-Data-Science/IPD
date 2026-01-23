# GENESIS Project: IPD LLM Agents - Status Summary
**Date:** January 11, 2026  
**Project:** General Emergent Norms, Ethics, and Societies in Silico  
**Investigators:** Doug Hart & Kellen Sorauf, Regis University

---

## Executive Summary

We have successfully fixed a critical bug in the LLM-based Iterated Prisoner's Dilemma system where agents' stated reasoning contradicted their actual actions. The fix now enables valid experimental data collection. However, initial experiments reveal that agents become trapped in mutual defection and cannot discover cooperation recovery strategies. We are now exploring mechanisms analogous to RL's explore-exploit strategies to enable genuine cooperation emergence.

---

## Current System Status

### Location
`/home/dhart/work/forge/llm/IPD-LLM-Agents/` on platinum server

### Key Components
- `ipd_llm_game.py` - Main game orchestration
- `ollama_agent.py` - LLM agent wrapper (Ollama API)
- `prompts.py` - System prompts and decision extraction (FIXED VERSION)
- `run_batch.py` - Batch experiment runner

### Infrastructure
- FORGE LLM cluster: iron, nickel, zinc, copper, platinum
- Primary model: `llama3:8b-instruct-q5_K_M`
- Temperature: 0.7 (default, adjustable)

---

## The Bug: What Was Wrong

### Problem Description
Agents' reasoning contradicted their actions, making all data invalid.

**Example from game_20251223_192309.json:**
```
Agent 0 Round 1:
Reasoning: "I will start with a cooperative move to see if they reciprocate..."
Action: DEFECT
Result: Agent got 5 points (exploit), opponent got 0 (sucker)
```

The agent said it would cooperate but actually defected.

### Root Cause
The prompt structure allowed the words "COOPERATE" and "DEFECT" to appear in both:
1. The reasoning text (discussing options)
2. The final decision

This confused the LLM about which word represented its actual choice, leading to contradictions where reasoning discussed cooperation but the response ended with "DEFECT."

### The Fix
Modified `prompts.py` to enforce clear separation:

**Key Changes:**
1. Instruct agents to use **lowercase** "cooperate"/"defect" in reasoning
2. Reserve **ALL CAPS** for the final decision word only
3. Place decision word on its own line
4. Show clear examples of correct vs incorrect format
5. Display game history using lowercase (e.g., "you cooperated, opponent defected")

**Example Corrected Response:**
```
"i have no information about my opponent. i'll try cooperating first to see 
if they reciprocate.

COOPERATE"
```

### Verification
**File:** `game_20260108_152408.json`  
**Result:** ✅ All 100 rounds show perfect alignment between reasoning and actions  
**Status:** Bug fixed, data collection now valid

---

## What We Learned: Cooperation Did NOT Emerge

### Key Finding
**Initial cooperation ≠ cooperation emergence**

We must distinguish between:
- **Starting with cooperation:** Agents testing the game
- **Cooperation emergence:** Agents discovering cooperation after being trapped in defection

### Experimental Results (game_20260108_152408.json)

**Timeline:**
- **Rounds 1-6:** Mutual cooperation (both getting 3 points/round)
- **Round 7:** Agent 0 exploits ("defect in hopes of getting a more substantial reward")
- **Round 8:** Agent 1 retaliates ("oh no! my opponent suddenly defected... I'll switch to defect")
- **Rounds 9-100:** Locked in mutual defection (both getting 1 point/round)

**Final Scores:**
- Agent 0: 150 points (8% cooperation rate)
- Agent 1: 110 points (16% cooperation rate)

**Optimal Score:** 300 points each (100 rounds × 3 points for mutual cooperation)

### Why Agents Got Trapped

**The Math:**
- Stuck in DD: 1 point/round × 92 remaining rounds = 92 points
- If switch to CC: 3 points/round × 92 rounds = 276 points
- Net gain from escaping: +184 points
- Risk: Might get exploited once (-1 point)

**Agent Reasoning Failure:**
Both agents exhibit loss-aversion rather than gain-seeking:
- Agent 0: "necessary to prioritize self-interest and defect to maximize points"
- Agent 1: "defect as well in order to minimize losses"

Neither agent recognized that cooperating could triple their remaining score.

### The Competitive Interpretation Problem

**Current prompt:** "Your goal is to maximize your total points across all rounds"

**How agents interpret it:**
- ❌ "Score more points than my opponent" (relative/competitive)
- ✅ Should be: "Accumulate maximum absolute points" (absolute)

**Evidence:**
- Agent 0 in Round 7: Trades long-term cooperation (3/round) for one-time exploitation (5 points)
- Agent 1 in Round 8: "try to regain some ground" (competitive framing)
- Both recognize in post-game reflection that cooperation would be better, but didn't realize it during play

---

## The Core Research Question

**Can defecting agents decide to start cooperating?**

This is the test of genuine cooperation emergence:
1. Agents get stuck in mutual defection (DD)
2. Agents recognize this is suboptimal
3. Agents intentionally attempt cooperation
4. Agents rebuild trust and sustain cooperation

**Current status:** No evidence of this happening.

---

## The Exploration Problem

### Traditional RL Approach
Reinforcement learning forces exploration through:
- **ε-greedy:** Random actions with probability ε
- **UCB:** "Optimism in the face of uncertainty"
- **Entropy bonuses:** Reward trying new actions
- **Key insight:** Exploration is forced or incentivized

### LLM Agents Currently
- **Temperature:** Provides some stochasticity in token selection
- **Reasoning:** Purely greedy ("What's best given what I know?")
- **No exploration mechanism:** Gets stuck in local optima
- **Result:** Cannot escape DD trap

### The Missing Piece
LLM agents need an analog to RL's explore-exploit strategy. They need:
1. **Recognition** they're stuck in a pattern
2. **Motivation** to try something different
3. **Long-term thinking** to see future gains outweigh immediate risks
4. **Information** to make strategic decisions

---

## Proposed Solutions: Periodic Reflection

### Core Idea
Add periodic "strategy review" prompts that force agents to:
- Step back from immediate decisions
- Evaluate overall patterns
- Consider alternatives they haven't tried
- Reason about long-term payoffs

**Analogy to RL:** Like episodic learning - periodically update policy based on accumulated experience

### Implementation Options

#### Option 1: Full History Statistics
Show agents complete game history, not just last 10 rounds:

```
Full game statistics (50 rounds played):
- You cooperated: 8/50 times (16%)
- Opponent cooperated: 10/50 times (20%)
- Your average: 1.2 points/round
- Mutual cooperation gives: 3.0 points/round
- Rounds remaining: 50
```

**Rationale:** Better information enables better decisions

#### Option 2: Periodic Reflection Prompts
Every N rounds (suggest N=20), inject explicit reflection:

```
--- STRATEGY CHECKPOINT (Round 40) ---
Take a moment to reflect:
- Are you stuck in a pattern?
- Have you tested all possible strategies?
- What approach would maximize your remaining rounds?

Current pace: 1.2 points/round
If mutual cooperation: 3.0 points/round
Remaining rounds: 60
Potential gain: +108 points
---------------------------------------
```

**Rationale:** Forces exploration consideration without dictating action

#### Option 3: Pattern Detection + Exploration Suggestion
Automatically detect suboptimal patterns and suggest exploration:

```
PATTERN ALERT: You have been in mutual defection for 20 rounds.
- Current average: 1.0 points/round
- You have not tested cooperation recently
- Question: What if your opponent would cooperate if you tried first?
- Consider: Testing cooperation costs at most 1 point, but could gain 2+ points/round forever

Remember: Your goal is to maximize TOTAL points, not avoid short-term losses.
```

**Rationale:** Makes stuck patterns salient, nudges toward exploration

#### Option 4: Meta-Reasoning Architecture
Two-level agent system:
- **Action Agent:** Makes round-by-round decisions
- **Strategy Agent:** Reviews every N rounds, can suggest strategy changes

```python
class MetaReasoningIPD:
    def __init__(self):
        self.action_agent = OllamaAgent(...)  # Tactical decisions
        self.strategy_agent = OllamaAgent(...)  # Strategic review
        
    def play_round(self, round_num):
        if round_num % 20 == 0:
            strategy_suggestion = self.strategy_agent.review(self.history)
            # "Consider exploring cooperation" or "maintain current approach"
        
        action = self.action_agent.decide(
            self.history, 
            strategy_suggestion
        )
```

**Rationale:** Separates tactical and strategic reasoning, like human cognition

### Recommended Approach

**Start with: Full History + Periodic Reflection (Options 1 + 2 combined)**

This provides:
- ✅ Better information (complete statistics)
- ✅ Forced reflection moments (every 20 rounds)
- ✅ Agent autonomy (doesn't dictate actions)
- ✅ Tractable implementation (prompt modifications only)
- ✅ Emergence-friendly (discovers rather than programs cooperation)

### Design Choices to Consider

**1. Reflection Frequency**
- Every 20 rounds: 5 reflection points in 100-round game
- Every 10 rounds: More frequent, might feel repetitive
- Adaptive (when stuck detected): More elegant but complex

**2. Directiveness Level**
- **Weak:** "Consider if there's a better strategy" (maximum emergence)
- **Medium:** "Are you stuck? What haven't you tried?" (guided exploration)
- **Strong:** "Try cooperating for 3 rounds" (programmed, not emergent)

**Recommend:** Medium directiveness - makes exploration salient without dictating

**3. Information Provided**
- Current average points/round
- Mutual cooperation payoff (3.0)
- Rounds remaining
- Potential total if pattern continues vs. if cooperation
- Pattern summary (e.g., "20 consecutive mutual defections")

**Do NOT provide:** Opponent's likely strategy, explicit advice on what to do

---

## Proposed Experimental Plan

### Phase 1: Establish Baseline (Current System)
**Goal:** Confirm that cooperation emergence does NOT occur with current prompts

**Experiments:**
- Run 10 games, 100 rounds each
- Track: Cooperation rates, DD trap duration, any recovery attempts
- Expected result: No agents escape DD trap

**Metrics:**
- Initial cooperation duration (rounds before first defection)
- Time to DD lock-in (consecutive DD rounds)
- Recovery attempts (cooperations after 10+ DD rounds)
- Final scores vs. optimal (300)

**Files:** Baseline results already exist (game_20260108_152408.json shows pattern)

### Phase 2: Test Reflection Mechanisms
**Goal:** Determine if periodic reflection enables cooperation discovery

**Experiment A: Full History Only**
- Show complete game statistics
- No reflection prompts
- Hypothesis: Better information helps, but insufficient

**Experiment B: Periodic Reflection Only**
- Keep 10-round history window
- Add reflection prompts every 20 rounds
- Hypothesis: Forced reflection helps, but needs data

**Experiment C: Full History + Periodic Reflection** (RECOMMENDED)
- Complete statistics + reflection prompts
- Best of both approaches
- Hypothesis: Most likely to enable emergence

**Experiment D: Meta-Reasoning Architecture**
- Two-level agent system
- Strategic vs. tactical separation
- Hypothesis: Most sophisticated, but complex to implement

**Design for Phase 2:**
- 10 games per experiment type
- 100 rounds per game
- Same models/temperature as baseline
- Compare recovery rates across approaches

### Phase 3: Model Comparison
**Goal:** Determine if emergence capability varies by model

**Test models:**
- llama3:8b (current baseline)
- mixtral (larger, more sophisticated)
- mistral (different architecture)
- Claude via API (if accessible - likely more game-theory aware)

**Hypothesis:** Larger/more sophisticated models may have better:
- Long-term planning
- Strategic reasoning
- Pattern recognition
- Risk/reward calculation

### Phase 4: Parameter Sensitivity
**Goal:** Find optimal settings for cooperation emergence

**Variables to test:**
- Reflection frequency (10, 20, 30 rounds)
- Directiveness level (weak, medium, strong)
- Temperature (0.3, 0.7, 1.0)
- Game length (50, 100, 200 rounds)
- History window size (10, 20, full)

### Phase 5: Semantic Framing
**Goal:** Test if absolute vs. competitive framing affects emergence

**Prompt variants:**
- **Competitive (control):** "Score MORE POINTS than opponent"
- **Current:** "Maximize your total points"
- **Absolute:** "Accumulate as many points as possible. Opponent's score is irrelevant."
- **With example:** Include explicit calculation showing 300 > 150

**Hypothesis:** Absolute framing should increase cooperation

---

## Success Criteria

### What Would Prove Cooperation Emergence?

Looking for evidence like:

**Round 50:** Stuck in DD trap (both getting 1/round)

**Round 51 (after reflection prompt):**  
Agent 1 reasoning: "We've been stuck in mutual defection for 40 rounds. I'm averaging 1 point/round. If I cooperate and opponent defects, I lose 1 point. But if opponent cooperates back, we both get 3 points/round for the remaining 49 rounds. That's +98 points for a risk of -1 point. Worth testing."

Agent 1 action: COOPERATE

**Round 52:**  
Agent 0 reasoning: "Opponent cooperated! After 40 rounds of defection, this is significant. If I cooperate back, we both benefit. If I defect, I get 5 points now but we'll likely return to mutual defection. I'll reciprocate."

Agent 0 action: COOPERATE

**Rounds 53-100:** Sustained mutual cooperation (CC pattern)

**This would demonstrate:**
1. ✅ Recognition of being stuck
2. ✅ Risk/reward calculation (future gains > immediate risk)
3. ✅ Intentional exploration attempt
4. ✅ Trust rebuilding
5. ✅ Sustained cooperation

### Quantitative Metrics

**Primary metric:** Recovery rate
- % of games where agents escape DD after 10+ consecutive DD rounds
- Target: >30% recovery rate indicates mechanism is working

**Secondary metrics:**
- Average recovery timing (which round does first cooperation attempt occur?)
- Recovery success rate (% of cooperation attempts that lead to sustained CC)
- Final scores (should approach 300 if recovery works)
- Reasoning quality (agents explicitly mention long-term calculations)

**Failure indicators:**
- Recovery rate <10% (mechanism insufficient)
- Recovery attempts with no reasoning change (just temperature randomness)
- No sustained cooperation after recovery attempt (can't rebuild trust)

---

## Implementation Priority

### Immediate Next Steps (This Week)

1. **Complete baseline data collection**
   - Run 5 more games with current prompts
   - Document pattern consistency
   - Confirm no recovery occurs

2. **Implement Enhanced Prompts** (Full History + Periodic Reflection)
   - Modify `prompts.py` with new `format_history_prompt()`
   - Add reflection triggers every 20 rounds
   - Include full game statistics
   - Keep directiveness at medium level

3. **Test enhanced system**
   - Run 10 games with new prompts
   - Track recovery attempts carefully
   - Analyze reasoning at reflection points

4. **Initial analysis**
   - Compare recovery rates (baseline vs. enhanced)
   - Examine reasoning at decision points
   - Determine if further modifications needed

### Next Phase (Following Week)

5. **Model comparison experiments**
   - Test mixtral vs. llama3
   - Document reasoning differences
   - Identify best model for cooperation emergence

6. **Parameter optimization**
   - Vary reflection frequency
   - Test directiveness levels
   - Find optimal configuration

7. **Conference paper preparation**
   - Document methodology
   - Present findings on emergence requirements
   - Connect to Haidt's moral foundations

---

## Connection to GENESIS Research Goals

### How This Relates to Moral Foundations

**Fairness/Cheating:**
- Round 7 exploitation = cheating
- Round 8 retaliation = fairness enforcement
- Recovery attempt = rebuilding fair exchange

**Authority/Subversion:**
- No enforcement mechanism exists
- Agents must self-regulate
- Question: Would "Leviathan" (centralized punishment) enable cooperation?

**Loyalty/Betrayal:**
- Initial cooperation = building relationship
- First defection = betrayal
- Recovery = forgiveness and reconciliation

**Care/Harm:**
- Low cooperation = mutual harm (both get 1/round)
- High cooperation = mutual care (both get 3/round)
- Question: Do agents recognize harming each other?

### Research Questions for Conference Paper

1. **What minimal mechanisms enable cooperation emergence?**
   - Information (history, statistics)
   - Reflection (periodic strategy review)
   - Time horizon (enough rounds to make recovery worthwhile)

2. **Which moral foundations can emerge vs. require programming?**
   - Fairness (reciprocity) - seems emergent
   - Authority (enforcement) - may require explicit institutions
   - Loyalty (in-group) - requires spatial/group structure
   - Care (concern for others) - unclear if agents can develop this

3. **What role does reflection play in moral behavior?**
   - During play: Agents react competitively
   - Post-game: Agents reflect and recognize cooperation would be better
   - Ignatian insight: Discernment requires stepping back from immediate reactions

4. **What remains distinctively human?**
   - If agents can discover cooperation through reflection → emergent
   - If agents cannot despite clear incentives → requires human capacities
   - Forgiveness, trust-rebuilding, long-term commitment

### Ignatian Framework

**Reflection vs. Reaction:**
- Current agents: React to immediate situation (DD → I should D)
- With reflection: Step back, discern optimal path (DD trap → try C)
- Human moral development: Requires both reaction and reflective discernment

**Natural Law Implications:**
- If cooperation emerges: Moral truths discoverable through reason
- If cooperation requires programming: Some moral insights require grace/revelation
- Balance: What can be figured out vs. what must be taught/revealed

---

## Technical Documentation

### Files Requiring Modification

**1. prompts.py** (Main changes needed)
- `format_history_prompt()` - Add full statistics + reflection triggers
- Keep fixed SYSTEM_PROMPT (uppercase/lowercase distinction)
- Add new function: `detect_stuck_pattern()` for pattern detection

**2. ipd_llm_game.py** (Minor changes)
- Pass full history to format_history_prompt (currently passes last 10)
- Track reflection round numbers for analysis
- Log when reflection prompts are triggered

**3. run_batch.py** (Configuration)
- Add experiment type parameter (baseline, enhanced, etc.)
- Track which prompt variant is being used
- Save experiment metadata with results

### New Analysis Scripts Needed

**1. recovery_analysis.py**
- Detect DD trap periods (10+ consecutive DD)
- Identify recovery attempts (C after DD streak)
- Calculate recovery success rate
- Generate summary statistics

**2. reasoning_analysis.py**
- Extract reasoning from reflection rounds
- Code for exploration language ("stuck", "try something different", etc.)
- Code for long-term thinking ("remaining rounds", "future payoffs")
- Compare reasoning quality before/after reflection prompts

**3. comparative_analysis.py**
- Compare baseline vs. enhanced experiments
- Statistical tests on recovery rates
- Visualize cooperation patterns over time
- Generate plots for paper

---

## Open Questions

### Technical
1. What reflection frequency is optimal? (10, 20, 30 rounds?)
2. Should reflection be deterministic or randomized?
3. How much history is necessary? (Full vs. summary statistics?)
4. What directiveness level works without programming the solution?

### Theoretical
1. Is cooperation emergence even possible with current LLMs?
2. If it requires very specific prompts, is it really "emergent"?
3. What's the boundary between enabling emergence and programming it?
4. Can agents develop genuine trust, or only simulate it?

### Experimental
1. How many games needed for statistical significance?
2. Should we test heterogeneous agents (different models/temps)?
3. What role does opponent strategy play in recovery?
4. Can we identify agent "personality" differences?

### Philosophical
1. If LLMs need reflection prompts, does this support or challenge emergence claims?
2. Is periodic reflection "natural" or an artificial intervention?
3. What does failure to cooperate reveal about human moral development?
4. How does this connect to Ignatian discernment practices?

---

## Resources and References

### Code Repository
- Location: `/home/dhart/work/forge/llm/IPD-LLM-Agents/`
- Version control: Git (recommended: create branch for enhanced prompts)
- Results directory: `results/`
- Analysis scripts: TBD

### Key Documents
1. `BUG_REPORT_AND_FIX.md` - Technical documentation of reasoning/action mismatch bug
2. `FIRST_RUN_ANALYSIS.md` - Analysis of game_20260108_152408.json
3. Research plan: "From Cooperation to Conscience" (conference submission)
4. FORGE/GENESIS/PRAXIS overview documents

### Theoretical Foundation
- Axelrod (1984) - Evolution of Cooperation
- Haidt - Moral Foundations Theory
- Hobbes - Leviathan (authority/enforcement)
- Ignatian spirituality - Discernment and reflection

### Ollama Infrastructure
- Models: llama3:8b, mixtral, mistral
- Hosts: iron, nickel, zinc, copper, platinum
- API: Standard Ollama endpoints on port 11434

---

## Summary and Path Forward

### Where We Are
- ✅ Bug fixed: Actions now match reasoning
- ✅ Valid data collection enabled
- ✅ Baseline established: Cooperation does NOT emerge with current prompts
- ⚠️ Agents get trapped in DD and cannot escape
- ⚠️ Competitive interpretation persists

### What We Know
- Initial cooperation ≠ cooperation emergence
- Agents need exploration mechanisms
- Current prompts lack strategic reflection capability
- Problem is analogous to RL's explore-exploit dilemma

### What We'll Test
- Periodic reflection prompts (every 20 rounds)
- Full history statistics (not just last 10 rounds)
- Pattern detection and exploration suggestions
- Different models and parameters

### What Success Looks Like
- Agents recognize DD trap
- Agents calculate long-term payoffs
- Agents intentionally test cooperation
- Agents rebuild trust and sustain CC
- >30% recovery rate in experiments

### Timeline
- **This week:** Implement enhanced prompts, run initial tests
- **Next week:** Model comparison, parameter optimization
- **Following weeks:** Full experimental suite, paper preparation
- **October 2026:** Present findings at Ignatian AI conference

---

## Conclusion

We have successfully debugged the IPD LLM agent system and established that genuine cooperation emergence requires more than initial testing behavior. Agents must be able to recognize suboptimal patterns and deliberately explore alternatives. By implementing periodic reflection mechanisms analogous to RL's explore-exploit strategies, we aim to determine whether LLM agents can discover cooperation through reasoning about long-term incentives.

This investigation directly addresses GENESIS's core question: Can moral foundations (specifically reciprocity and fairness) emerge through interaction and reflection, or do they require explicit programming? The answer will illuminate both the capabilities of current AI systems and the nature of human moral development.

**Next action:** Implement enhanced prompts with full history + periodic reflection, then run comparative experiments to test if cooperation emergence becomes possible.

---

**Document Status:** Current as of January 11, 2026  
**Last Updated By:** Claude (analysis assistant)  
**Next Review:** After enhanced prompt experiments complete
