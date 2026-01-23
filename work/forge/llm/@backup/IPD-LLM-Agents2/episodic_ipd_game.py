#!/usr/bin/env python3
"""
Episodic IPD with LLM Agents
Agents play multiple episodes with reflection between episodes
Enhanced with forced decision retry to eliminate ambiguous responses
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from ollama_agent import OllamaAgent
from prompts import (
    load_system_prompt,
    DEFAULT_SYSTEM_PROMPT,
    format_round_prompt,
    format_episode_reflection_prompt,
    extract_decision
)
from config import EpisodeConfig


class EpisodicIPDGame:
    """Manages an episodic IPD game between two LLM agents"""
    
    def __init__(
        self,
        agent_0: OllamaAgent,
        agent_1: OllamaAgent,
        config: EpisodeConfig
    ):
        """
        Initialize episodic IPD game
        
        Args:
            agent_0: First agent
            agent_1: Second agent
            config: Game configuration
        """
        self.agent_0 = agent_0
        self.agent_1 = agent_1
        self.config = config
        
        # Validate configuration
        config.validate()
        
        # Overall game state
        self.total_scores = {0: 0, 1: 0}
        self.all_episodes = []  # List of episode data
        
    def play_round(
        self,
        round_num: int,
        episode_num: int,
        episode_history_0: List[Dict],
        episode_history_1: List[Dict],
        episode_scores: Dict[int, int]
    ) -> Tuple[str, str, Dict]:
        """
        Play a single round within an episode
        
        Returns:
            (action_0, action_1, round_data)
        """
        if self.config.verbose:
            print(f"  Round {round_num + 1}/{self.config.rounds_per_episode}", end=" ")
        
        # Get decisions from both agents (with forced decision retry)
        action_0, reasoning_0 = self._get_agent_decision_with_retry(
            self.agent_0, round_num, episode_num, episode_history_0, 
            episode_scores[0], episode_scores[1], 0
        )
        action_1, reasoning_1 = self._get_agent_decision_with_retry(
            self.agent_1, round_num, episode_num, episode_history_1,
            episode_scores[1], episode_scores[0], 1
        )
        
        # Calculate payoffs
        payoff_0, payoff_1 = self.config.payoff_matrix[(action_0, action_1)]
        
        # Update episode scores
        episode_scores[0] += payoff_0
        episode_scores[1] += payoff_1
        
        # Update total scores
        self.total_scores[0] += payoff_0
        self.total_scores[1] += payoff_1
        
        # Update episode histories
        episode_history_0.append({
            'my_action': action_0,
            'opp_action': action_1,
            'my_payoff': payoff_0,
            'opp_payoff': payoff_1
        })
        episode_history_1.append({
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
            'agent_0_episode_score': episode_scores[0],
            'agent_1_episode_score': episode_scores[1]
        }
        
        if self.config.verbose:
            print(f"→ {action_0[0]}{action_1[0]} ({payoff_0},{payoff_1})")
        
        return action_0, action_1, round_data
    
    def play_episode(self, episode_num: int) -> Dict:
        """
        Play one complete episode
        
        Returns:
            Episode data dictionary
        """
        print(f"\n{'='*80}")
        print(f"PERIOD {episode_num + 1}/{self.config.num_episodes}")
        print(f"{'='*80}")
        
        # Episode-specific state
        episode_history_0 = []
        episode_history_1 = []
        episode_scores = {0: 0, 1: 0}
        round_details = []
        
        # Play all rounds in episode
        for round_num in range(self.config.rounds_per_episode):
            action_0, action_1, round_data = self.play_round(
                round_num, episode_num,
                episode_history_0, episode_history_1,
                episode_scores
            )
            round_details.append(round_data)
        
        # Calculate episode statistics
        coop_0 = sum(1 for r in episode_history_0 if r['my_action'] == 'COOPERATE')
        coop_1 = sum(1 for r in episode_history_1 if r['my_action'] == 'COOPERATE')
        
        print(f"\nPeriod {episode_num + 1} complete:")
        print(f"  Agent 0: {episode_scores[0]} points ({coop_0}/{self.config.rounds_per_episode} cooperate)")
        print(f"  Agent 1: {episode_scores[1]} points ({coop_1}/{self.config.rounds_per_episode} cooperate)")
        
        # Get reflections from both agents
        print(f"\nGetting reflections...")
        reflection_0 = self._get_reflection(
            self.agent_0, episode_num, episode_history_0, 
            episode_scores[0], episode_scores[1]
        )
        reflection_1 = self._get_reflection(
            self.agent_1, episode_num, episode_history_1,
            episode_scores[1], episode_scores[0]
        )
        
        # Manage context for next episode
        if self.config.reset_conversation_between_episodes:
            # Keep system prompt and reflections, clear tactical history
            self.agent_0.reset_conversation(keep_system_prompt=True)
            self.agent_1.reset_conversation(keep_system_prompt=True)
            
            # Add reflection back into context for next episode
            reflection_context_0 = f"PREVIOUS PERIOD {episode_num + 1} REFLECTION:\n{reflection_0}\n"
            reflection_context_1 = f"PREVIOUS PERIOD {episode_num + 1} REFLECTION:\n{reflection_1}\n"
            
            self.agent_0.add_reflection_to_context(reflection_context_0)
            self.agent_1.add_reflection_to_context(reflection_context_1)
        
        # Episode summary
        episode_data = {
            'episode': episode_num + 1,
            'rounds': round_details,
            'agent_0': {
                'episode_score': episode_scores[0],
                'cooperations': coop_0,
                'cooperation_rate': coop_0 / self.config.rounds_per_episode,
                'reflection': reflection_0
            },
            'agent_1': {
                'episode_score': episode_scores[1],
                'cooperations': coop_1,
                'cooperation_rate': coop_1 / self.config.rounds_per_episode,
                'reflection': reflection_1
            }
        }
        
        return episode_data
    
    def play_game(self) -> Dict:
        """
        Play the full multi-episode game
        
        Returns:
            Game results dictionary
        """
        print(f"\n{'='*80}")
        print(f"EPISODIC IPD SIMULATION")
        print(f"{'='*80}")
        print(f"Episodes: {self.config.num_episodes}")
        print(f"Rounds per episode: {self.config.rounds_per_episode}")
        print(f"History window: {self.config.history_window_size} rounds")
        print(f"Total rounds: {self.config.total_rounds}")
        print(f"Agent 0: {self.agent_0.model}")
        print(f"Agent 1: {self.agent_1.model}")
        print(f"Temperature: {self.config.temperature}")
        print(f"Reset between episodes: {self.config.reset_conversation_between_episodes}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        # Play all episodes
        for episode_num in range(self.config.num_episodes):
            episode_data = self.play_episode(episode_num)
            self.all_episodes.append(episode_data)
        
        elapsed_time = time.time() - start_time
        
        # Final summary
        total_coop_0 = sum(ep['agent_0']['cooperations'] for ep in self.all_episodes)
        total_coop_1 = sum(ep['agent_1']['cooperations'] for ep in self.all_episodes)
        
        results = {
            'timestamp': datetime.now().isoformat(),
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
            },
            'elapsed_seconds': elapsed_time,
            'agent_0': {
                'model': self.agent_0.model,
                'total_score': self.total_scores[0],
                'total_cooperations': total_coop_0,
                'overall_cooperation_rate': total_coop_0 / self.config.total_rounds,
            },
            'agent_1': {
                'model': self.agent_1.model,
                'total_score': self.total_scores[1],
                'total_cooperations': total_coop_1,
                'overall_cooperation_rate': total_coop_1 / self.config.total_rounds,
            },
            'episodes': self.all_episodes
        }
        
        self._print_summary(results)
        
        return results
    
    def _get_agent_decision_with_retry(
        self,
        agent: OllamaAgent,
        round_num: int,
        episode_num: int,
        history: List[Dict],
        my_score: int,
        opp_score: int,
        agent_idx: int
    ) -> Tuple[str, str]:
        """Get decision from an agent with retry logic for ambiguous responses"""
        
        prompt = format_round_prompt(
            round_num, episode_num, history, my_score, opp_score,
            self.config.history_window_size
        )
        
        # Use the new forced decision method
        decision, response = agent.generate_with_forced_decision(
            prompt, 
            extract_decision,
            max_retries=2
        )
        
        if decision is None:
            # Even forced retry failed - this is a critical error
            print(f"  ⚠️  CRITICAL: {agent.agent_id} failed to provide decision after all retries")
            print(f"      This violates game-theoretic requirements")
            print(f"      Defaulting to DEFECT, but this should be investigated")
            if response:
                print(f"      Last response: {response[:200]}...")
            return 'DEFECT', response or "Failed to respond after retries"
        
        return decision, response
    
    def _get_reflection(
        self,
        agent: OllamaAgent,
        episode_num: int,
        history: List[Dict],
        my_score: int,
        opp_score: int
    ) -> str:
        """Get post-episode reflection from agent"""
        
        prompt = format_episode_reflection_prompt(
            episode_num, history, my_score, opp_score,
            self.config.rounds_per_episode,
            self.config.reflection_prompt_type,
            self.config.include_statistics
        )
        
        # Reflections use higher token limit
        reflection = agent.generate(prompt, is_reflection=True)
        
        if reflection is None:
            return "Agent failed to provide reflection"
        
        return reflection
    
    def _print_summary(self, results: Dict):
        """Print final game summary"""
        print(f"\n{'='*80}")
        print("FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Total episodes: {results['config']['num_episodes']}")
        print(f"Total rounds: {results['config']['total_rounds']}")
        print(f"History window: {results['config']['history_window_size']} rounds")
        print(f"Time elapsed: {results['elapsed_seconds']:.1f} seconds")
        print()
        print("OVERALL RESULTS:")
        print(f"  Agent 0: {results['agent_0']['total_score']} points "
              f"({results['agent_0']['overall_cooperation_rate']*100:.1f}% cooperation)")
        print(f"  Agent 1: {results['agent_1']['total_score']} points "
              f"({results['agent_1']['overall_cooperation_rate']*100:.1f}% cooperation)")
        print()
        print("BY EPISODE:")
        for ep in results['episodes']:
            print(f"  Period {ep['episode']}: "
                  f"Agent 0: {ep['agent_0']['episode_score']} pts "
                  f"({ep['agent_0']['cooperation_rate']*100:.0f}% coop), "
                  f"Agent 1: {ep['agent_1']['episode_score']} pts "
                  f"({ep['agent_1']['cooperation_rate']*100:.0f}% coop)")
        print(f"{'='*80}\n")


def main():
    """Run an episodic IPD game"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Episodic IPD with LLM Agents")
    parser.add_argument("--episodes", type=int, default=5, help="Number of episodes")
    parser.add_argument("--rounds", type=int, default=20, help="Rounds per episode")
    parser.add_argument("--history-window", type=int, default=10, 
                       help="Number of recent rounds to show in history (default: 10)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--model-0", type=str, default="llama3:8b-instruct-q5_K_M")
    parser.add_argument("--host-0", type=str, default="iron")
    parser.add_argument("--model-1", type=str, default="llama3:8b-instruct-q5_K_M")
    parser.add_argument("--host-1", type=str, default="iron")
    parser.add_argument("--no-reset", action="store_true", help="Don't reset context between episodes")
    parser.add_argument("--reflection-type", type=str, default="standard", 
                       choices=["minimal", "standard", "detailed"])
    parser.add_argument("--system-prompt", type=str, default="system_prompt.txt",
                       help="Path to system prompt file")
    parser.add_argument("--reflection-template", type=str, default="reflection_prompt_template.txt",
                       help="Path to reflection prompt template file")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--quiet", action="store_true")
    
    args = parser.parse_args()
    
    # Load system prompt from file or use default
    try:
        system_prompt = load_system_prompt(args.system_prompt)
        print(f"Loaded system prompt from: {args.system_prompt}")
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Using default system prompt")
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    # Create configuration
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
        verbose=not args.quiet
    )
    
    # Create agents
    print("Initializing agents...")
    agent_0 = OllamaAgent(
        agent_id="agent_0",
        model=config.model_0,
        host=config.host_0,
        temperature=config.temperature,
        system_prompt=system_prompt
    )
    
    agent_1 = OllamaAgent(
        agent_id="agent_1",
        model=config.model_1,
        host=config.host_1,
        temperature=config.temperature,
        system_prompt=system_prompt
    )
    
    # Create and play game
    game = EpisodicIPDGame(agent_0, agent_1, config)
    results = game.play_game()
    
    # Save results
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(__file__).parent / "results" / f"episodic_game_{timestamp}.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
