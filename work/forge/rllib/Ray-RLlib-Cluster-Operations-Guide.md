# Ray RLlib Cluster Operations Guide

## Overview

This guide describes how to manage the five-machine Ray RLlib cluster for distributed reinforcement learning consisting of:

- **Nickel** - 3x NVIDIA TITAN X Pascal (34GB total VRAM) - Worker
- **Zinc** - 2x NVIDIA GeForce GTX 1080 Ti (22GB total VRAM) - Worker  
- **Copper** - 1x NVIDIA TITAN X Pascal (12GB VRAM) - Worker
- **Iron** - 1x NVIDIA TITAN X Pascal (12GB VRAM) - Worker
- **Platinum** - 1x NVIDIA GTX 1660 (6GB VRAM) - **Head Node**

**Total Resources:** 8 GPUs, ~90GB VRAM, 751GB RAM

All cluster management commands should be run from **Platinum** (the head node).

## Prerequisites

- SSH access to all five machines configured with key-based authentication
- Dedicated virtual environments at `~/venvs/rllib/` on each machine
- Tailscale VPN for secure inter-node communication (platinum at `100.116.129.84`)
- Management scripts located in `~/work/forge/rllib/` on Platinum

## Cluster Architecture

- **Head Node (Platinum):** Runs Ray dashboard, coordinates distributed training, manages cluster state
- **Worker Nodes (Nickel, Zinc, Copper, Iron):** Execute parallel rollouts, run environment simulations
- **Network:** Tailscale VPN ensures secure inter-node communication
- **Communication:** Ray uses port 6379 for Redis coordination, 8265 for dashboard

## Basic Operations

### Starting the Cluster

To start the entire Ray RLlib cluster:

```bash
cd ~/work/forge/rllib
./manage_ray_cluster.sh start
```

**What happens:**

1. Starts Ray head node on platinum with dashboard
2. Generates secure Redis password for cluster communication
3. Saves connection configuration to `/tmp/ray_cluster_config.sh`
4. Distributes configuration to all worker nodes via SSH
5. Starts Ray worker processes on nickel, zinc, copper, and iron
6. Workers automatically connect to head node and register their GPUs

**Expected output:**

```
=== Starting Ray RLlib Cluster ===

===================================
Starting Ray Head Node on platinum
===================================
...
✓ Head node started successfully
✓ Configuration saved to /tmp/ray_cluster_config.sh
ℹ Dashboard available at: http://100.116.129.84:8265

===================================
Starting Worker Nodes
===================================

ℹ Starting worker on nickel...
Worker started on nickel with 3 GPUs
✓ nickel connected

ℹ Starting worker on zinc...
Worker started on zinc with 2 GPUs
✓ zinc connected
...

===================================
Cluster Startup Complete
===================================

Cluster ready!

Dashboard: http://100.116.129.84:8265
```

**Startup time:** Approximately 30-60 seconds for all nodes to connect.

### Stopping the Cluster

To cleanly shut down the entire cluster:

```bash
cd ~/work/forge/rllib
./manage_ray_cluster.sh stop
```

**What happens:**

1. Stops Ray worker processes on nickel, zinc, copper, and iron
2. Stops Ray head node on platinum
3. Frees all GPU and system memory
4. Cleans up temporary configuration files

**Expected output:**

```
=== Stopping Ray RLlib Cluster ===

Stopping worker nodes...
  Stopping nickel... ✓ stopped
  Stopping zinc... ✓ stopped
  Stopping copper... ✓ stopped
  Stopping iron... ✓ stopped

Stopping head node on platinum...
✓ Head node stopped

✓ Cluster shutdown complete.
```

**Note:** You may see a message like "Stopped only 5 out of 6 Ray processes" - this indicates one process was forcefully terminated after timeout, which is expected Ray behavior.

### Checking Cluster Status

To view the current state of the cluster:

```bash
cd ~/work/forge/rllib
./manage_ray_cluster.sh status
```

**What it shows:**

- Number of active nodes
- Total GPUs and CPU cores available
- Memory resources across cluster
- Running jobs and resource allocation
- Node health status

**Example output:**

```
=== Ray RLlib Cluster Status ===

======== Autoscaler status: 2024-12-15 10:30:45 ========
Node status
---------------------------------------------------------------
Healthy:
 1 node_100.116.129.84    # platinum (head)
 1 node_100.x.x.x         # nickel
 1 node_100.x.x.x         # zinc
 1 node_100.x.x.x         # copper
 1 node_100.x.x.x         # iron

Resources
---------------------------------------------------------------
 Total Resources: 8.0/8.0 GPU, 40.0/40.0 CPU, 180.0/200.0 GiB memory
 
 Usage:
  0.0/8.0 GPU
  0.0/40.0 CPU
  0.0 GiB/200.0 GiB memory
```

### Accessing the Ray Dashboard

The Ray Dashboard provides real-time visualization of cluster activity:

**URL:** http://100.116.129.84:8265

**Dashboard Features:**

- **Jobs:** View running and completed training experiments
- **Actors:** Monitor actor lifecycle and resource usage  
- **Metrics:** Real-time CPU, GPU, and memory utilization graphs
- **Logs:** Access logs from all cluster nodes
- **Node Status:** Per-node health and resource availability
- **Task Timeline:** Visualize task execution across workers

### Restarting the Cluster

To restart the entire cluster (useful for applying updates or recovering from issues):

```bash
cd ~/work/forge/rllib
./manage_ray_cluster.sh restart
```

This performs a clean stop followed by a fresh start.

## Understanding Status Output

### Node Status

- **Healthy** - Node is connected and accepting work
- **Idle** - Node connected but not currently processing tasks  
- **Dead** - Node disconnected or unreachable

### Resource Metrics

- **GPU:** Number of GPUs available/total
  - Example: `3.0/8.0` means 3 GPUs in use, 5 available
- **CPU:** CPU cores available for computation
- **Memory:** System RAM available across cluster

### Running Jobs

When experiments are active, status shows:
- Job name and duration
- Resource allocation per job
- Progress indicators

## Running Training Experiments

### Basic Single-Agent Training

Create a training script (e.g., `train_cartpole.py`):

```python
import ray
from ray.rllib.algorithms.ppo import PPOConfig

# Connect to existing cluster
ray.init(address='auto')

# Configure PPO training
config = (
    PPOConfig()
    .environment(env="CartPole-v1")
    .framework("torch")
    .resources(
        num_gpus=1,  # 1 GPU for learner
    )
    .rollouts(
        num_rollout_workers=4,  # 4 parallel workers
        num_envs_per_env_runner=2,
    )
    .training(
        train_batch_size=4000,
        sgd_minibatch_size=256,
    )
)

# Build and train
algo = config.build()
for i in range(100):
    result = algo.train()
    print(f"Iteration {i}: reward={result['env_runners']['episode_return_mean']:.2f}")

algo.stop()
ray.shutdown()
```

Run the training:

```bash
cd ~/work/forge/rllib
source ~/venvs/rllib/bin/activate
python train_cartpole.py
```

### Multi-Agent Training (IPD Example)

For Iterated Prisoner's Dilemma or other multi-agent scenarios:

```python
import ray
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.multi_agent_env import MultiAgentEnv

# Connect to cluster
ray.init(address='auto')

# Configure multi-agent training
config = (
    PPOConfig()
    .environment(env=YourIPDEnvironment)
    .multi_agent(
        policies={"agent_0", "agent_1"},
        policy_mapping_fn=lambda agent_id, *args, **kwargs: agent_id,
    )
    .resources(num_gpus=1)
    .rollouts(num_rollout_workers=8)
)

algo = config.build()
for i in range(1000):
    result = algo.train()
    if i % 100 == 0:
        algo.save_checkpoint(f"/tmp/checkpoint_{i}")
        
algo.stop()
ray.shutdown()
```

### Resource Allocation Strategies

**Strategy 1: Maximize Parallel Rollouts**

Best for: Environment simulation is the bottleneck

```python
config.resources(num_gpus=0.25)  # 0.25 GPU per worker = 4 workers per GPU
config.rollouts(num_rollout_workers=16)  # Distributed across cluster
```

**Strategy 2: GPU-Intensive Training**

Best for: Complex neural networks, large batch sizes

```python
config.resources(num_gpus=2)  # 2 GPUs dedicated to learner
config.rollouts(num_rollout_workers=4)  # Fewer workers
```

**Strategy 3: Balanced Hybrid**

Best for: Both training and rollouts need GPU acceleration

```python
config.resources(num_gpus=1)  # 1 GPU for learner
config.rollouts(
    num_rollout_workers=8,  # Distributed rollouts
    num_gpus_per_env_runner=0.5,  # Share GPUs for rollouts
)
```

## Troubleshooting

### Cluster Won't Start

**Check if Ray processes are still running:**

```bash
# On platinum
ray status

# If stuck, force stop
ray stop
./manage_ray_cluster.sh start
```

**Check network connectivity to workers:**

```bash
# From platinum
for node in nickel zinc copper iron; do
    echo "Testing $node..."
    ssh dhart@$node "echo 'Connected to $node'"
done
```

### Worker Not Connecting

**Check Ray logs on the problem worker:**

```bash
ssh dhart@<hostname>
source ~/venvs/rllib/bin/activate
cat /tmp/ray/session_latest/logs/raylet.out
```

**Manually restart the worker:**

```bash
# On the worker node
source ~/venvs/rllib/bin/activate
ray stop

# Get Redis password from platinum:/tmp/ray_cluster_config.sh
ray start --address='100.116.129.84:6379' --redis-password='<password>'
```

**Or restart from platinum:**

```bash
./manage_ray_cluster.sh restart
```

### Out of GPU Memory

**Symptoms:**
- Training crashes with CUDA out of memory errors
- Dashboard shows GPU memory at 100%

**Solutions:**

1. **Reduce batch size:**
   ```python
   config.training(
       train_batch_size=2000,  # Reduced from 4000
       sgd_minibatch_size=128,  # Reduced from 256
   )
   ```

2. **Use fractional GPUs:**
   ```python
   config.resources(num_gpus=0.5)  # Use half GPU instead of full
   ```

3. **Reduce number of parallel workers:**
   ```python
   config.rollouts(num_rollout_workers=4)  # Reduced from 8
   ```

**Check current GPU usage:**

```bash
# On specific machine
ssh dhart@<hostname> "nvidia-smi"

# Or from dashboard: http://100.116.129.84:8265
```

### Dashboard Not Accessible

**Check if head node is running:**

```bash
./manage_ray_cluster.sh status
```

**Verify dashboard port:**

```bash
netstat -tlnp | grep 8265
```

**If needed, restart cluster:**

```bash
./manage_ray_cluster.sh restart
```

### Training Job Hangs

**Common causes:**
- Requesting more resources than available
- Deadlock from improper resource allocation
- Network connectivity issues between nodes

**Diagnostic steps:**

1. **Check resource availability:**
   ```bash
   ray status  # Look for available GPUs/CPUs
   ```

2. **Check logs:**
   ```bash
   tail -f /tmp/ray/session_latest/logs/monitor.log
   ```

3. **Kill and restart:**
   ```bash
   ./manage_ray_cluster.sh restart
   # Then reduce resource requirements in your training config
   ```

## Virtual Environment Management

Each machine has a dedicated RLlib virtual environment at `~/venvs/rllib/`.

### Activating Environment

```bash
source ~/venvs/rllib/bin/activate
```

### Checking Installed Packages

```bash
source ~/venvs/rllib/bin/activate
pip list | grep -E "ray|torch|gymnasium"
```

### Updating Ray RLlib

**On all machines (from platinum):**

```bash
for node in platinum nickel zinc copper iron; do
    echo "Updating $node..."
    ssh dhart@$node "source ~/venvs/rllib/bin/activate && pip install --upgrade ray[rllib]"
done
```

**After updating, restart cluster:**

```bash
./manage_ray_cluster.sh restart
```

## Performance Optimization

### 1. Maximize GPU Utilization

- Use `ray status` and dashboard to monitor GPU usage
- Adjust `num_gpus` and `num_gpus_per_env_runner` to fill available GPUs
- Aim for 80-95% GPU utilization during training

### 2. Balance Rollouts vs Training

- **More workers** = more data collection, better sample efficiency
- **Fewer workers** = more training throughput
- Find optimal ratio for your specific environment

### 3. Batch Size Tuning

- **Larger batches** = better GPU utilization, more stable gradients
- **Smaller batches** = more frequent updates, faster iteration
- Constrained by GPU memory

### 4. Network Efficiency

- Keep data transfer between nodes minimal
- Use local storage for checkpoints when possible
- Monitor network utilization in dashboard

## Monitoring and Logging

### Real-Time Monitoring

```bash
# Watch cluster status continuously
watch -n 2 'ray status'
```

### Access Logs

```bash
# View head node logs
tail -f /tmp/ray/session_latest/logs/monitor.log

# View worker logs
ssh dhart@<hostname> "tail -f /tmp/ray/session_latest/logs/raylet.out"
```

### Training Metrics

Ray Dashboard provides real-time metrics. For additional logging:

```python
config.debugging(log_level="INFO")
config.reporting(
    metrics_num_episodes_for_smoothing=10,
    min_sample_timesteps_per_iteration=1000,
)
```

## Configuration Files

### Cluster Configuration

**Location:** `/tmp/ray_cluster_config.sh` (on platinum)

**Contents:**
- Redis address and port
- Redis password for cluster authentication  
- Generated automatically on cluster start
- Distributed to worker nodes by management script

### Example Configuration

```bash
# Ray Cluster Configuration
# Generated on Sun Dec 15 08:45:23 MST 2024
export RAY_HEAD_IP="100.116.129.84"
export RAY_PORT=6379
export RAY_REDIS_PASSWORD="a1b2c3d4e5f6..."
export RAY_ADDRESS="100.116.129.84:6379"
```

## Usage Recommendations

### For Daily Use

1. Start cluster at beginning of work session
2. Check status before launching experiments
3. Monitor dashboard during training
4. Stop cluster when finished to free resources

### For Long-Running Experiments

1. Use checkpointing to save progress regularly
2. Monitor GPU memory and temperature
3. Set up logging for overnight runs
4. Leverage Ray's fault tolerance features

### For Multi-User Environment

1. Check cluster status before starting jobs
2. Coordinate resource usage with other users
3. Use appropriate resource fractions to avoid conflicts
4. Clean up completed jobs to free resources

### For Development Workflow

1. Test on single machine first
2. Verify with small-scale distributed test
3. Scale up to full cluster for production runs
4. Monitor resource utilization and adjust

## Quick Reference

```bash
# Start cluster
cd ~/work/forge/rllib && ./manage_ray_cluster.sh start

# Check status
cd ~/work/forge/rllib && ./manage_ray_cluster.sh status

# Access dashboard
# Open browser to: http://100.116.129.84:8265

# Stop cluster
cd ~/work/forge/rllib && ./manage_ray_cluster.sh stop

# Restart cluster
cd ~/work/forge/rllib && ./manage_ray_cluster.sh restart

# Activate environment
source ~/venvs/rllib/bin/activate

# Check GPU usage on specific machine
ssh dhart@<hostname> "nvidia-smi"

# View Ray logs
tail -f /tmp/ray/session_latest/logs/monitor.log

# Check cluster resources from Python
python -c "import ray; ray.init(address='auto'); print(ray.cluster_resources())"
```

## Common Training Patterns

### Pattern 1: Single-Agent RL

```python
import ray
from ray.rllib.algorithms.ppo import PPOConfig

ray.init(address='auto')

config = (
    PPOConfig()
    .environment(env="CartPole-v1")
    .resources(num_gpus=1)
    .rollouts(num_rollout_workers=8)
)

algo = config.build()
for i in range(100):
    result = algo.train()
    print(f"Episode {i}: {result['env_runners']['episode_return_mean']:.2f}")
    
algo.stop()
ray.shutdown()
```

### Pattern 2: Multi-Agent RL with Self-Play

```python
import ray
from ray.rllib.algorithms.ppo import PPOConfig

ray.init(address='auto')

config = (
    PPOConfig()
    .environment(env=IPDEnvironment)
    .multi_agent(
        policies={"agent_0", "agent_1"},
        policy_mapping_fn=lambda agent_id, *args, **kwargs: agent_id,
    )
    .resources(num_gpus=1)
    .rollouts(num_rollout_workers=8)
)

algo = config.build()
for i in range(1000):
    result = algo.train()
    if i % 100 == 0:
        checkpoint = algo.save_checkpoint(f"/tmp/ipd_checkpoint_{i}")
        print(f"Checkpoint {i} saved to {checkpoint}")
        
algo.stop()
ray.shutdown()
```

### Pattern 3: Hyperparameter Tuning

```python
import ray
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig

ray.init(address='auto')

config = (
    PPOConfig()
    .environment(env="CartPole-v1")
    .resources(num_gpus=0.5)  # Share GPUs across trials
)

tune.run(
    "PPO",
    config=config.to_dict(),
    param_space={
        "lr": tune.grid_search([0.001, 0.0001]),
        "gamma": tune.grid_search([0.95, 0.99]),
    },
    num_samples=4,  # 4 trials per configuration
    stop={"training_iteration": 100},
)

ray.shutdown()
```

## Network Access

All machines are accessible via Tailscale VPN:
- Head node (platinum) at `100.116.129.84`
- Only accessible to users with Tailscale credentials
- Dashboard: `http://100.116.129.84:8265`
- Redis communication on port 6379

## Support

For issues or questions:
- Check troubleshooting section above
- Review Ray logs: `cat /tmp/ray/session_latest/logs/monitor.log`
- Check Ray documentation: https://docs.ray.io/en/latest/rllib/
- Contact cluster administrator: dhart@regis.edu

---

**Last Updated:** December 2024  
**Ray Version:** 2.x with RLlib  
**Cluster Configuration:** 5 nodes, 8 GPUs, Tailscale VPN
