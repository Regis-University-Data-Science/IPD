# Lightweight Kubernetes (K3s) for Containerized Architecture on GENESIS

---

## Overview

This directory contains Kubernetes (K3s) manifests and shell scripts for deploying and managing the GENESIS research platform in a containerized environment. The manifests define three types of workloads: a PostgreSQL database (ForgeDB), Ollama LLM agent containers pinned to individual GPU nodes, and an optional interactive researcher container for running experiments.

Before using these files, the cluster must first be provisioned using the Ansible playbooks in `ansible/`.

---

## Directory Structure

* `manifests/` - K3s YAML manifest files that define the containerized workloads.
   * `_ollama-agent-template.yml` - Template for creating new Ollama agent deployments. Copy this file to `ollama-<hostname>.yml` and edit to match your node.
   * `forge-code.yml` - Deployment for the FORGE research code container. This container is optional; researchers who prefer to develop and modify game code should clone the repo and run from a virtual environment.
   * `forge-db-storage.yml` - Persistent storage for PostgreSQL data. Survives pod restarts and redeployments. Apply this before `forge-db.yml`.
   * `forge-db.yml` - Deployment for the ForgeDB PostgreSQL database container.
   * `ollama-copper.yml`, `ollama-iron.yml`, `ollama-nickel.yml`, `ollama-platinum.yml`, `ollama-tungsten.yml`, `ollama-zinc.yml` - Ollama agent deployments for the Regis University reference cluster. Each deployment is pinned to a specific GPU node.

---

## Shell Scripts

Shell scripts provide lifecycle management for the K3s cluster workloads. Run these from the `k3s/` directory on the control node.

1. `k3s_start_cluster.sh` - Deploy and start all K3s pods for the research cluster. Requires `ansible/install_k3s_cluster.sh` to have been run first.
2. `k3s_status_cluster.sh` - Check the status of all running K3s pods and services.
3. `k3s_check_node.sh` - Check the status of a specific node. Usage: `./k3s_check_node.sh <hostname>`
4. `k3s_restart_deployment.sh` - Restart a single deployment by name. Usage: `./k3s_restart_deployment.sh <deployment-name>`
5. `k3s_restart_all_deployments.sh` - Restart all running deployments. There will be a brief downtime during restart.
6. `k3s_stop_cluster.sh` - Shut down all running K3s pods.
7. `forge-shell.sh` - Start an interactive FORGE shell session for running experiments inside the containerized environment.

---

## Changelog

### Version 1.0 (April 2026)
* Initial release of K3s cluster management documentation.
* Author:
   * Emily D. Carpenter
   * Marketing & Data Sciences, Anderson College of Business and Computing
   * Regis University, Denver, CO, USA
   * Project: GENESIS - General Emergent Norms, Ethics, and Societies in Silico
   * Advisors: Dr. Douglas Hart, Dr. Kellen Sorauf