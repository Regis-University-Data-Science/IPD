#!/bin/bash
#*******************************************************************************
# FORGE K3s Container Deployment
# 
# Purpose: Deploy Lightweight Kubernetes (K3s) pods for the research cluster.
# 
# Prerequisites: Run ansible/setup_cluster.sh first
#
# Additional consideration: ensure bare-metal ollama agents are stopped on target 
# machines (if running):
#   ansible -K -i inventory.ini nickel,zinc,copper -m shell -a "systemctl stop ollama.service" --become
#
# Author:
#   Emily D. Carpenter
#   Anderson College of Business and Computing, Regis University
#   MSDS 696/S71: Data Science Practicum II
#   Dr. Douglas Hart, Dr. Kellen Sorauf
#   Practicum II, February-May 2026
#*******************************************************************************

echo "=== FORGE K3s Deployment ==="

# Change directory to script folder
cd "$(dirname "$0")"

echo "Creating persistent storage..."
kubectl apply -f forge-db-storage.yml

echo "Deploying ForgeDB..."
kubectl apply -f forge-db.yml
echo "=== Database deployed ==="

echo "Verifying deployment..."
kubectl get pods
kubectl get services

# Deploy Ollama nodes individually as needed:
# kubectl apply -f ollama-tungsten.yml
kubectl apply -f ollama-iron.yml
kubectl apply -f ollama-copper.yml
kubectl apply -f ollama-nickel.yml
kubectl apply -f ollama-zinc.yml


echo ""
echo "=== Deployment complete ==="

echo ""
echo "To launch a FORGE code container for interactive use:"
echo "  ./forge-shell.sh"