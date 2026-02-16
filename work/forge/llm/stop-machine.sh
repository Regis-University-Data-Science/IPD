#!/bin/bash
# Description: Stops the LLM model and API service cleanly on a single cluster server

if [ -z "$1" ]; then
    echo "Usage: $0 <hostname>"
    echo "Available hosts: nickel, zinc, copper, iron, platinum, tungsten"
    exit 1
fi

HOST="$1"

echo "=== Initiating Graceful LLM Shutdown on $HOST ==="
echo " "

# 1. Stop the Ollama service cleanly (unloads the VRAM)
echo "  > Stopping ollama.service on $HOST..."
ssh "$HOST" "sudo /usr/bin/systemctl stop ollama.service"

# 2. Verify shutdown status
STATUS=$(ssh "$HOST" "sudo /usr/bin/systemctl status ollama.service | grep Active")
echo "  > Status: $STATUS"

echo ""
echo "=== Shutdown Procedure Complete for $HOST ==="
