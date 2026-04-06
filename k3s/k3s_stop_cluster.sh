#!/bin/bash

# Stop all FORGE K3s deployments (does not uninstall K3s)
#
# Purpose:  Allows user to stop the pods in the cluster
# Usage:    ./k3s_stop_cluster.sh

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

################################################################################
# Following commands will allow a user to BACKUP the database, drop the container, then restore.
# This assumes an issue with the default storage directory at /var/lib/forge/postgres

# BACKUP DATABASE
# kubectl exec $(kubectl get pod -l app=forge-db -o name) -- su postgres -c "pg_dump forge" > forge_backup.sql

# DELETE K3s DB CONTAINERS
# kubectl delete -f forge-db.yml
# kubectl delete -f forge-db-storage.yml

# NOTE: if needed, remove and recreate the /var/lib/forge/postgres directory

# RECREATE K3s DB CONTAINERS
# kubectl apply -f forge-db-storage.yml
# kubectl apply -f forge-db.yml

# RESTORE DB DATA AFTER POD RUNNING
# kubectl exec -i $(kubectl get pod -l app=forge-db -o name) -- su postgres -c "psql forge" < forge_backup.sql

# TEST RESTORATION
# kubectl exec $(kubectl get pod -l app=forge-db -o name) -- su postgres -c "psql -d forge -c 'SELECT count(*) FROM ipd2.results;'"