#!/bin/bash
# Description: Check health and VRAM status of a single machine in the LLM cluster

if [ -z "$1" ]; then
    echo "Usage: $0 <hostname>"
    echo "Available hosts: nickel, zinc, copper, iron, platinum, tungsten"
    exit 1
fi

HOSTNAME="$1"

echo "=== LLM Machine Health and VRAM Status Check ==="
echo "------------------------------------------------"
echo ""

echo "--- $HOSTNAME Status ---"

# Check service status
SERVICE_STATUS=$(ssh dhart@$HOSTNAME "systemctl is-active ollama.service" 2>/dev/null)
echo "Service: 	$SERVICE_STATUS since"

# Check loaded models
echo "Loaded Models:"
MODELS=$(ssh dhart@$HOSTNAME "curl -s http://localhost:11434/api/ps 2>/dev/null")
if [ -n "$MODELS" ]; then
    echo "$MODELS" | jq -r '.models[]? | "\t- " + .name' 2>/dev/null || echo "	None"
else
    echo "	API not responding"
fi

# Check VRAM usage
echo "VRAM Usage (Name | Used MiB):"
ssh dhart@$HOSTNAME "nvidia-smi --query-gpu=name,memory.used --format=csv,noheader" 2>/dev/null | \
    awk -F', ' '{printf "\t%s:\t%s\n", $1, $2}' || echo "	Unable to query"

# Check active users
ACTIVE_USERS=$(ssh dhart@$HOSTNAME "ps aux | grep -E '(python|ollama)' | grep -v grep | awk '{print \$1}' | sort -u | tr '\n' ' '" 2>/dev/null)
if [ -n "$ACTIVE_USERS" ]; then
    echo "Active users: $ACTIVE_USERS"
else
    echo "Active users: None"
fi

# Check GPU process owners
GPU_PIDS=$(ssh dhart@$HOSTNAME "nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null" 2>/dev/null)
if [ -n "$GPU_PIDS" ]; then
    echo "GPU process owners:"
    for PID in $GPU_PIDS; do
        USER=$(ssh dhart@$HOSTNAME "ps -o user= -p $PID 2>/dev/null")
        CMD=$(ssh dhart@$HOSTNAME "ps -o args= -p $PID 2>/dev/null" | cut -c1-50)
        echo "	- PID $PID: $USER ($CMD...)"
    done
else
    echo "GPU process owners: None"
fi

echo ""
echo "=== Status Check Complete for $HOSTNAME ==="
