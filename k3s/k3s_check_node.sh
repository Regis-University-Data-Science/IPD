#!/bin/bash
#*******************************************************************************
# Forge Cluster Node Status
# 
# Purpose: check the status of a specific node on the cluster
# Usage:    ./k3s_check_node.sh <hostname>
#
# Author:
#   Emily D. Carpenter
#   Anderson College of Business and Computing, Regis University
#   MSDS 696/S71: Data Science Practicum II
#   Dr. Douglas Hart, Dr. Kellen Sorauf
#   Practicum II, February-May 2026
#*******************************************************************************

# Change directory to script folder
cd "$(dirname "$0")"

if [ -z "$1" ]; then
    echo "Usage: ./k3s_check_node.sh <hostname>"
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