#!/bin/bash
#*******************************************************************************
# Forge Lightweight Kubernetes (K3s)
# 
# Purpose:  Allows user to check the status of the Kubernetes (k3s) cluster
# Usage:    ./k3s_status_cluster.sh
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

echo ""
echo "Cluster status..."
echo "=== Nodes ==="
kubectl get nodes
echo ""
echo "=== Deployments ==="
kubectl get deployments
echo ""
echo "=== Pods ==="
kubectl get pods
echo ""
echo "=== Services ==="
kubectl get services
echo ""
