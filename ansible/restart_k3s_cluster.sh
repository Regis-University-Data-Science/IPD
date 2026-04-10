#!/bin/bash
#*******************************************************************************
# Restart FORGE K3s Cluster
#
# Purpose:  Restart K3s services on all nodes after a shutdown.
# Usage:    ./restart_cluster.sh
#
# NOTE:     This restarts K3s infrastructure only. To deploy workloads,
#           run k3s/k3s_start_cluster.sh after this script completes.
#           *** Ensure SSH keys are loaded prior to execution (ssh-add)
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

echo "=== Restarting FORGE K3s cluster ==="

echo "Starting K3s server..."
ansible -K -i inventory.ini control -m shell -a "systemctl start k3s" --become

echo "Starting K3s agents..."
ansible -K -i inventory.ini 'all:!control' -m shell -a "systemctl start k3s-agent" --become

echo ""
echo "Waiting for nodes to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=120s

echo ""
kubectl get nodes
echo "=== K3s cluster restarted ==="

echo ""
echo "To deploy workloads, run: ../k3s/k3s_start_cluster.sh"