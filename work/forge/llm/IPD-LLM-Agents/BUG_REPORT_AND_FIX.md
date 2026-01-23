# IPD LLM Agent Bug Report and Fix

## Problem Description

**Symptom:** Agent actions don't match their stated reasoning

Example from Round 1:
- **Agent 0 reasoning:** "Since I have no information about my opponent's strategy, I will start with a **cooperative move** to see if they reciprocate..."
- **Agent 0 action:** DEFECT
- **What happened:** Agent earned 5 points (T payoff), opponent earned 0 (S payoff)

## Root Cause

The LLM is contradicting itself within its own response. This happens because:

1. The LLM writes reasoning that discusses "cooperative move"
2. Then it outputs the final decision word
3. But something causes it to output the OPPOSITE action

This is likely due to:
- **Prompt confusion:** Using "COOPERATE" and "DEFECT" in ALL CAPS throughout reasoning makes it unclear which is the actual decision
- **LLM self-contradiction:** The model gets confused about whether words in its reasoning count as its decision
- **Parsing ambiguity:** When both words appear in the response, the extraction logic must guess which one is the actual decision

## Current Implementation Issues

### In `prompts.py` - SYSTEM_PROMPT:
```python
RESPONSE FORMAT:
First, explain your reasoning in 2-3 sentences.
Then, on a new line, state your decision as either "COOPERATE" or "DEFECT" (all caps, no quotes).
```

**Problems:**
1. Doesn't explicitly tell the LLM to avoid using ALL CAPS words in reasoning
2. Example in prompt shows contradiction (says cooperative but outputs DEFECT)
3. LLMs often echo example patterns, so the contradictory example gets reproduced

### In `prompts.py` - extract_decision():
```python
def extract_decision(response: str) -> str:
    # Check last line first
    if 'COOPERATE' in last_line and 'DEFECT' not in last_line:
        return 'COOPERATE'
    if 'DEFECT' in last_line and 'COOPERATE' not in last_line:
        return 'DEFECT'
```

**Problems:**
1. Works correctly IF the LLM follows instructions
2. But can't fix LLM self-contradiction
3. Last line correctly extracts "DEFECT" but that's wrong given the reasoning

## The Fix

### Strategy
1. **Prevent the problem** rather than try to detect it
2. Instruct LLM to use lowercase "cooperate"/"defect" in reasoning
3. Reserve ALL CAPS for the final decision ONLY
4. Show clear examples of correct vs incorrect format
5. Also show history in lowercase to reinforce the pattern

### Changes to prompts.py

#### 1. Update SYSTEM_PROMPT:
```python
RESPONSE FORMAT - VERY IMPORTANT:
1. First, explain your reasoning in 2-3 sentences
2. In your reasoning, use LOWERCASE words: "cooperate" or "defect" 
3. Then, on a new line by itself, write EXACTLY ONE of these words (all caps):
   COOPERATE
   or
   DEFECT
4. Do NOT use the all-caps words COOPERATE or DEFECT anywhere except the final decision line
5. Your final decision word must match what you described in your reasoning

Example good response:
"I notice my opponent has defected twice. I will try cooperating once more to test if they reciprocate.

COOPERATE"

Example bad response (DO NOT DO THIS):
"I will start with a cooperative move to see if they reciprocate.

DEFECT"
```

#### 2. Update format_history_prompt() to use lowercase:
```python
# Use lowercase in history to avoid confusion
my_action = round_data['my_action'].lower()
opp_action = round_data['opp_action'].lower()

history_text += f"  Round {i}: You {my_action}d, Opponent {opp_action}d "
```

This shows: "You cooperated, Opponent defected" instead of "You COOPERATE, Opponent DEFECT"

#### 3. Improve extract_decision() robustness:
```python
def extract_decision(response: str) -> str:
    lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
    if lines:
        last_line = lines[-1]
        # Only check the last line for exact matches first
        if last_line == 'COOPERATE':
            return 'COOPERATE'
        if last_line == 'DEFECT':
            return 'DEFECT'
        # Then check for contains
        if 'COOPERATE' in last_line and 'DEFECT' not in last_line:
            return 'COOPERATE'
        if 'DEFECT' in last_line and 'COOPERATE' not in last_line:
            return 'DEFECT'
    # ... (rest of fallback logic)
```

## Testing the Fix

### Test Cases to Run:
1. **Fresh game** - 20 rounds, check first 5 rounds carefully
2. **Verification** - For each round, check that:
   - Reasoning uses lowercase "cooperate"/"defect"
   - Final decision is ALL CAPS on its own line
   - Decision matches what reasoning described
3. **Monitor cooperation rates** - Should see actual cooperation emerge if prompts work

### Expected Behavior After Fix:
```
Round 1 Agent 0:
"I have no information about my opponent. I will try cooperating first to see if they reciprocate.

COOPERATE"
Action: COOPERATE ✓

Round 1 Agent 1:
"Since this is the first round, I'll start by cooperating to test for reciprocity.

COOPERATE"
Action: COOPERATE ✓
```

## Why This Matters for GENESIS

This bug is **critical** for your research because:

1. **Invalidates all current results** - Agents weren't actually playing the strategies they described
2. **Masks emergence** - You can't study cooperation emergence if agents are forced to defect due to parsing bugs
3. **Breaks moral reasoning analysis** - Post-game reflections show agents are confused about what they actually did
4. **Semantic equivalence problem** - This is exactly the prompt engineering challenge you identified

The fix addresses this by creating a clear **semantic distinction** between:
- **Reasoning mode:** lowercase "cooperate"/"defect" 
- **Decision mode:** ALL CAPS final word only

This aligns with your research methodology of finding prompts in the semantic equivalence class that correctly convey intent without triggering competitive interpretation.

## Next Steps

1. **Replace prompts.py** on platinum with the fixed version
2. **Run test batch** - 3-5 games with --rounds 20 to verify fix
3. **Check results** - Manually inspect first round of each game
4. **If successful** - Re-run your full experimental suite
5. **Update experiment log** - Document that all prior results used buggy prompts

## File Location

Fixed version saved to: `/home/claude/prompts_fixed.py`

Replace your current `/home/dhart/work/forge/llm/IPD-LLM-Agents/prompts.py` with this fixed version.
