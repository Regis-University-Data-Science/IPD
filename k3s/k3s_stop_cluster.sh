#!/bin/bash

# Stop all FORGE K3s deployments (does not uninstall K3s)
#
# Purpose:  Allows user to stop the pods in the cluster
# Usage:    ./k3s_stop_cluster.sh

echo "=== Stopping FORGE containers ==="
kubectl delete -f forge-db.yml 2>/dev/null
kubectl delete -f ollama-copper.yml 2>/dev/null
kubectl delete -f ollama-iron.yml 2>/dev/null
kubectl delete -f ollama-nickel.yml 2>/dev/null
kubectl delete -f ollama-platinum.yml 2>/dev/null
kubectl delete -f ollama-tungsten.yml 2>/dev/null
kubectl delete -f ollama-zinc.yml 2>/dev/null
echo ""
kubectl get pods
echo "=== FORGE containers stopped ==="