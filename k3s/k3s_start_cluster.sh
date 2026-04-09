#!/bin/bash
#*******************************************************************************
# Start Forge Lightweight Kubernetes (K3s) cluster pods
# 
# Purpose:  Allows user to start the pods in the cluster
# Usage:    ./k3s_start_cluster.sh
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

echo "=== Starting FORGE containers ==="
kubectl apply -f forge-db-storage.yml
kubectl apply -f forge-db.yml

# Uncomment the nodes to be run:
# kubectl apply -f ollama-platinum.yml
# kubectl apply -f ollama-tungsten.yml
# kubectl apply -f ollama-iron.yml
kubectl apply -f ollama-copper.yml
kubectl apply -f ollama-nickel.yml
kubectl apply -f ollama-zinc.yml

echo ""
kubectl get pods
echo "=== FORGE containers started ==="