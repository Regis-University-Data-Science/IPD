# LLM Cluster Operations Guide

## Overview

This guide describes how to manage the five-machine LLM cluster consisting of:
- **Nickel** - Mixtral 8x7B (3x TITAN X Pascal, 34GB total VRAM)
- **Zinc** - CodeLlama 34B (2x GTX 1080 Ti, 22GB total VRAM)
- **Copper** - Mistral 7B (1x TITAN X Pascal, 12GB VRAM)
- **Iron** - Llama3 8B (1x TITAN X Pascal, 12GB VRAM)
- **Platinum** - Phi-3 Mini (1x GTX 1660, 6GB VRAM)

All cluster management commands should be run from **Platinum** (the orchestrator machine).

## Prerequisites

- SSH access to all five machines configured with key-based authentication
- Scripts located in `/home/dhart/bin/` on Platinum
- Sudo privileges configured for systemctl commands via NOPASSWD

## Basic Operations

### Starting the Cluster

To start all models across the cluster:

```bash
cd ~/work/forge/llm
./start-cluster.sh
```

**What happens:**
1. Sets CUDA_VISIBLE_DEVICES for each machine's GPU configuration
2. Restarts the Ollama service on each machine
3. Loads the designated model via API with 24-hour persistence
4. Models remain loaded for 24 hours unless explicitly stopped

**Expected output:**
```
=== LLM CLUSTER STARTUP: API-BASED MODEL LOADING ===

--- Processing nickel (mixtral-multi) ---
  > Setting CUDA_VISIBLE_DEVICES=0,1,2...
  > Restarting ollama.service (applies env vars)...
  > Waiting for Ollama service to be ready...
  > Loading model with keep_alive=24h...
  > Model load initiated. Waiting 5s before proceeding...
...
```

**Startup time:** Approximately 2-3 minutes for all models to fully load into VRAM.

### Stopping the Cluster

To cleanly shut down all models and services:

```bash
cd ~/work/forge/llm
./stop-cluster.sh
```

**What happens:**
1. Stops the Ollama service on each machine
2. Automatically unloads models from VRAM
3. Frees GPU memory for other workloads

**Expected output:**
```
=== Initiating Graceful LLM Cluster Shutdown ===

  > Stopping ollama.service on nickel...
  > Stopping ollama.service on zinc...
  > Stopping ollama.service on copper...
  > Stopping ollama.service on iron...
  > Stopping ollama.service on platinum...

=== Shutdown Procedure Complete. ===
```

### Checking Cluster Status

To view the current state of all machines:

```bash
cd ~/work/forge/llm
./status-cluster.sh
```

**What it shows:**
- Ollama service status (active/inactive)
- Currently loaded models
- VRAM usage per GPU

**Example output:**
```
=== LLM Cluster Health and VRAM Status Check ===
------------------------------------------------

--- nickel Status ---
Service: 	active (running) since
Loaded Models:
	- mixtral-multi:latest
VRAM Usage (Name | Used MiB):
	NVIDIA TITAN X (Pascal):	10115 MiB
	NVIDIA GeForce GTX 1080 Ti:	9861 MiB
	NVIDIA GeForce GTX 1080 Ti:	9395 MiB

--- zinc Status ---
Service: 	active (running) since
Loaded Models:
	- codellama-multi:latest
VRAM Usage (Name | Used MiB):
	NVIDIA GeForce GTX 1080 Ti:	11136 MiB
	NVIDIA GeForce GTX 1080 Ti:	10622 MiB
...
```

## Understanding Status Output

### Service Status
- **`active (running)`** - Ollama service is running and can accept requests
- **`inactive (dead)`** - Ollama service is stopped

### Loaded Models
- **Model name listed** - Model is loaded in VRAM and ready to serve requests
- **`None`** - Service is running but no model is loaded
- **`API not responding`** - Service is not running or not accessible

### VRAM Usage
- **Baseline (service only):** ~50-85 MiB per GPU
- **Model loaded:** Significant increase based on model size:
  - Mixtral 8x7B: ~29 GB across 3 GPUs
  - CodeLlama 34B: ~22 GB across 2 GPUs
  - Mistral 7B: ~5.9 GB
  - Llama3 8B: ~6.2 GB
  - Phi-3 Mini: ~4.1 GB

## Troubleshooting

### Model Not Loading

If status shows service active but no model loaded:

1. Check if the model exists on that machine:
   ```bash
   ssh <hostname> "ollama list"
   ```

2. Manually test loading:
   ```bash
   ssh <hostname> 'curl -X POST http://localhost:11434/api/generate -d "{
       \"model\": \"<model-name>\",
       \"prompt\": \"test\",
       \"keep_alive\": \"24h\",
       \"stream\": false
   }"'
   ```

3. Check Ollama logs:
   ```bash
   ssh <hostname> "sudo journalctl -u ollama.service -n 50"
   ```

### Service Won't Start

If a machine's Ollama service shows `inactive (dead)`:

```bash
ssh <hostname> "sudo systemctl start ollama.service"
ssh <hostname> "sudo systemctl status ollama.service"
```

### VRAM Not Releasing

If VRAM remains high after stopping:

```bash
ssh <hostname> "sudo systemctl restart ollama.service"
```

Or reboot the machine if necessary.

## Configuration Files

### Model Configuration: `/home/dhart/work/forge/llm/load-model.sh`

Format: `hostname|model-tag|keep-alive|cuda-devices`

Example:
```bash
nickel|mixtral-multi|24h|0,1,2
zinc|codellama-multi|24h|0,1
copper|mistral:7b-instruct-q5_K_M|24h|0
iron|llama3:8b-instruct-q5_K_M|24h|0
platinum|phi3-mini-utility|24h|0
```

**Fields:**
- **hostname:** Machine name
- **model-tag:** Ollama model identifier
- **keep-alive:** How long to keep model in memory (e.g., 24h, 2h, 30m)
- **cuda-devices:** GPU indices to use (comma-separated for multi-GPU)

### Modifying Configuration

To change model assignments or settings:

1. Edit the configuration file:
   ```bash
   nano ~/work/forge/llm/load-model.sh
   ```

2. Restart the cluster for changes to take effect:
   ```bash
   ./stop-cluster.sh
   ./start-cluster.sh
   ```

## Network Access

All machines are accessible via Tailscale VPN:
- Services bind to `0.0.0.0:11434`
- Only accessible to users with Tailscale credentials
- API endpoint: `http://<hostname>:11434/api/generate`

## Usage Recommendations

### For Daily Use
- Start cluster at beginning of work session
- Check status before submitting jobs
- Stop cluster when finished to free resources

### For Long-Running Jobs
- Models persist for 24 hours by default
- No need to restart between jobs
- Status check confirms models remain loaded

### For Shared Resources
- Check status before starting to see if resources are in use
- Coordinate with other users before stopping the cluster
- Models can serve multiple concurrent requests

## Quick Reference

```bash
# Start everything
cd ~/work/forge/llm && ./start-cluster.sh

# Check status
cd ~/work/forge/llm && ./status-cluster.sh

# Stop everything
cd ~/work/forge/llm && ./stop-cluster.sh

# Check specific machine
ssh <hostname> "curl -s http://localhost:11434/api/ps"

# View VRAM on specific machine
ssh <hostname> "nvidia-smi"
```

## Support

For issues or questions:
- Check troubleshooting section above
- Review logs: `ssh <hostname> "sudo journalctl -u ollama.service"`
- Contact cluster administrator: dhart@regis.edu

---

**Last Updated:** December 2025  
**Cluster Version:** Ollama-based LLM serving with API access
