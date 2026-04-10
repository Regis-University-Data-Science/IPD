#!/bin/bash
#*******************************************************************************
# Shutdown FORGE K3s Cluster
#
# Purpose:  Stop K3s services on all nodes without uninstalling.
#           Use initialize_cluster.sh or systemctl to restart.
# Usage:    ./shutdown_cluster.sh
#
# NOTE:     This stops the K3s infrastructure, not just workloads.
#           For stopping workloads only, use k3s/k3s_stop_cluster.sh instead.
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

echo "=== Shutting down FORGE K3s cluster ==="

echo "Stopping K3s agents..."
ansible -K -i inventory.ini 'all:!control' -m shell -a "systemctl stop k3s-agent" --become

echo "Stopping K3s server..."
ansible -K -i inventory.ini control -m shell -a "systemctl stop k3s" --become

echo ""
echo "=== K3s cluster shut down ==="
echo "NOTE: To restart the cluster, run: ./initialize_cluster.sh"