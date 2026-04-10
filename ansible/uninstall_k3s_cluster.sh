#!/bin/bash
#*******************************************************************************
# Uninstall FORGE K3s Cluster
#
# Purpose:  Completely remove K3s from all nodes.
# Usage:    ./uninstall_cluster.sh
#
# WARNING:  This will destroy all running pods, services, and K3s configuration.
#           To simply stop the cluster, use shutdown_k3s_cluster.sh instead.
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

echo "=== Uninstalling FORGE K3s cluster ==="
echo "WARNING: This will remove K3s from ALL nodes."
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Uninstall cancelled."
    exit 0
fi

ansible-playbook -K -i inventory.ini uninstall_k3s.yml

echo ""
echo "=== K3s cluster uninstalled ==="
echo "NOTE: PostgreSQL data is preserved/retained at /var/lib/forge/postgres."
echo "To reinstall, run: ./install_k3s_cluster.sh"