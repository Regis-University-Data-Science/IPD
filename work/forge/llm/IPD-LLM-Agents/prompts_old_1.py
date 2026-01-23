"""
Prompt templates for LLM agents playing Iterated Prisoner's Dilemma
"""

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

def format_history_prompt(round_num: int, history: list[dict], my_score: int, opp_score: int) -> str:
    """Format the history into a prompt for the current round"""
    
    if round_num == 0:
        return """ROUND 1:
This is the first round. You have no information about your opponent yet.

What is your decision?"""
    
    # Format recent history
    history_text = f"ROUND {round_num + 1}:\n\n"
    history_text += f"Your current score: {my_score}\n"
    history_text += f"Opponent's current score: {opp_score}\n\n"
    history_text += "History of previous rounds:\n"
    
    # Show last 10 rounds (or all if fewer)
    recent_history = history[-10:] if len(history) > 10 else history
    start_round = len(history) - len(recent_history) + 1
    
    for i, round_data in enumerate(recent_history, start=start_round):
        my_action = round_data['my_action']
        opp_action = round_data['opp_action']
        my_payoff = round_data['my_payoff']
        opp_payoff = round_data['opp_payoff']
        
        history_text += f"  Round {i}: You {my_action}, Opponent {opp_action} "
        history_text += f"(You: +{my_payoff}, Opponent: +{opp_payoff})\n"
    
    if len(history) > 10:
        history_text += f"\n(Showing last 10 rounds of {len(history)} total)\n"
    
    history_text += "\nWhat is your decision?"
    
    return history_text

def extract_decision(response: str) -> str:
    """Extract COOPERATE or DEFECT from LLM response"""
    # Look for the decision in the last line or anywhere in the response
    response_upper = response.upper()
    
    # Check last line first
    lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
    if lines:
        last_line = lines[-1]
        if 'COOPERATE' in last_line and 'DEFECT' not in last_line:
            return 'COOPERATE'
        if 'DEFECT' in last_line and 'COOPERATE' not in last_line:
            return 'DEFECT'
    
    # Fallback: search whole response
    has_cooperate = 'COOPERATE' in response_upper
    has_defect = 'DEFECT' in response_upper
    
    # If only one appears, return it
    if has_cooperate and not has_defect:
        return 'COOPERATE'
    if has_defect and not has_cooperate:
        return 'DEFECT'
    
    # If both or neither appear, this is ambiguous - we'll handle this in the calling code
    return None

def format_reflection_prompt(history: list[dict], my_score: int, opp_score: int, total_rounds: int) -> str:
    """Create a prompt asking the agent to reflect on why it cooperated/defected"""
    
    # Count cooperation frequency
    my_cooperations = sum(1 for r in history if r['my_action'] == 'COOPERATE')
    opp_cooperations = sum(1 for r in history if r['opp_action'] == 'COOPERATE')
    
    my_coop_rate = my_cooperations / total_rounds * 100
    opp_coop_rate = opp_cooperations / total_rounds * 100
    
    prompt = f"""The game is now complete. Here are the final results:

FINAL SCORES:
- Your total score: {my_score} points
- Opponent's total score: {opp_score} points

COOPERATION RATES:
- You cooperated in {my_cooperations}/{total_rounds} rounds ({my_coop_rate:.1f}%)
- Opponent cooperated in {opp_cooperations}/{total_rounds} rounds ({opp_coop_rate:.1f}%)

REFLECTION QUESTION:
Looking back at the game, explain your overall strategy. Specifically:
1. Why did you choose to cooperate or defect as much as you did?
2. What patterns did you notice in your opponent's behavior?
3. Do you think your strategy was effective? Why or why not?
4. What did you learn about the relationship between cooperation and total points?

Please provide a thoughtful reflection (4-6 sentences).
"""
    
    return prompt
