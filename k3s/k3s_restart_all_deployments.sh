#!/bin/bash
#*******************************************************************************
# Rolling Restart of FORGE K3s Cluster Pods
#
# Purpose:  Restart all running deployments. Note: there will be a brief downtime
#           while deployments are restarted.
# Usage:    ./k3s_restart_all_deployments.sh
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

echo "=== Rolling restart of FORGE deployments ==="
kubectl scale deployment --all --replicas=0
kubectl scale deployment --all --replicas=1

echo ""
echo "Pod status..."
kubectl get pods
echo "=== All deployments restarted ==="
echo ""
echo "To monitor restart progress: kubectl get pods"
echo "Restart typically takes 30-60 seconds (longer on first pull)."