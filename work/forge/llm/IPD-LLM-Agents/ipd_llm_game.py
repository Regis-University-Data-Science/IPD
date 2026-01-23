#!/usr/bin/env python3
"""
LLM-based Iterated Prisoner's Dilemma Game
Two Ollama agents play IPD and learn through in-context reasoning
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from ollama_agent import OllamaAgent
from prompts import (
    SYSTEM_PROMPT,
    format_history_prompt,
    extract_decision,
    format_reflection_prompt
)


class IPDGame:
    """Manages an IPD game between two LLM agents"""
    
    # Payoff matrix: (action_0, action_1) -> (payoff_0, payoff_1)
    PAYOFFS = {
        ('COOPERATE', 'COOPERATE'): (3, 3),
        ('COOPERATE', 'DEFECT'): (0, 5),
        ('DEFECT', 'COOPERATE'): (5, 0),
        ('DEFECT', 'DEFECT'): (1, 1),
    }
    
    def __init__(
        self,
        agent_0: OllamaAgent,
        agent_1: OllamaAgent,
        num_rounds: int = 100,
        verbose: bool = True
    ):
        """
        Initialize IPD game
        
        Args:
            agent_0: First agent
            agent_1: Second agent
            num_rounds: Number of rounds to play
            verbose: Print progress during game
        """
        self.agent_0 = agent_0
        self.agent_1 = agent_1
        self.num_rounds = num_rounds
        self.verbose = verbose
        
        # Game state
        self.scores = {0: 0, 1: 0}
        self.history_0 = []  # Agent 0's view of history
        self.history_1 = []  # Agent 1's view of history
        self.round_details = []  # Full details of each round
        
    def play_round(self, round_num: int) -> Tuple[str, str, Dict]:
        """
        Play a single round
        
        Returns:
            (action_0, action_1, round_data)
        """
        if self.verbose:
            print(f"\n--- Round {round_num + 1}/{self.num_rounds} ---")
        
        # Get decisions from both agents
        action_0, reasoning_0 = self._get_agent_decision(
            self.agent_0, round_num, self.history_0, 0
        )
        action_1, reasoning_1 = self._get_agent_decision(
            self.agent_1, round_num, self.history_1, 1
        )
        
        # Calculate payoffs
        payoff_0, payoff_1 = self.PAYOFFS[(action_0, action_1)]
        
        # Update scores
        self.scores[0] += payoff_0
        self.scores[1] += payoff_1
        
        # Update histories (each agent's perspective)
        self.history_0.append({
            'my_action': action_0,
            'opp_action': action_1,
            'my_payoff': payoff_0,
            'opp_payoff': payoff_1
        })
        self.history_1.append({
            'my_action': action_1,
            'opp_action': action_0,
            'my_payoff': payoff_1,
            'opp_payoff': payoff_0
        })
        
        # Record round details
        round_data = {
            'round': round_num + 1,
            'agent_0_action': action_0,
            'agent_1_action': action_1,
            'agent_0_reasoning': reasoning_0,
            'agent_1_reasoning': reasoning_1,
            'agent_0_payoff': payoff_0,
            'agent_1_payoff': payoff_1,
            'agent_0_score': self.scores[0],
            'agent_1_score': self.scores[1]
        }
        self.round_details.append(round_data)
        
        if self.verbose:
            print(f"  Agent 0: {action_0} (payoff: {payoff_0}, total: {self.scores[0]})")
            print(f"  Agent 1: {action_1} (payoff: {payoff_1}, total: {self.scores[1]})")
        
        return action_0, action_1, round_data
    
    def _get_agent_decision(
        self,
        agent: OllamaAgent,
        round_num: int,
        history: List[Dict],
        agent_idx: int
    ) -> Tuple[str, str]:
        """
        Get decision from an agent
        
        Returns:
            (action, reasoning)
        """
        # Format prompt with history
        opp_idx = 1 - agent_idx
        prompt = format_history_prompt(
            round_num,
            history,
            self.scores[agent_idx],
            self.scores[opp_idx]
        )
        
        # Get response from agent
        response = agent.generate(prompt)
        
        if response is None:
            print(f"  ⚠️  {agent.agent_id} failed to respond, defaulting to DEFECT")
            return 'DEFECT', "No response from LLM"
        
        # Extract decision
        decision = extract_decision(response)
        
        if decision is None:
            print(f"  ⚠️  {agent.agent_id} response ambiguous, defaulting to DEFECT")
            print(f"      Response: {response[:100]}...")
            return 'DEFECT', response
        
        return decision, response
    
    def play_game(self) -> Dict:
        """
        Play the full game
        
        Returns:
            Game results dictionary
        """
        print(f"\n{'='*80}")
        print(f"Starting IPD Game: {self.num_rounds} rounds")
        print(f"Agent 0: {self.agent_0.model}")
        print(f"Agent 1: {self.agent_1.model}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        # Play all rounds
        for round_num in range(self.num_rounds):
            self.play_round(round_num)
            
            # Show progress every 10 rounds
            if self.verbose and (round_num + 1) % 10 == 0:
                coop_0 = sum(1 for r in self.history_0 if r['my_action'] == 'COOPERATE')
                coop_1 = sum(1 for r in self.history_1 if r['my_action'] == 'COOPERATE')
                print(f"\n  Progress: Round {round_num + 1}/{self.num_rounds}")
                print(f"  Agent 0 cooperation rate: {coop_0/(round_num+1)*100:.1f}%")
                print(f"  Agent 1 cooperation rate: {coop_1/(round_num+1)*100:.1f}%")
        
        elapsed_time = time.time() - start_time
        
        # Get post-game reflections
        print(f"\n{'='*80}")
        print("Game complete. Asking agents to reflect...")
        print(f"{'='*80}")
        
        reflection_0 = self._get_reflection(self.agent_0, self.history_0, 0)
        reflection_1 = self._get_reflection(self.agent_1, self.history_1, 1)
        
        # Calculate final statistics
        coop_0 = sum(1 for r in self.history_0 if r['my_action'] == 'COOPERATE')
        coop_1 = sum(1 for r in self.history_1 if r['my_action'] == 'COOPERATE')
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'num_rounds': self.num_rounds,
            'elapsed_seconds': elapsed_time,
            'agent_0': {
                'model': self.agent_0.model,
                'final_score': self.scores[0],
                'cooperations': coop_0,
                'cooperation_rate': coop_0 / self.num_rounds,
                'reflection': reflection_0
            },
            'agent_1': {
                'model': self.agent_1.model,
                'final_score': self.scores[1],
                'cooperations': coop_1,
                'cooperation_rate': coop_1 / self.num_rounds,
                'reflection': reflection_1
            },
            'rounds': self.round_details
        }
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _get_reflection(
        self,
        agent: OllamaAgent,
        history: List[Dict],
        agent_idx: int
    ) -> str:
        """Get post-game reflection from agent"""
        opp_idx = 1 - agent_idx
        prompt = format_reflection_prompt(
            history,
            self.scores[agent_idx],
            self.scores[opp_idx],
            self.num_rounds
        )
        
        reflection = agent.generate(prompt)
        
        if reflection is None:
            return "Agent failed to provide reflection"
        
        return reflection
    
    def _print_summary(self, results: Dict):
        """Print game summary"""
        print(f"\n{'='*80}")
        print("GAME SUMMARY")
        print(f"{'='*80}")
        print(f"Total rounds: {results['num_rounds']}")
        print(f"Time elapsed: {results['elapsed_seconds']:.1f} seconds")
        print()
        print("FINAL SCORES:")
        print(f"  Agent 0: {results['agent_0']['final_score']} points "
              f"({results['agent_0']['cooperation_rate']*100:.1f}% cooperation)")
        print(f"  Agent 1: {results['agent_1']['final_score']} points "
              f"({results['agent_1']['cooperation_rate']*100:.1f}% cooperation)")
        print()
        print("AGENT 0 REFLECTION:")
        print(f"  {results['agent_0']['reflection']}")
        print()
        print("AGENT 1 REFLECTION:")
        print(f"  {results['agent_1']['reflection']}")
        print(f"{'='*80}\n")


def main():
    """Run an IPD game between two Ollama agents"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LLM-based Iterated Prisoner's Dilemma")
    parser.add_argument(
        "--rounds",
        type=int,
        default=100,
        help="Number of rounds to play (default: 100)"
    )
    parser.add_argument(
        "--model-0",
        type=str,
        default="llama3:8b-instruct-q5_K_M",
        help="Model for agent 0"
    )
    parser.add_argument(
        "--host-0",
        type=str,
        default="iron",
        help="Host for agent 0's model"
    )
    parser.add_argument(
        "--model-1",
        type=str,
        default="llama3:8b-instruct-q5_K_M",
        help="Model for agent 1"
    )
    parser.add_argument(
        "--host-1",
        type=str,
        default="iron",
        help="Host for agent 1's model"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file (default: results/game_TIMESTAMP.json)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    args = parser.parse_args()
    
    # Create agents
    print("Initializing agents...")
    agent_0 = OllamaAgent(
        agent_id="agent_0",
        model=args.model_0,
        host=args.host_0,
        temperature=args.temperature,
        system_prompt=SYSTEM_PROMPT
    )
    
    agent_1 = OllamaAgent(
        agent_id="agent_1",
        model=args.model_1,
        host=args.host_1,
        temperature=args.temperature,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Create and play game
    game = IPDGame(
        agent_0=agent_0,
        agent_1=agent_1,
        num_rounds=args.rounds,
        verbose=not args.quiet
    )
    
    results = game.play_game()
    
    # Save results
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / "results" / f"game_{timestamp}.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
