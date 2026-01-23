#!/usr/bin/env python3
"""
Quick test script for episodic IPD system
Runs a short game to verify everything works
"""

from config import EpisodeConfig
from ollama_agent import OllamaAgent
from prompts import SYSTEM_PROMPT
from episodic_ipd_game import EpisodicIPDGame
import json
from datetime import datetime


def test_episodic_game():
    """Run a quick test game"""
    
    print("="*80)
    print("EPISODIC IPD TEST")
    print("="*80)
    
    # Create a short test configuration
    config = EpisodeConfig(
        num_episodes=3,
        rounds_per_episode=10,
        temperature=0.7,
        model_0="llama3:8b-instruct-q5_K_M",
        host_0="iron",
        model_1="llama3:8b-instruct-q5_K_M",
        host_1="iron",
        reset_conversation_between_episodes=True,
        reflection_prompt_type="standard",
        include_statistics=True,
        verbose=True
    )
    
    print(f"\nTest configuration:")
    print(f"  Episodes: {config.num_episodes}")
    print(f"  Rounds per episode: {config.rounds_per_episode}")
    print(f"  Total rounds: {config.total_rounds}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Reset between episodes: {config.reset_conversation_between_episodes}")
    print()
    
    # Create agents
    print("Initializing agents...")
    agent_0 = OllamaAgent(
        agent_id="agent_0",
        model=config.model_0,
        host=config.host_0,
        temperature=config.temperature,
        system_prompt=SYSTEM_PROMPT
    )
    
    agent_1 = OllamaAgent(
        agent_id="agent_1",
        model=config.model_1,
        host=config.host_1,
        temperature=config.temperature,
        system_prompt=SYSTEM_PROMPT
    )
    
    print("✓ Agents initialized\n")
    
    # Create and play game
    game = EpisodicIPDGame(agent_0, agent_1, config)
    results = game.play_game()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/test_episodic_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Test complete! Results saved to: {output_file}")
    
    # Quick analysis
    print("\n" + "="*80)
    print("QUICK ANALYSIS")
    print("="*80)
    
    for i, episode in enumerate(results['episodes']):
        coop_0 = episode['agent_0']['cooperation_rate'] * 100
        coop_1 = episode['agent_1']['cooperation_rate'] * 100
        score_0 = episode['agent_0']['episode_score']
        score_1 = episode['agent_1']['episode_score']
        
        print(f"\nEpisode {i+1}:")
        print(f"  Agent 0: {score_0:3d} points, {coop_0:5.1f}% cooperation")
        print(f"  Agent 1: {score_1:3d} points, {coop_1:5.1f}% cooperation")
        
        if i > 0:
            prev_coop_0 = results['episodes'][i-1]['agent_0']['cooperation_rate'] * 100
            prev_coop_1 = results['episodes'][i-1]['agent_1']['cooperation_rate'] * 100
            change_0 = coop_0 - prev_coop_0
            change_1 = coop_1 - prev_coop_1
            
            if change_0 > 10 or change_1 > 10:
                print(f"  → Cooperation increased!")
            elif change_0 < -10 or change_1 < -10:
                print(f"  → Cooperation decreased")
    
    print("\n" + "="*80)
    return results


if __name__ == "__main__":
    try:
        results = test_episodic_game()
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
