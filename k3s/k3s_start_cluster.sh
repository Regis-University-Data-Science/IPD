#!/bin/bash

# Start FORGE K3s deployments
#
# Purpose:  Allows user to start the pods in the cluster
# Usage:    ./k3s_start_cluster.sh

echo "=== Starting FORGE containers ==="
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