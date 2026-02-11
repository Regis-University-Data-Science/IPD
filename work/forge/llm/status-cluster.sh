#!/bin/bash
# Description: Checks service status, loaded models, and VRAM usage on all cluster machines.

HOSTS=("nickel" "zinc" "copper" "iron" "platinum" "tungsten")

echo "=== LLM Cluster Health and VRAM Status Check ==="
echo "------------------------------------------------"

for HOST in "${HOSTS[@]}"; do
    echo -e "\n--- $HOST Status ---"

    # 1. Check Ollama Service Status
    STATUS_OUTPUT=$(ssh "$HOST" "sudo /usr/bin/systemctl status ollama.service | grep 'Active:' | awk '{print \$2, \$3, \$4}'")
    echo -e "Service: \t$STATUS_OUTPUT"

    # 2. Check loaded models via API
    MODELS_OUTPUT=$(ssh "$HOST" "curl -s http://localhost:11434/api/ps 2>/dev/null")
    if echo "$MODELS_OUTPUT" | grep -q '"models":\[\]'; then
        echo -e "Loaded Models: \tNone"
    elif echo "$MODELS_OUTPUT" | grep -q '"name"'; then
        echo "Loaded Models:"
        echo "$MODELS_OUTPUT" | grep -o '"name":"[^"]*"' | sed 's/"name":"//g' | sed 's/"//g' | while read MODEL; do
            echo -e "\t- $MODEL"
        done
    else
        echo -e "Loaded Models: \tAPI not responding"
    fi

    # 3. Check VRAM Usage
    VRAM_OUTPUT=$(ssh "$HOST" "nvidia-smi --query-gpu=name,memory.used --format=csv,nounits | grep -v 'name'")

    if [ -z "$VRAM_OUTPUT" ]; then
        echo -e "VRAM Usage: \tNo GPU found or nvidia-smi failed"
    else
        echo "VRAM Usage (Name | Used MiB):"
        echo "$VRAM_OUTPUT" | while read LINE; do
            GPU_NAME=$(echo "$LINE" | awk -F', ' '{print $1}')
            VRAM_USED=$(echo "$LINE" | awk -F', ' '{print $2}')
            echo -e "\t$GPU_NAME:\t$VRAM_USED MiB"
        done
    fi
done

echo -e "\n=== Cluster Health Check Complete ==="
