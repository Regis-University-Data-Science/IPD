# FORGE Ray/RLlib Personal Environment Setup Guide
**For Students - Regis University GENESIS Project**  
**Last Updated:** December 23, 2025

---

## Overview

You will create your own Ray/RLlib environment in your home directory for running reinforcement learning experiments. This is the **RL baseline** for the GENESIS project - comparing traditional RL agents to LLM agents.

**Note:** This is typically set up after you're comfortable with the LLM experiments.

---

## Part 1: Initial Setup (30 minutes)

### Step 1: Copy the RLlib Code

```bash
# If you haven't already created the forge workspace
mkdir -p ~/work/forge
cd ~/work/forge

# Copy the RLlib implementation
cp -r /home/dhart/work/forge/rllib ~/work/forge/

# Verify
ls -la ~/work/forge/rllib/
```

### Step 2: Set Up Python Virtual Environment

```bash
# Navigate to the RLlib directory
cd ~/work/forge/rllib

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install Ray and dependencies
pip install ray[rllib] torch numpy gymnasium

# This may take several minutes - Ray is a large package
```

**Note:** Ray installation can be 500MB+. Be patient.

### Step 3: Test Ray Cluster Connection

```bash
# Still in ~/work/forge/rllib with .venv activated

# Check if Ray cluster is running
~/work/forge/rllib/manage_ray_cluster.sh status

# Test connection with simple script
python test_ray_cluster.py
```

**Expected output:**
```
Connected to Ray cluster
Cluster resources: {'CPU': 128, 'GPU': 8, ...}
✅ Ray cluster is accessible
```

---

## Part 2: Understanding Ray Cluster Architecture

### Shared Ray Cluster
Unlike Ollama (which is always running), the Ray cluster:
- Is started/stopped as needed
- Runs as a shared resource managed centrally
- Requires one "head node" and multiple "worker nodes"

### Cluster Management
**Doug or designated coordinator manages:**
- Starting the Ray head node (on platinum)
- Starting Ray worker nodes (on other machines)
- Stopping the cluster when not in use

**You submit jobs to the running cluster.**

### Your Personal Environment
Your RLlib code and results are in `~/work/forge/rllib/`, but the actual computation happens on the shared Ray cluster.

---

## Part 3: Running Your First RL Experiment

### Check Cluster Status

```bash
# Make sure cluster is running
~/work/forge/rllib/manage_ray_cluster.sh status

# If not running, coordinate with Doug to start it
# (or you may have permission to start it yourself)
```

### Run the IPD Training Example

```bash
cd ~/work/forge/rllib/IPD-Two-Agents
source ../.venv/bin/activate

# Run training for 50 iterations (shorter test)
python train_ipd_example.py --iterations 50

# Or full training (100 iterations, ~1-2 hours)
python train_ipd_example.py --iterations 100
```

**What happens:**
- Script connects to Ray cluster
- Distributes training across worker nodes
- Periodically saves checkpoints
- Shows progress every few iterations
- Final cooperation rate reported

**Expected output:**
```
Connected to Ray cluster
Cluster resources: {...}

Building PPO algorithm...

Starting training for 50 iterations...
================================================================================

Iteration   0:
  Agent 0 reward:   45.23
  Agent 1 reward:   43.87
  Episode length:  100.00
  Cooperation rate (est): 15.0%
  ...

Iteration  45:
  Agent 0 reward:  285.12
  Agent 1 reward:  287.45
  Episode length:  100.00
  Cooperation rate (est): 95.2%
  🎯 New best cooperation rate: 95.2%
  
================================================================================
Training Complete!
Best cooperation rate achieved: 95.2%
================================================================================
```

### Analyze RL Results

Unlike LLM experiments, RL agents can't explain their reasoning. You'll analyze:
- Training curves (cooperation rate over iterations)
- Final policy behavior
- Convergence speed
- Stability of cooperation

---

## Part 4: Coordination Protocol

### Ray Cluster is More Constrained

**Key differences from Ollama:**
- Ray cluster uses ALL machines when running
- More expensive to start/stop
- Typically left running during a work session
- Takes 5-10 minutes to restart if stopped

### Before Starting RL Experiments

**1. Check if cluster is running:**
```bash
~/work/forge/rllib/manage_ray_cluster.sh status
```

**2. Check communication channel:**
- Is someone running a long job?
- Is cluster scheduled for maintenance?

**3. Estimate your job duration:**
- 50 iterations: ~30-60 minutes
- 100 iterations: ~1-2 hours
- 200+ iterations: ~3-4 hours

**4. Announce your job:**
- "Starting 100-iteration RL training, ~2 hours"
- Include estimated completion time

**5. When finished:**
- "RL training complete, cluster free"

### If Multiple People Need Ray

**Option 1: Sequential**
- Person A runs job (2 hours)
- Person B runs next job (2 hours)
- Schedule in advance

**Option 2: Time-sharing**
- Morning: Person A
- Afternoon: Person B
- Coordinate on shared calendar

**Option 3: Background jobs**
- Submit long jobs to run overnight
- Requires additional setup (screen/tmux or batch system)

---

## Part 5: Common RL Experiment Types

### Basic Training

**Short test (50 iterations):**
```bash
python train_ipd_example.py --iterations 50
```

**Standard run (100 iterations):**
```bash
python train_ipd_example.py --iterations 100
```

**Long run (200 iterations):**
```bash
python train_ipd_example.py --iterations 200
```

### Checkpointing

The training script automatically saves checkpoints:
```
~/work/forge/rllib/IPD-Two-Agents/checkpoints/
  checkpoint_000010/
  checkpoint_000020/
  ...
```

**To resume from checkpoint (if implemented):**
```bash
python train_ipd_example.py --resume checkpoint_000050
```

### Testing Trained Policies

After training, you can evaluate the learned policies:
```bash
python test_ipd_example.py --checkpoint path/to/checkpoint
```

This runs the trained agents without learning to see stable behavior.

---

## Part 6: Comparing RL vs. LLM Results

### Your Research Goal
Compare two paths to cooperation:

**RL Agents (this environment):**
- Learn through value functions and gradient descent
- No explicit reasoning
- Optimize numerical rewards
- Training takes hours

**LLM Agents (~/work/forge/llm):**
- Reason through natural language
- Can explain decisions
- Discover cooperation through reflection
- Immediate (no training), but slower per round

### Key Metrics to Compare

**Cooperation emergence:**
- RL: Track cooperation rate over training iterations
- LLM: Track cooperation rate over game rounds

**Final performance:**
- Do both converge to mutual cooperation?
- Which is more stable?

**Efficiency:**
- RL: How many training iterations to convergence?
- LLM: How many rounds to discover cooperation?

**Explainability:**
- RL: Cannot explain why it cooperates (just learned policy)
- LLM: Provides reasoning and post-game reflections

### Document Both

Create parallel experiment logs:
- `~/work/forge/rllib/my_rl_experiments.md`
- `~/work/forge/llm/my_llm_experiments.md`

Compare findings for GENESIS paper.

---

## Part 7: Troubleshooting Ray Issues

### Ray Cluster Not Responding

**Problem:** "Cannot connect to Ray cluster"
```bash
# Check status
~/work/forge/rllib/manage_ray_cluster.sh status

# If down, coordinate with Doug to restart
# or restart yourself if you have permissions:
~/work/forge/rllib/manage_ray_cluster.sh stop
~/work/forge/rllib/manage_ray_cluster.sh start
```

### Training Crashes

**Problem:** Training stops with error
```bash
# Common issues:
# - Out of GPU memory (reduce batch size or workers)
# - Network issues between nodes
# - Worker node failed

# Check Ray logs
~/work/forge/rllib/manage_ray_cluster.sh logs
```

**Solution:** 
- Restart from last checkpoint
- Reduce resource requirements
- Check with Doug if node issues

### Very Slow Training

**Problem:** Training taking much longer than expected

```bash
# Check if someone else is also using cluster
# (Ray can handle multiple jobs, but slows down)

# Check resource allocation in your script
# May need to adjust num_workers or GPUs
```

### Virtual Environment Issues

**Problem:** Ray not installed or import errors
```bash
cd ~/work/forge/rllib
source .venv/bin/activate
pip install ray[rllib] torch numpy gymnasium --force-reinstall
```

---

## Part 8: Advanced Topics (Optional)

### Custom Environment Modifications

The IPD environment is in:
```python
~/work/forge/rllib/IPD-Two-Agents/train_ipd_example.py
```

You can modify:
- Observation space (what agents see)
- Episode length (rounds per game)
- Payoff matrix (different game dynamics)
- Training hyperparameters (learning rate, etc.)

**Warning:** Changes require understanding RL fundamentals.

### Tensorboard Monitoring

Ray/RLlib can log to Tensorboard:
```bash
# Start tensorboard (in a separate terminal)
tensorboard --logdir ~/ray_results

# Open browser to: http://localhost:6006
# View real-time training curves
```

### Experiment Tracking

Consider organizing experiments:
```bash
~/work/forge/rllib/experiments/
  experiment_001_baseline/
    train_output.txt
    checkpoints/
    results.json
  experiment_002_longer_episodes/
    ...
```

---

## Part 9: Best Practices for RL Experiments

### Before Starting

```bash
# 1. Activate environment
cd ~/work/forge/rllib/IPD-Two-Agents
source ../.venv/bin/activate

# 2. Check Ray cluster
~/work/forge/rllib/manage_ray_cluster.sh status

# 3. Estimate runtime
# 100 iterations ≈ 1-2 hours

# 4. Coordinate with others
# Post in channel: "Starting RL training, ~2 hours"
```

### During Training

- ✅ Monitor progress (prints every few iterations)
- ✅ Don't interrupt unless necessary (wastes computation)
- ✅ Take notes on training behavior
- ✅ Save interesting checkpoints

### After Training

- ✅ Document final cooperation rate
- ✅ Save important checkpoints
- ✅ Compare to previous runs
- ✅ Release cluster (post in channel)

---

## Part 10: Ray vs. Ollama Comparison

| Aspect | Ollama Cluster | Ray Cluster |
|--------|----------------|-------------|
| **Always on?** | Yes | No (started as needed) |
| **Startup time** | Instant (models loaded) | 5-10 minutes |
| **Job duration** | 10-30 minutes typical | 1-4 hours typical |
| **Isolation** | Multiple users, no conflict | Shared resources |
| **Coordination** | Lightweight (check status) | Heavier (schedule time) |
| **Interruption cost** | Low (restart quickly) | High (wastes training) |

**General guideline:**
- Ollama: Can run many small experiments easily
- Ray: Schedule longer blocks for training runs

---

## Quick Reference Card

```bash
# SETUP (do once)
cd ~/work/forge/rllib
python3 -m venv .venv
source .venv/bin/activate
pip install ray[rllib] torch numpy gymnasium

# BEFORE EACH SESSION
cd ~/work/forge/rllib/IPD-Two-Agents
source ../.venv/bin/activate
~/work/forge/rllib/manage_ray_cluster.sh status

# RUN TRAINING
# [coordinate in channel: "Starting RL job, 2 hours"]
python train_ipd_example.py --iterations 100
# [when done: "RL training complete"]

# CHECK RESULTS
ls ~/ray_results/  # Training logs and checkpoints

# HELP
cat ~/work/forge/rllib/README.md
# or ask in #forge-cluster channel
```

---

## Appendix: RL Background (Brief)

### What is Reinforcement Learning?

Agents learn through trial and error:
1. Observe environment state
2. Take action
3. Receive reward
4. Update policy to maximize future rewards

### How RL Agents Learn Cooperation

In IPD:
- Early: Random exploration (mixed cooperation/defection)
- Middle: Discover cooperation patterns yield higher rewards
- Late: Converge to mutual cooperation strategy

**Key: They optimize rewards, not reasoning about morality.**

### Comparing to LLM Agents

**RL agents:**
- ✅ Learn optimal policies through experience
- ❌ Cannot explain their reasoning
- ✅ Very efficient once trained
- ❌ Require long training time

**LLM agents:**
- ✅ Can explain reasoning in natural language
- ❌ May not discover optimal strategy
- ✅ Immediate (no training needed)
- ❌ Slower per decision

**Both paths to cooperation reveal different aspects of intelligence.**

---

## Next Steps

### Week 1-2: Focus on LLM experiments
Get comfortable with the system using Ollama/LLM experiments first.

### Week 3-4: Start RL experiments
Once you understand IPD dynamics from LLM side, run RL baseline.

### Week 5+: Systematic comparison
Compare RL and LLM approaches:
- Convergence patterns
- Final cooperation rates
- Stability
- Explainability

**This comparison is the heart of GENESIS research.**

---

## Resources

**Your workspace:**
- `~/work/forge/rllib/IPD-Two-Agents/`
- `~/work/forge/rllib/manage_ray_cluster.sh`

**Doug's reference:**
- `/home/dhart/work/forge/rllib/`

**Ray documentation:**
- https://docs.ray.io/en/latest/rllib/index.html

**Questions:**
- Ask Doug
- Ask in #forge-cluster
- Pair with other students

---

**Ready to compare RL and LLM paths to cooperation! 🤖**
