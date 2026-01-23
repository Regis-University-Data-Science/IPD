#!/usr/bin/env python3
"""
Example: Training Two Agents on Iterated Prisoner's Dilemma
Uses Ray RLlib on the cluster
"""

import ray
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple
import argparse


class IteratedPrisonersDilemmaEnv(MultiAgentEnv):
    """
    Multi-Agent Iterated Prisoner's Dilemma Environment
    
    Two agents play IPD for a fixed number of rounds.
    Actions: 0 = Cooperate, 1 = Defect
    
    Payoff Matrix:
              Cooperate  Defect
    Cooperate   (3,3)    (0,5)
    Defect      (5,0)    (1,1)
    """
    
    def __init__(self, config=None):
        super().__init__()
        
        config = config or {}
        self.episode_length = config.get("episode_length", 100)
        self.history_length = config.get("history_length", 10)
        
        # Agent IDs
        self.agents = ["agent_0", "agent_1"]
        self._agent_ids = set(self.agents)
        
        # Action space: 0=Cooperate, 1=Defect
        self.action_space = spaces.Discrete(2)
        
        # Observation space: history of last N rounds + current scores
        # [my_actions (N), opp_actions (N), my_score, opp_score, round_num]
        obs_size = 2 * self.history_length + 3
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(obs_size,), dtype=np.float32
        )
        
        # Payoff matrix
        self.payoffs = {
            (0, 0): (3, 3),  # Both cooperate
            (0, 1): (0, 5),  # I cooperate, opponent defects
            (1, 0): (5, 0),  # I defect, opponent cooperates
            (1, 1): (1, 1),  # Both defect
        }
        
        self.reset()
    
    def reset(self, *, seed=None, options=None):
        """Reset the environment"""
        super().reset(seed=seed)
        
        self.current_round = 0
        self.scores = {agent: 0 for agent in self.agents}
        self.history = {agent: [] for agent in self.agents}
        
        # Return initial observations
        obs = {agent: self._get_obs(agent) for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        
        return obs, infos
    
    def _get_obs(self, agent_id: str) -> np.ndarray:
        """Get observation for an agent"""
        opponent_id = "agent_1" if agent_id == "agent_0" else "agent_0"
        
        # Get recent history (padded with zeros if needed)
        my_history = self.history[agent_id][-self.history_length:]
        opp_history = self.history[opponent_id][-self.history_length:]
        
        # Pad if necessary
        my_history = [0] * (self.history_length - len(my_history)) + my_history
        opp_history = [0] * (self.history_length - len(opp_history)) + opp_history
        
        # Normalize scores
        max_score = 5 * self.episode_length  # Maximum possible score
        my_score_norm = self.scores[agent_id] / max_score
        opp_score_norm = self.scores[opponent_id] / max_score
        round_norm = self.current_round / self.episode_length
        
        # Concatenate observation
        obs = np.array(
            my_history + opp_history + [my_score_norm, opp_score_norm, round_norm],
            dtype=np.float32
        )
        
        return obs
    
    def step(self, action_dict: Dict[str, int]) -> Tuple:
        """Execute one round of the game"""
        
        # Get actions
        action_0 = action_dict["agent_0"]
        action_1 = action_dict["agent_1"]
        
        # Calculate payoffs
        payoff_0, payoff_1 = self.payoffs[(action_0, action_1)]
        
        # Update scores
        self.scores["agent_0"] += payoff_0
        self.scores["agent_1"] += payoff_1
        
        # Update history
        self.history["agent_0"].append(action_0)
        self.history["agent_1"].append(action_1)
        
        # Update round counter
        self.current_round += 1
        
        # Check if episode is done
        terminated = self.current_round >= self.episode_length
        truncated = False
        
        # Prepare outputs
        observations = {agent: self._get_obs(agent) for agent in self.agents}
        rewards = {"agent_0": payoff_0, "agent_1": payoff_1}
        terminateds = {agent: terminated for agent in self.agents}
        terminateds["__all__"] = terminated
        truncateds = {agent: truncated for agent in self.agents}
        truncateds["__all__"] = truncated
        infos = {agent: {} for agent in self.agents}
        
        return observations, rewards, terminateds, truncateds, infos


def train_ipd(num_iterations: int = 100, checkpoint_freq: int = 10):
    """Train two agents on IPD using PPO"""
    
    # Initialize Ray
    ray.init(address='auto', ignore_reinit_error=True)
    print("Connected to Ray cluster")
    print(f"Cluster resources: {ray.cluster_resources()}")
    
    # Configure PPO for multi-agent training
    config = (
        PPOConfig()
        .environment(
            env=IteratedPrisonersDilemmaEnv,
            env_config={
                "episode_length": 100,
                "history_length": 10,
            }
        )
        .framework("torch")
        .resources(
            num_gpus=1,  # Use 1 GPU for training
            num_cpus_per_learner_worker=4,
        )
        .training(
            train_batch_size=4000,
            sgd_minibatch_size=256,
            num_sgd_iter=10,
            lr=5e-5,
            gamma=0.99,
            lambda_=0.95,
        )
        .rollouts(
            num_rollout_workers=8,  # Distribute across cluster
            num_envs_per_env_runner=4,
        )
        .multi_agent(
            policies={"policy_0", "policy_1"},
            policy_mapping_fn=lambda agent_id, *args, **kwargs: f"policy_{agent_id[-1]}",
        )
    )
    
    # Build algorithm
    print("\nBuilding PPO algorithm...")
    algo = config.build()
    
    # Training loop
    print(f"\nStarting training for {num_iterations} iterations...")
    print("=" * 80)
    
    best_cooperation_rate = 0
    
    for iteration in range(num_iterations):
        result = algo.train()
        
        # Extract metrics
        episode_reward_mean_0 = result['env_runners']['policy_reward_mean'].get('policy_0', 0)
        episode_reward_mean_1 = result['env_runners']['policy_reward_mean'].get('policy_1', 0)
        episode_len_mean = result['env_runners']['episode_len_mean']
        
        # Estimate cooperation rate (rough heuristic)
        # If both agents get ~3 per round, they're mostly cooperating
        # If both get ~1 per round, they're mostly defecting
        avg_reward_per_round = (episode_reward_mean_0 + episode_reward_mean_1) / 2 / episode_len_mean
        cooperation_rate = max(0, (avg_reward_per_round - 1) / 2)  # Normalize to 0-1
        
        # Print progress
        if iteration % 5 == 0:
            print(f"\nIteration {iteration:3d}:")
            print(f"  Agent 0 reward: {episode_reward_mean_0:6.2f}")
            print(f"  Agent 1 reward: {episode_reward_mean_1:6.2f}")
            print(f"  Episode length: {episode_len_mean:6.2f}")
            print(f"  Cooperation rate (est): {cooperation_rate:.2%}")
            print(f"  Timesteps: {result['env_runners']['num_env_steps_sampled_lifetime']:,}")
        
        # Track best cooperation
        if cooperation_rate > best_cooperation_rate:
            best_cooperation_rate = cooperation_rate
            print(f"  🎯 New best cooperation rate: {cooperation_rate:.2%}")
        
        # Checkpoint
        if (iteration + 1) % checkpoint_freq == 0:
            checkpoint_path = algo.save()
            print(f"  💾 Checkpoint saved: {checkpoint_path}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("Training Complete!")
    print(f"Best cooperation rate achieved: {best_cooperation_rate:.2%}")
    print("=" * 80)
    
    # Save final model
    final_checkpoint = algo.save()
    print(f"\nFinal model saved: {final_checkpoint}")
    
    algo.stop()
    ray.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Train IPD agents on Ray cluster")
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=100,
        help="Number of training iterations (default: 100)"
    )
    parser.add_argument(
        "--checkpoint-freq",
        type=int,
        default=10,
        help="Checkpoint frequency (default: 10)"
    )
    
    args = parser.parse_args()
    
    train_ipd(
        num_iterations=args.iterations,
        checkpoint_freq=args.checkpoint_freq
    )


if __name__ == "__main__":
    main()

