# FORGE Personal Environment Setup Guide
**For Students - Regis University GENESIS Project**  
**Last Updated:** December 23, 2025

---

## Overview

You will create your own complete FORGE environment in your home directory. This gives you:
- ✅ Full control over your code and experiments
- ✅ Safe space to experiment without affecting others
- ✅ Your own results and modifications
- ✅ Independence to work at your own pace

The Ollama and Ray clusters are shared resources that we coordinate informally.

---

## Part 1: Initial Setup (30 minutes)

### Step 1: Create Your Directory Structure

Open a terminal and run:

```bash
# Create your workspace
mkdir -p ~/work/forge
cd ~/work/forge

# Verify you're in the right place
pwd
# Should show: /home/YOUR_USERNAME/work/forge
```

### Step 2: Copy the FORGE Code

```bash
# Copy the LLM implementation
cp -r /home/dhart/work/forge/llm ~/work/forge/

# Copy the RLlib implementation  
cp -r /home/dhart/work/forge/rllib ~/work/forge/

# Verify the copy
ls -la ~/work/forge/
# You should see: llm/ and rllib/ directories
```

### Step 3: Set Up Python Virtual Environment

```bash
# Navigate to the LLM IPD directory
cd ~/work/forge/llm/IPD-LLM-Agents

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Your prompt should change to show (.venv)

# Install required packages
pip install -r requirements.txt

# This will install: requests, numpy, matplotlib
```

**Note:** You'll need to activate the virtual environment each time you work:
```bash
cd ~/work/forge/llm/IPD-LLM-Agents
source .venv/bin/activate
```

### Step 4: Test Your Setup

```bash
# Still in ~/work/forge/llm/IPD-LLM-Agents with .venv activated

# Run connectivity test
python test_connection.py
```

**Expected output:**
```
============================================================
OLLAMA IPD TEST SUITE
============================================================
Testing decision extraction...
✅ Success! Agent responded:
...
============================================================
✅ All tests passed! System is ready.
============================================================
```

**If you see the success message, you're done with setup!**

---

## Part 2: Running Your First Experiment (15 minutes)

### Quick Test Run (10 rounds, ~2 minutes)

```bash
# Make sure you're in the right directory and venv is active
cd ~/work/forge/llm/IPD-LLM-Agents
source .venv/bin/activate

# Check cluster status first
~/work/forge/llm/status-cluster.sh

# If cluster is available, run a quick test
python ipd_llm_game.py --rounds 10
```

**What you'll see:**
- Progress updates for each round
- Final scores and cooperation rates
- Agent reflections
- Results saved to your `results/` directory

### Analyze Your Results

```bash
# Find your results file
ls results/

# Analyze it
python analyze_results.py results/game_TIMESTAMP.json

# Generate plots
python analyze_results.py results/game_TIMESTAMP.json --plots
```

**Congratulations! You've run your first IPD experiment.**

---

## Part 3: Understanding Your Environment

### Your Directory Structure

```
~/work/forge/
├── llm/
│   ├── IPD-LLM-Agents/          ← Your main working directory
│   │   ├── .venv/               ← Your Python environment (don't edit)
│   │   ├── results/             ← Your experiment results
│   │   ├── ipd_llm_game.py      ← Main experiment script
│   │   ├── analyze_results.py   ← Analysis script
│   │   ├── prompts.py           ← You can modify this!
│   │   └── ...
│   ├── status-cluster.sh        ← Check cluster availability
│   └── ...
└── rllib/
    ├── IPD-Two-Agents/          ← RL experiments
    └── ...
```

### What You Can Modify

**Feel free to change:**
- Prompts in `prompts.py`
- Experiment parameters
- Analysis scripts
- Create new files and directories

**These changes only affect YOUR environment.**

### What You Share

**Shared resources (coordinate before using):**
- Ollama cluster (nickel, zinc, copper, iron, platinum)
- Ray cluster (when running)

**Not shared:**
- Your code
- Your results
- Your virtual environment

---

## Part 4: Coordination Protocol

### Before Running Experiments

**1. Check cluster status:**
```bash
~/work/forge/llm/status-cluster.sh
```

**2. Check the shared communication channel:**
- Look for messages like "Running experiment until 3pm"
- If unclear, ask: "Anyone using the cluster?"

**3. Announce your usage:**
- Post: "Starting 100-round experiment, ~15 minutes"
- Or: "Running Ray job on 4 nodes, ~1 hour"

**4. When finished:**
- Post: "Experiment complete, cluster available"

### For Small Experiments (< 5 minutes)
- Check status script
- If no one's posted they're running something, go ahead
- Optional: Post a quick heads-up

### For Long Experiments (> 30 minutes)
- Always announce beforehand
- Give estimated completion time
- Update if it's taking longer

### If Someone's Using the Cluster
- Wait for them to finish
- Work on analysis, documentation, or code in the meantime
- Or coordinate: "Can I run a quick 10-round test between your runs?"

---

## Part 5: Common Tasks

### Running Different Experiment Types

**Short test (20 rounds):**
```bash
python ipd_llm_game.py --rounds 20
```

**Standard experiment (100 rounds):**
```bash
python ipd_llm_game.py --rounds 100
```

**Different temperature:**
```bash
python ipd_llm_game.py --rounds 100 --temperature 0.9
```

**Different models:**
```bash
python ipd_llm_game.py \
  --model-0 mixtral-multi \
  --host-0 nickel \
  --model-1 llama3:8b-instruct-q5_K_M \
  --host-1 iron \
  --rounds 100
```

**Custom output name:**
```bash
python ipd_llm_game.py --rounds 100 --output my_experiment_01.json
```

### Analyzing Results

**Basic analysis:**
```bash
python analyze_results.py results/game_TIMESTAMP.json
```

**With plots:**
```bash
python analyze_results.py results/game_TIMESTAMP.json --plots
```

**Plots are saved in the same directory as your results.**

### Batch Experiments

**Quick test batch (3 short games):**
```bash
python run_batch.py --quick
```

**Full research batch:**
```bash
python run_batch.py --batch
```

**Note:** Coordinate batch runs since they take longer!

---

## Part 6: Getting Updates from Doug

When Doug updates the reference code, you can selectively incorporate changes:

### Check What Changed

```bash
# Compare your version to Doug's
diff ~/work/forge/llm/prompts.py /home/dhart/work/forge/llm/prompts.py
```

### Copy Specific Updates

```bash
# Copy a single file
cp /home/dhart/work/forge/llm/prompts.py ~/work/forge/llm/

# Copy entire directory (overwrites your changes!)
cp -r /home/dhart/work/forge/llm/IPD-LLM-Agents ~/work/forge/llm/
```

### Selective Merge

If you've made your own modifications and want Doug's updates:
1. Make a backup of your version
2. Copy Doug's version
3. Manually merge your changes back in

**Or learn git for easier version control!**

---

## Part 7: Sharing Your Work

### Share Results Files

**Copy to shared location (if created):**
```bash
cp results/my_interesting_experiment.json /opt/forge-shared-results/
```

**Or share directly:**
- Email the JSON file
- Post in Slack/Discord
- Show plots in group meetings

### Share Code Changes

If you make improvements worth sharing:

**Option 1: Share the file directly**
```bash
# Show what you changed
diff ~/work/forge/llm/prompts.py /home/dhart/work/forge/llm/prompts.py
```

**Option 2: Describe the change**
- "I modified prompts.py line 45 to add..."
- Others can incorporate if useful

**Option 3: Use version control**
- Git makes this much easier
- Can be set up later if needed

---

## Part 8: Troubleshooting

### Virtual Environment Issues

**Problem:** `python` command not found or wrong version
```bash
# Make sure venv is activated
source ~/work/forge/llm/IPD-LLM-Agents/.venv/bin/activate

# Verify
which python
# Should show: .../forge/llm/IPD-LLM-Agents/.venv/bin/python
```

**Problem:** Package import errors
```bash
# Reinstall requirements
cd ~/work/forge/llm/IPD-LLM-Agents
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Connection Issues

**Problem:** "Connection refused" to Ollama
```bash
# Check cluster status
~/work/forge/llm/status-cluster.sh

# If services are down, notify Doug
# The LLM cluster may need to be restarted
```

**Problem:** "Model not found"
```bash
# Check available models
~/work/forge/llm/status-cluster.sh

# Verify you're using correct model name in your command
```

### Experiment Issues

**Problem:** Experiment crashes or hangs
```bash
# Check the error message
# Common issues:
# - Out of memory (reduce rounds or use smaller model)
# - Network timeout (cluster overloaded, try later)
# - Syntax error (check your code modifications)
```

**Problem:** Results seem wrong
```bash
# Verify the JSON file was created
ls -lh results/

# Check for error messages in the output
# Re-run with --quiet flag removed for more details
python ipd_llm_game.py --rounds 20  # verbose output
```

### Getting Help

**1. Check documentation:**
- `README.md` - Full technical details
- `QUICKSTART.md` - Quick reference
- `EXPERIMENT_LOG_*.md` - Research notes and findings

**2. Ask in communication channel:**
- Describe what you tried
- Share error messages
- Someone can help troubleshoot

**3. Pair debugging session:**
- Schedule time with Doug or other student
- Work through the problem together
- Document solution for others

---

## Part 9: Best Practices

### Before Every Session

```bash
# 1. Navigate to workspace
cd ~/work/forge/llm/IPD-LLM-Agents

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Check for updates (optional)
ls /home/dhart/work/forge/llm/IPD-LLM-Agents/

# 4. Check cluster status
~/work/forge/llm/status-cluster.sh
```

### During Experiments

- ✅ Save intermediate results
- ✅ Take notes on what you're testing
- ✅ Name output files descriptively
- ✅ Monitor progress (experiments can take 15-30 min)

### After Experiments

- ✅ Analyze results promptly
- ✅ Document interesting findings
- ✅ Release cluster (post in channel)
- ✅ Back up important results

### Good Neighbor Guidelines

- 📢 Communicate your plans
- ⏰ Respect others' scheduled time
- 🤝 Help each other troubleshoot
- 📝 Document useful discoveries
- 🔄 Share interesting results

---

## Part 10: Next Steps

### Week 1: Learning
- Run several small experiments (10-20 rounds)
- Understand the system behavior
- Get comfortable with the tools
- Read the documentation

### Week 2: Exploring
- Try different parameters
- Modify prompts (in YOUR copy)
- Compare results
- Start forming research questions

### Week 3+: Research
- Design systematic experiments
- Collect data methodically
- Analyze patterns
- Contribute to GENESIS findings

---

## Quick Reference Card

```bash
# SETUP (do once)
mkdir -p ~/work/forge
cp -r /home/dhart/work/forge/{llm,rllib} ~/work/forge/
cd ~/work/forge/llm/IPD-LLM-Agents
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# DAILY WORKFLOW
cd ~/work/forge/llm/IPD-LLM-Agents
source .venv/bin/activate
~/work/forge/llm/status-cluster.sh
# [post in channel: "starting experiment"]
python ipd_llm_game.py --rounds 100
python analyze_results.py results/game_*.json --plots
# [post in channel: "experiment complete"]

# HELP
cat README.md
cat QUICKSTART.md
# or ask in #forge-cluster channel
```

---

## Appendix: Understanding the Research

### What is GENESIS?
General Emergent Norms, Ethics, and Societies in Silico - investigating whether AI agents can develop moral foundations through interaction.

### What are we studying?
Can LLM agents learn to cooperate in Iterated Prisoner's Dilemma? Can they explain their reasoning in moral terms?

### Why does this matter?
- Understanding how cooperation emerges
- Comparing RL vs. LLM learning mechanisms  
- Connecting to moral reasoning frameworks (Haidt)
- Implications for AI alignment and ethics

### Your Role
- Run systematic experiments
- Document observations
- Analyze agent reasoning
- Contribute to understanding emergent cooperation

**This is real research. Your experiments matter. Your observations contribute to the project.**

---

## Resources

**Documentation in your workspace:**
- `~/work/forge/llm/IPD-LLM-Agents/README.md`
- `~/work/forge/llm/IPD-LLM-Agents/QUICKSTART.md`
- `~/work/forge/llm/IPD-LLM-Agents/EXPERIMENT_LOG_*.md`

**Doug's reference code:**
- `/home/dhart/work/forge/` (read-only, for comparison)

**Communication:**
- [Your communication channel - Slack/Discord/etc.]

**Questions:**
- Ask Doug: douglas.hart@regis.edu
- Ask in group channel
- Schedule office hours

---

**Welcome to FORGE! Let's discover how cooperation emerges. 🚀**
