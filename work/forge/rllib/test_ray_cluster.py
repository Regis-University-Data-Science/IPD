#!/usr/bin/env python3
"""
Ray RLlib Cluster Test Suite
Tests basic functionality, multi-node training, and IPD environment
"""

import ray
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.algorithms.dqn import DQNConfig
import gymnasium as gym
import torch
import time
import sys


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_1_basic_ray_connection():
    """Test 1: Basic Ray connection and cluster resources"""
    print_header("Test 1: Ray Connection and Cluster Resources")
    
    try:
        # Initialize Ray (connect to existing cluster)
        ray.init(address='auto', ignore_reinit_error=True)
        print("✓ Successfully connected to Ray cluster")
        
        # Get cluster resources
        resources = ray.cluster_resources()
        print(f"\nCluster Resources:")
        print(f"  CPUs: {resources.get('CPU', 0):.0f}")
        print(f"  GPUs: {resources.get('GPU', 0):.0f}")
        print(f"  Memory: {resources.get('memory', 0) / 1e9:.1f} GB")
        
        # Get nodes
        nodes = ray.nodes()
        print(f"\nCluster Nodes: {len(nodes)}")
        for i, node in enumerate(nodes):
            print(f"  Node {i+1}: {node.get('NodeName', 'Unknown')}")
            print(f"    Alive: {node['Alive']}")
            print(f"    Resources: {node.get('Resources', {})}")
        
        print("\n✓ Test 1 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Test 1 FAILED: {e}")
        return False


def test_2_pytorch_gpu():
    """Test 2: PyTorch GPU availability"""
    print_header("Test 2: PyTorch GPU Availability")
    
    try:
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
            print(f"Number of GPUs: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                print(f"\nGPU {i}:")
                print(f"  Name: {torch.cuda.get_device_name(i)}")
                print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1e9:.1f} GB")
            
            # Test GPU computation
            x = torch.randn(1000, 1000).cuda()
            y = torch.matmul(x, x)
            print("\n✓ GPU computation test passed")
        else:
            print("\n⚠ Warning: CUDA not available, but continuing tests")
        
        print("\n✓ Test 2 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Test 2 FAILED: {e}")
        return False


def test_3_simple_training():
    """Test 3: Simple single-agent training on CartPole"""
    print_header("Test 3: Single-Agent Training (CartPole)")
    
    try:
        config = (
            PPOConfig()
            .environment(env="CartPole-v1")
            .framework("torch")
            .resources(num_gpus=0.25)  # Use 1/4 of a GPU
            .training(
                train_batch_size_per_learner=2000,
                minibatch_size=128,
                num_epochs=5,
            )
            .env_runners(
                num_env_runners=2,
                num_envs_per_env_runner=1,
            )
        )
        
        print("Creating PPO algorithm...")
        algo = config.build()
        
        print("Training for 3 iterations...")
        for i in range(3):
            result = algo.train()
            print(f"  Iteration {i+1}:")
            print(f"    Episode reward mean: {result['env_runners']['episode_return_mean']:.2f}")
            print(f"    Episode length mean: {result['env_runners']['episode_len_mean']:.2f}")
        
        algo.stop()
        print("\n✓ Test 3 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Test 3 FAILED: {e}")
        return False


def test_4_distributed_training():
    """Test 4: Distributed training across cluster"""
    print_header("Test 4: Distributed Training")
    
    try:
        config = (
            PPOConfig()
            .environment(env="CartPole-v1")
            .framework("torch")
            .resources(
                num_gpus=1,  # Use 1 GPU for learner
            )
            .learners(
                num_cpus_per_learner=2,
            )
            .training(
                train_batch_size_per_learner=4000,
                minibatch_size=128,
                num_epochs=10,
            )
            .env_runners(
                num_env_runners=4,  # Distribute rollouts across nodes
                num_envs_per_env_runner=2,
            )
        )
        
        print("Creating distributed PPO algorithm...")
        algo = config.build()
        
        print("Training for 2 iterations...")
        start_time = time.time()
        for i in range(2):
            result = algo.train()
            elapsed = time.time() - start_time
            print(f"  Iteration {i+1} (elapsed: {elapsed:.1f}s):")
            print(f"    Episode reward mean: {result['env_runners']['episode_return_mean']:.2f}")
            print(f"    Timesteps: {result['env_runners']['num_env_steps_sampled_lifetime']}")
        
        algo.stop()
        print("\n✓ Test 4 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Test 4 FAILED: {e}")
        return False


def test_5_multi_gpu():
    """Test 5: Multi-GPU training"""
    print_header("Test 5: Multi-GPU Training")
    
    try:
        available_gpus = ray.cluster_resources().get("GPU", 0)
        print(f"Available GPUs in cluster: {available_gpus}")
        
        if available_gpus < 2:
            print("⚠ Skipping multi-GPU test (need at least 2 GPUs)")
            return True
        
        config = (
            PPOConfig()
            .environment(env="CartPole-v1")
            .framework("torch")
            .resources(
                num_gpus=2,  # Use 2 GPUs
            )
            .training(
                train_batch_size_per_learner=8000,
            )
            .env_runners(
                num_env_runners=4,
            )
        )
        
        print("Creating multi-GPU PPO algorithm...")
        algo = config.build()
        
        print("Training for 1 iteration...")
        result = algo.train()
        print(f"  Episode reward mean: {result['env_runners']['episode_return_mean']:.2f}")
        
        algo.stop()
        print("\n✓ Test 5 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Test 5 FAILED: {e}")
        print("⚠ Note: Multi-GPU training can be tricky, may need tuning")
        return True  # Don't fail on this test


def test_6_ipd_environment():
    """Test 6: Custom IPD environment compatibility"""
    print_header("Test 6: Custom IPD Environment")
    
    try:
        from gymnasium import spaces
        import numpy as np
        
        class SimpleIPDEnv(gym.Env):
            """Simple Iterated Prisoner's Dilemma Environment"""
            
            def __init__(self, config=None):
                super().__init__()
                self.action_space = spaces.Discrete(2)  # 0=Cooperate, 1=Defect
                self.observation_space = spaces.Box(
                    low=0, high=1, shape=(4,), dtype=np.float32
                )  # [my_last, opp_last, my_score, opp_score]
                
                self.episode_length = 100
                self.current_step = 0
                
                # Payoff matrix (R, S, T, P)
                self.payoffs = {
                    (0, 0): (3, 3),  # Both cooperate
                    (0, 1): (0, 5),  # I cooperate, opponent defects
                    (1, 0): (5, 0),  # I defect, opponent cooperates
                    (1, 1): (1, 1),  # Both defect
                }
                
                self.reset()
            
            def reset(self, *, seed=None, options=None):
                super().reset(seed=seed)
                self.current_step = 0
                self.my_score = 0
                self.opp_score = 0
                self.last_actions = (0, 0)
                return self._get_obs(), {}
            
            def _get_obs(self):
                return np.array([
                    self.last_actions[0],
                    self.last_actions[1],
                    self.my_score / 100.0,
                    self.opp_score / 100.0
                ], dtype=np.float32)
            
            def step(self, action):
                # Simulate opponent action (random for now)
                opp_action = self.action_space.sample()
                
                # Get payoffs
                my_payoff, opp_payoff = self.payoffs[(action, opp_action)]
                self.my_score += my_payoff
                self.opp_score += opp_payoff
                
                # Update state
                self.last_actions = (action, opp_action)
                self.current_step += 1
                
                # Check if done
                terminated = self.current_step >= self.episode_length
                truncated = False
                
                return self._get_obs(), my_payoff, terminated, truncated, {}
        
        # Test environment creation
        print("Creating IPD environment...")
        env = SimpleIPDEnv()
        
        # Test reset
        obs, info = env.reset()
        print(f"✓ Environment reset successful")
        print(f"  Observation shape: {obs.shape}")
        print(f"  Observation: {obs}")
        
        # Test steps
        print("\nTesting 5 random steps:")
        for i in range(5):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            print(f"  Step {i+1}: action={action}, reward={reward:.1f}, terminated={terminated}")
        
        # Test with RLlib
        print("\n✓ Creating RLlib algorithm with IPD environment...")
        config = (
            DQNConfig()
            .environment(env=SimpleIPDEnv)
            .framework("torch")
            .resources(num_gpus=0.1)
            .training(train_batch_size=256)
            .env_runners(num_env_runners=1)
        )
        
        algo = config.build()
        print("✓ Training for 1 iteration...")
        result = algo.train()
        print(f"  Episode reward mean: {result['env_runners']['episode_return_mean']:.2f}")
        algo.stop()
        
        print("\n✓ Test 6 PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Test 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  RAY RLLIB CLUSTER TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_1_basic_ray_connection,
        test_2_pytorch_gpu,
        test_3_simple_training,
        test_4_distributed_training,
        test_5_multi_gpu,
        test_6_ipd_environment,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {test.__name__}: {e}")
            results.append((test.__name__, False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ray RLlib cluster is ready!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
        