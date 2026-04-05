#!/bin/bash
# Check status of a specific FORGE cluster node

if [ -z "$1" ]; then
    echo "Usage: ./check_node.sh <hostname>"
    echo "Available: nickel zinc copper iron platinum tungsten"
    exit 1
fi

NODE=$1

echo "=== Node: $NODE ==="
kubectl get node $NODE
echo ""
echo "=== Pods on $NODE ==="
kubectl get pods --field-selector spec.nodeName=$NODE
echo ""
echo "=== GPU Resources ==="
kubectl describe node $NODE | grep -A3 "nvidia.com/gpu"