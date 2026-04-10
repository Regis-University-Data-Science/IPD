#!/bin/bash
#*******************************************************************************
# Uninstall NVIDIA Container Toolkit
#
# Purpose:  Remove NVIDIA Container Toolkit from all cluster nodes.
# Usage:    ./uninstall_nvidia_toolkit.sh
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

echo "=== Uninstalling FORGE K3s NVIDIA Toolkit ==="
echo "WARNING: This will remove the NVIDIA Toolkit from ALL nodes."
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo "=== Uninstalling NVIDIA Container Toolkit ==="
ansible-playbook -K -i inventory.ini uninstall_nvidia_toolkit.yml

echo ""
echo "=== NVIDIA Container Toolkit uninstalled ==="