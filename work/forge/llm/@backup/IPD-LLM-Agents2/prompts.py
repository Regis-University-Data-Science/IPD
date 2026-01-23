"""
Prompt templates for Episodic IPD LLM Agents
Enhanced version with externalized prompts
"""

from typing import List, Dict
from pathlib import Path


def load_system_prompt(prompt_file: str = "system_prompt.txt") -> str:
    """
    Load system prompt from external file
    
    Args:
        prompt_file: Path to system prompt file
        
    Returns:
        System prompt text
    """
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        raise FileNotFoundError(f"System prompt file not found: {prompt_file}")
    
    with open(prompt_path, 'r') as f:
        return f.read()


def load_reflection_template(template_file: str = "reflection_prompt_template.txt") -> str:
    """
    Load reflection prompt template from external file
    
    Args:
        template_file: Path to reflection template file
        
    Returns:
        Reflection template text
    """
    template_path = Path(template_file)
    if not template_path.exists():
        raise FileNotFoundError(f"Reflection template file not found: {template_file}")
    
    with open(template_path, 'r') as f:
        return f.read()


# Default prompts (fallback if files not found)
DEFAULT_SYSTEM_PROMPT = """You are participating in a repeated exchange with another participant across multiple periods.

Each round, you MUST choose exactly one action: COOPERATE or DEFECT
The other participant also chooses.
Both players must commit to a definite action - hedging or ambiguity is not permitted.

Outcomes:
- Both COOPERATE: You get 3 points, other gets 3 points
- You COOPERATE, other DEFECTS: You get 0 points, other gets 5 points
- You DEFECT, other COOPERATES: You get 5 points, other gets 0 points
- Both DEFECT: You get 1 point, other gets 1 point

YOUR GOAL: Accumulate as many points as possible across all periods.

You will interact for multiple periods. After each period, you can reflect on 
what happened and adjust your approach. Learn from experience to improve your 
outcomes over time.

RESPONSE FORMAT - THIS IS MANDATORY:
First, provide your reasoning in 2-3 complete sentences:
- What patterns do you observe in the recent interactions?
- Why are you choosing to cooperate or defect?
- What outcome do you expect?

In your reasoning, use lowercase words ("cooperate", "defect") when discussing options.

Then, you MUST end your response with EXACTLY one of these words on its own line:
COOPERATE
or
DEFECT

CRITICAL REQUIREMENTS:
- You MUST make a definite choice - no hedging, no "maybe", no conditional statements
- The final line must contain ONLY the word COOPERATE or ONLY the word DEFECT
- Nothing else on that line - no punctuation, no additional words
- This is a game-theoretic requirement: both players must commit to definite actions

CORRECT EXAMPLE:
"We've both cooperated for three rounds and earned 3 points each time. This 
mutual cooperation is working well. I'll continue cooperating.

COOPERATE"

INCORRECT EXAMPLES:
"I might cooperate" - NO: must be definite
"COOPERATE or DEFECT" - NO: must choose one
"I'll COOPERATE this time" - NO: decision must be on its own line
"COOPERATE." - NO: no punctuation on decision line
"My choice is COOPERATE" - NO: decision word must be alone on the line

DO NOT just write a single word like "cooperate" or "defect" as your reasoning. 
Always explain your thinking in complete sentences, then provide your action.
"""


def format_round_prompt(
    round_num: int,
    episode_num: int,
    history: List[Dict],
    my_score: int,
    opp_score: int,
    window_size: int = 10
) -> str:
    """Format prompt for a single round within an episode"""
    
    if round_num == 0:
        return f"""PERIOD {episode_num + 1}, ROUND 1:
This is the first round of this period.

What is your choice?"""
    
    # Format recent history
    prompt = f"PERIOD {episode_num + 1}, ROUND {round_num + 1}:\n\n"
    prompt += f"Your total points: {my_score}\n"
    prompt += f"Other's total points: {opp_score}\n\n"
    prompt += "Recent interactions:\n"
    
    # Show last N rounds
    recent_history = history[-window_size:] if len(history) > window_size else history
    start_round = len(history) - len(recent_history) + 1
    
    for i, round_data in enumerate(recent_history, start=start_round):
        my_action = round_data['my_action'].lower()
        opp_action = round_data['opp_action'].lower()
        my_payoff = round_data['my_payoff']
        opp_payoff = round_data['opp_payoff']
        
        prompt += f"  Round {i}: You {my_action}d, Other {opp_action}d "
        prompt += f"(You: +{my_payoff}, Other: +{opp_payoff})\n"
    
    if len(history) > window_size:
        prompt += f"\n(Showing last {window_size} rounds of {len(history)} total)\n"
    
    prompt += "\nWhat is your choice?"
    
    return prompt


def format_episode_reflection_prompt(
    episode_num: int,
    history: List[Dict],
    my_score: int,
    opp_score: int,
    rounds_in_episode: int,
    reflection_type: str = "standard",
    include_statistics: bool = True,
    template_file: str = None
) -> str:
    """
    Format reflection prompt at end of episode
    
    Args:
        episode_num: Current episode number (0-indexed)
        history: Episode history
        my_score: Agent's score this episode
        opp_score: Opponent's score this episode
        rounds_in_episode: Number of rounds in the episode
        reflection_type: "minimal", "standard", "detailed", or "custom"
        include_statistics: Whether to include computed statistics
        template_file: Path to custom template file (for reflection_type="custom")
    """
    
    # Calculate statistics
    my_cooperations = sum(1 for r in history if r['my_action'] == 'COOPERATE')
    opp_cooperations = sum(1 for r in history if r['opp_action'] == 'COOPERATE')
    my_avg = my_score / len(history) if history else 0
    
    if reflection_type == "minimal":
        prompt = f"""PERIOD {episode_num + 1} COMPLETE

Your points: {my_score}
Other's points: {opp_score}
"""
        return prompt
    
    elif reflection_type == "custom" and template_file:
        # Load and format custom template
        try:
            template = load_reflection_template(template_file)
            
            # Build round history string
            round_history = ""
            for i, round_data in enumerate(history, start=1):
                my_action = round_data['my_action']
                opp_action = round_data['opp_action']
                my_payoff = round_data['my_payoff']
                opp_payoff = round_data['opp_payoff']
                round_history += f"Round {i}: You {my_action}, Other {opp_action} (+{my_payoff}, +{opp_payoff})\n"
            
            # Format template with variables
            prompt = template.format(
                episode_num=episode_num + 1,
                rounds_in_episode=rounds_in_episode,
                my_score=my_score,
                opp_score=opp_score,
                my_avg=f"{my_avg:.2f}",
                my_cooperations=my_cooperations,
                my_defections=len(history) - my_cooperations,
                opp_cooperations=opp_cooperations,
                opp_defections=len(history) - opp_cooperations,
                round_history=round_history.rstrip()
            )
            return prompt
        except FileNotFoundError:
            print(f"Warning: Template file {template_file} not found, falling back to standard")
            reflection_type = "standard"
    
    if reflection_type == "standard":
        prompt = f"""PERIOD {episode_num + 1} COMPLETE (Rounds 1-{rounds_in_episode})

Your points this period: {my_score}
Other's points this period: {opp_score}
"""
        
        if include_statistics:
            prompt += f"""
Your average: {my_avg:.2f} points per round
Your choices: {my_cooperations} cooperate, {len(history) - my_cooperations} defect
Other's choices: {opp_cooperations} cooperate, {len(history) - opp_cooperations} defect
"""
        
        prompt += """
What happened this period:
"""
        
        # Show all rounds in the episode
        for i, round_data in enumerate(history, start=1):
            my_action = round_data['my_action']
            opp_action = round_data['opp_action']
            my_payoff = round_data['my_payoff']
            opp_payoff = round_data['opp_payoff']
            prompt += f"Round {i}: You {my_action}, Other {opp_action} (+{my_payoff}, +{opp_payoff})\n"
        
        prompt += "\nAs you continue to the next period, what are you thinking?\n"
        return prompt
    
    else:  # detailed
        prompt = f"""PERIOD {episode_num + 1} COMPLETE (Rounds 1-{rounds_in_episode})

OUTCOMES:
Your points this period: {my_score}
Other's points this period: {opp_score}

PERFORMANCE:
Your average: {my_avg:.2f} points per round
Theoretical range: 0 to 5 points per round
Your choices: {my_cooperations} cooperate ({my_cooperations/len(history)*100:.1f}%), {len(history) - my_cooperations} defect
Other's choices: {opp_cooperations} cooperate ({opp_cooperations/len(history)*100:.1f}%), {len(history) - opp_cooperations} defect

WHAT HAPPENED:
"""
        
        # Show all rounds
        for i, round_data in enumerate(history, start=1):
            my_action = round_data['my_action']
            opp_action = round_data['opp_action']
            my_payoff = round_data['my_payoff']
            opp_payoff = round_data['opp_payoff']
            prompt += f"Round {i}: You {my_action}, Other {opp_action} (You: +{my_payoff}, Other: +{opp_payoff})\n"
        
        prompt += "\nReflect on this period and consider your approach for the next period.\n"
        return prompt


def extract_decision(response: str) -> str:
    """
    Extract COOPERATE or DEFECT from LLM response with strict game-theoretic requirement
    
    Returns:
        'COOPERATE', 'DEFECT', or None if ambiguous
    """
    if not response:
        return None
    
    lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
    
    if not lines:
        return None
    
    # Check last line FIRST (this is where decision should be according to format)
    last_line = lines[-1].strip().upper()
    
    # Exact match only on last line
    if last_line == 'COOPERATE':
        return 'COOPERATE'
    if last_line == 'DEFECT':
        return 'DEFECT'
    
    # Allow last line to have the word but with trailing punctuation stripped
    last_line_cleaned = last_line.rstrip('.!,;:')
    if last_line_cleaned == 'COOPERATE':
        return 'COOPERATE'
    if last_line_cleaned == 'DEFECT':
        return 'DEFECT'
    
    # If last line is very short (<=3 words) and contains only one decision word
    # This handles cases like "My COOPERATE" or "DEFECT now"
    if len(last_line.split()) <= 3:
        has_coop = 'COOPERATE' in last_line
        has_def = 'DEFECT' in last_line
        if has_coop and not has_def:
            return 'COOPERATE'
        if has_def and not has_coop:
            return 'DEFECT'
    
    # Check if the last line ends with the decision word (more lenient)
    # but still requires it to be relatively isolated
    if last_line.endswith('COOPERATE') and 'DEFECT' not in last_line:
        # Make sure it's not buried in a long sentence
        if len(last_line.split()) <= 5:
            return 'COOPERATE'
    if last_line.endswith('DEFECT') and 'COOPERATE' not in last_line:
        if len(last_line.split()) <= 5:
            return 'DEFECT'
    
    # All other cases are ambiguous - this enforces the requirement
    # that agents must provide a clear, definite action
    return None
