#!/bin/bash
# Description: Start a single machine in the LLM cluster with API-based model loading

if [ -z "$1" ]; then
    echo "Usage: $0 <hostname>"
    echo "Available hosts: nickel, zinc, copper, iron, platinum, tungsten"
    exit 1
fi

HOST="$1"
MODEL_CONFIG_FILE="$HOME/work/forge/llm/load-model.sh"

echo "=== LLM SINGLE MACHINE STARTUP: $HOST ==="
echo " "

# Read the config file and extract configuration for this host
HOST_CONFIG=$(grep "^$HOST|" "$MODEL_CONFIG_FILE")

if [ -z "$HOST_CONFIG" ]; then
    echo "Error: Configuration for $HOST not found in $MODEL_CONFIG_FILE"
    echo "Available hosts: nickel, zinc, copper, iron, platinum, tungsten"
    exit 1
fi

IFS='|' read -r HOSTNAME MODEL_TAG KEEP_ALIVE CUDA_DEVICES <<< "$HOST_CONFIG"

echo "--- Processing $HOSTNAME ($MODEL_TAG) ---"

# 1. Set Environment Variables and Restart Service
echo "  > Setting CUDA_VISIBLE_DEVICES=$CUDA_DEVICES..."
ssh "$HOST" "sudo /usr/bin/systemctl set-environment CUDA_VISIBLE_DEVICES='$CUDA_DEVICES'"

echo "  > Restarting ollama.service (applies env vars)..."
ssh "$HOST" "sudo /usr/bin/systemctl restart ollama.service"

# 2. Wait for service to be ready
echo "  > Waiting for Ollama service to be ready..."
sleep 3

# 3. Load model using API with proper keep-alive
echo "  > Loading model with keep_alive=$KEEP_ALIVE..."
ssh "$HOST" "curl -s -X POST http://localhost:11434/api/generate -d '{
    \"model\": \"$MODEL_TAG\",
    \"prompt\": \"Ready to serve\",
    \"keep_alive\": \"$KEEP_ALIVE\",
    \"stream\": false
}' > /dev/null 2>&1 &"

# 4. Wait for model to start loading
echo "  > Model load initiated. Waiting 5s before proceeding..."
sleep 5

echo ""
echo "=== Startup sequence completed for $HOST. Model loading in background. ==="
echo "=== Wait 30 seconds, then run status-machine.sh $HOST for confirmation. ==="
