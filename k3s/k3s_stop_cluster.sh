#!/bin/bash
#*******************************************************************************
# Stop Forge Lightweight Kubernetes (K3s) cluster pods
# 
# Purpose:  Shuts down all running K3s cluster pods
# Usage:    ./k3s_stop_cluster.sh
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

echo "=== Stopping FORGE Deployments, Services, and Pods ==="
kubectl delete deployments,services,pods --all

echo "=== Stopping FORGE Storage Resources ==="
kubectl delete pvc --all
kubectl delete pv --all
echo ""

echo "=== Checking Status ==="
kubectl get pods
kubectl get services
echo "=== FORGE containers stopped ==="

echo "NOTE: PostgreSQL data is preserved/retained at /var/lib/forge/postgres."