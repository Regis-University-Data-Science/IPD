#!/bin/bash
#*******************************************************************************
# Stop Forge Lightweight Kubernetes (K3s) cluster pods
# 
# Purpose:  Shuts down all running K3s cluster pods
# Usage:    ./k3s_stkop_cluster.sh
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

echo "=== Stopping FORGE containers ==="
kubectl delete -f forge-db.yml
kubectl delete -f forge-db-storage.yml
echo ""

echo "Stopping Ollama containers..."
kubectl delete -f ollama-copper.yml 2>/dev/null
kubectl delete -f ollama-iron.yml 2>/dev/null
kubectl delete -f ollama-nickel.yml 2>/dev/null
kubectl delete -f ollama-platinum.yml 2>/dev/null
kubectl delete -f ollama-tungsten.yml 2>/dev/null
kubectl delete -f ollama-zinc.yml 2>/dev/null

kubectl get pods
echo "=== FORGE containers stopped ==="

echo "NOTE: Database storage (forge-db-storage.yml) preserved at /var/lib/forge/postgres."