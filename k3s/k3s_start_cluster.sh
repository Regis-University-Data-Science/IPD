#!/bin/bash
#*******************************************************************************
# Start FORGE Lightweight Kubernetes (K3s) Cluster Pods
# 
# Purpose:  Deploy and start K3s pods for the research cluster.
# Usage:    ./k3s_start_cluster.sh
#
# Prerequisites: Run ansible/setup_cluster.sh first
#
# Additional consideration: ensure bare-metal Ollama agents are stopped on
# target machines (if running). Example:
#   ansible -K -i inventory.ini nickel,zinc -m shell -a "systemctl stop ollama.service" --become
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

echo "Creating persistent storage..."
kubectl apply -f manifests/forge-db-storage.yml

echo "Deploying ForgeDB..."
kubectl apply -f manifests/forge-db.yml

# Uncomment the nodes to be run:
echo "Deploying Ollama Agents..."
kubectl apply -f manifests/ollama-copper.yml
kubectl apply -f manifests/ollama-iron.yml
kubectl apply -f manifests/ollama-nickel.yml
kubectl apply -f manifests/ollama-platinum.yml
kubectl apply -f manifests/ollama-tungsten.yml
kubectl apply -f manifests/ollama-zinc.yml

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

echo "=== FORGE containers started ==="

echo ""
echo "To launch a FORGE code container for interactive use:"
echo "  ./forge-shell.sh"