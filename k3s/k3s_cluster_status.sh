#!/bin/bash

# FORGE K3s Cluster Status
#
# Purpose:  Allows user to check the status of the Kubernetes (k3s) cluster
# Usage:    ./k3s_cluster_status.sh

echo "=== Nodes ==="
kubectl get nodes
echo ""
echo "=== Pods ==="
kubectl get pods
echo ""
echo "=== Services ==="
kubectl get services
