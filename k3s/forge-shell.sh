#!/bin/bash
#*******************************************************************************
# FORGE K3s Container Deployment
# 
# Purpose:  Start an interactive FORGE pod with persistent results storage
# Usage:    ./forge-shell.sh
#
# Author:
#   Emily D. Carpenter
#   Anderson College of Business and Computing, Regis University
#   MSDS 696/S71: Data Science Practicum II
#   Dr. Douglas Hart, Dr. Kellen Sorauf
#   Practicum II, February-May 2026
#*******************************************************************************

export FORGE_USER=$(whoami)
export FORGE_UID=$(id -u)
mkdir -p ~/forge-results

echo "Starting FORGE container for ${FORGE_USER}..."
envsubst < forge-code.yml | kubectl apply -f -

echo "Waiting for pod to start..."
kubectl wait --for=condition=Ready pod/forge-${FORGE_USER} --timeout=120s

echo "Pod created. Connecting..."
kubectl exec -it forge-${FORGE_USER} -- su ${FORGE_USER}

echo ""
echo "Session ended. Your results are saved in ~/forge-results/"
echo ""
echo "To reconnect: kubectl exec -it forge-${FORGE_USER} -- su ${FORGE_USER}"
echo "To remove:    kubectl delete pod forge-${FORGE_USER}"