#!/bin/bash
# Description: Stops the LLM model and API service cleanly on all cluster servers.

HOSTS=("nickel" "zinc" "copper" "iron" "platinum" "tungsten")

echo "=== Initiating Graceful LLM Cluster Shutdown ==="
echo " "

# Loop through all machines
for HOST in "${HOSTS[@]}"; do

   # 1. Stop the Ollama service cleanly (unloads the VRAM)
   echo "  > Stopping ollama.service on $HOST..."
   ssh "$HOST" "sudo /usr/bin/systemctl stop ollama.service"

   # 2. Verify shutdown status
   STATUS=$(ssh "$HOST" "sudo /usr/bin/systemctl status ollama.service | grep Active")

done

echo ""
echo "=== Shutdown Procedure Complete. ==="
