#!/bin/bash
#*******************************************************************************
# Restart (Bounce) a Single FORGE K3s Deployment
#
# Purpose:  Restart a single deployment by name.
# Usage:    ./k3s_restart_deployment.sh <deployment-name>
# Example:  ./k3s_restart_deployment.sh ollama-copper
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
    echo "Usage: ./k3s_restart_deployment.sh <deployment-name>"
    echo ""
    echo "Active deployments:"
    kubectl get deployments --no-headers -o custom-columns=":metadata.name"
    exit 1
fi

DEPLOYMENT=$1

kubectl scale deployment "$DEPLOYMENT" --replicas=0
kubectl scale deployment "$DEPLOYMENT" --replicas=1

echo ""
echo "Pod status..."
kubectl get pods
echo "=== $DEPLOYMENT restarted ==="
echo ""
echo "To monitor restart progress: kubectl get pods"
echo "Restart typically takes 30-60 seconds (longer on first pull)."