# Lightweight Kubernetes (K3s) for Containerized Architecture on GENESIS

---

## Overview

This directory contains manifests and shell scripts for deploying and managing the GENESIS research platform as containerized workloads on a K3s cluster. K3s is a lightweight, certified Kubernetes distribution designed for resource-constrained and edge environments. It was chosen over standard Kubernetes (K8s) because it installs as a single binary, requires minimal configuration, and runs well on heterogeneous hardware, making it suitable for research clusters that vary in GPU capability across nodes.

The manifests define three types of workloads:

* **ForgeDB** - A PostgreSQL database container with persistent storage for experiment data.
* **Ollama agents** - LLM inference containers, each pinned to a specific GPU node.
* **FORGE code container** - An optional interactive research shell for running experiments without a local development environment.

Before using these files, the cluster must first be provisioned using the Ansible playbooks in `ansible/`. Refer to the Ansible `README.md` for installation instructions.

### Directory Structure

* `manifests/` - K3s YAML manifest files that define the containerized workloads.
   * `_ollama-agent-template.yml` - Template for creating new Ollama agent deployments. Copy this file to `ollama-<hostname>.yml` and edit to match your node.
   * `forge-code.yml` - Pod definition for the FORGE interactive research container. Used by `forge-shell.sh`.
   * `forge-db-storage.yml` - PersistentVolume and PersistentVolumeClaim for PostgreSQL data. Must be applied before `forge-db.yml`. Data is retained on disk even when pods are removed.
   * `forge-db.yml` - Deployment for the ForgeDB PostgreSQL database container.
   * `ollama-copper.yml`, `ollama-iron.yml`, `ollama-nickel.yml`, `ollama-platinum.yml`, `ollama-tungsten.yml`, `ollama-zinc.yml` - Ollama agent deployments for the Regis University reference cluster. Each deployment is pinned to a specific GPU node.

### Shell Scripts

Shell scripts provide lifecycle management for the K3s cluster workloads. Run these from the `k3s/` directory on the control node.

1. `k3s_start_cluster.sh` - Deploy and start all K3s pods. Applies storage, database, and Ollama agent manifests in the correct order.
2. `k3s_status_cluster.sh` - Check the status of all nodes, deployments, pods, and services.
3. `k3s_check_node.sh` - Check the status of a specific node, including its pods and GPU resources. Usage: `./k3s_check_node.sh <hostname>`
4. `k3s_restart_deployment.sh` - Restart a single deployment by name. Usage: `./k3s_restart_deployment.sh <deployment-name>`
5. `k3s_restart_all_deployments.sh` - Restart all running deployments. There will be a brief downtime during restart.
6. `k3s_stop_cluster.sh` - Shut down all running pods, services, and storage resources. PostgreSQL data is preserved on disk at `/var/lib/forge/postgres`.
7. `forge-shell.sh` - Start an interactive FORGE shell session for running experiments inside the containerized environment.

---

## 1. Configuration

### Prerequisites

1. The cluster must be provisioned using the Ansible playbooks in `ansible/`. Refer to the Ansible `README.md` for installation and configuration instructions.
2. If bare-metal Ollama agents are running on any nodes, they must be stopped before starting containerized agents. Containerized Ollama uses port 12434 to coexist with bare-metal Ollama (port 11434), but running both simultaneously on the same node can cause GPU resource conflicts.
3. Additionally, the `hostPort` in each Ollama agent manifest is currently set to 12434 to avoid conflict with bare-metal Ollama agents on port 11434. If no bare-metal agents are in use, set the `hostPort `in each Ollama agent manifest to 11434.

To stop bare-metal Ollama on specific nodes:

```bash
ansible -K -i ansible/inventory.ini nickel,zinc -m shell -a "systemctl stop ollama.service" --become
```

### Ollama Agent Manifests

The Ollama agent manifests in `manifests/` are configured for the Regis University reference cluster. To deploy on your own cluster, you will need to create a manifest for each GPU node.

For each GPU node in your cluster:
1. Copy `manifests/_ollama-agent-template.yml` to `manifests/ollama-<hostname>.yml`.
2. Edit the file and replace all template placeholders with your node's hostname.
3. Verify the GPU resource requests match your node's capabilities.

Alternatively, edit the existing Regis reference manifests and replace hostnames and hardware values to match your nodes.

### Updating the Start Script

The `k3s_start_cluster.sh` script contains hardcoded references to the Regis University Ollama agent manifest filenames. After creating or renaming manifests for your cluster, update the `kubectl apply` lines in this script to reference your manifest files.

For example, this is how the Regis University Compute Cluster agents are listed in the `k3s_start_cluster.sh` shell script. These entries must be updated to reference the manifests (YAML files) configured for each unique custom compute cluster. 

```bash
# Update each line below to use the YML file configured in the new compute cluster:
echo "Deploying Ollama Agents..."
kubectl apply -f manifests/ollama-copper.yml
kubectl apply -f manifests/ollama-iron.yml
kubectl apply -f manifests/ollama-nickel.yml
kubectl apply -f manifests/ollama-platinum.yml
kubectl apply -f manifests/ollama-tungsten.yml
kubectl apply -f manifests/ollama-zinc.yml
```

### Port Configuration

Containerized Ollama agents are configured to use host port **12434** to allow coexistence with bare-metal Ollama installations (which use port 11434). This means:

* Bare-metal clients connect to Ollama via `<hostname>:11434`
* Containerized clients connect via `<hostname>:12434`
* Internal pod-to-pod traffic within K3s uses `ollama-<hostname>:11434`

If bare-metal Ollama is not installed or has been removed, you may change `hostPort` in each Ollama manifest to `11434` and update `OLLAMA_PORT` in the environment variables file (`forge_k3s.env`) located in the primary research code directory.

---

## 2. Usage

### Starting the Cluster

To start the K3s cluster, run the following shell script in the `k3s/` directory on the control node:

```bash
./k3s_start_cluster.sh
```

By default, this script deploys the database (with persistent storage)  followed by Ollama agents on each configured node. After completion, the script will display the status of all nodes, deployments, pods, and services.

### Checking Status

To view the status (health) of the full cluster, run the following script located in the `k3s/` directory:

```bash
./k3s_status_cluster.sh
```

To check a specific node, its pods, and GPU resources, run the check node shell script where <hostname> is the name defined in the `inventory.ini` file:

```bash
./k3s_check_node.sh <hostname>
```

Users can also run standard `kubectl` commands directly. Example:

```bash
# Show all deployments, pods, and services
kubectl get all

# Show persistent volumes and volume claims
kubectl get pv,pvc

# Show all nodes registered in the cluster
kubectl get nodes
```

### Running Experiments

The `forge-shell.sh` script starts an interactive research container personalized to your user account:

```bash
./forge-shell.sh
```

This creates a pod named `forge-<username>`, mounts a `~/forge-results/` directory for persistent output, and opens a shell session inside the container. The research code and all dependencies are pre-installed.

Important notes:
* Experiment results saved to `~/forge-results/` persist on the host after the session ends.
* Code changes made inside the container are not preserved. For development work, clone the repository and use a Python virtual environment instead.
* To reconnect to an existing session: `kubectl exec -it forge-<username> -- su <username>`
* To remove the pod: `kubectl delete pod forge-<username>`
* When running inside forge-shell, Ollama hostnames use the K3s service name rather than the bare-metal hostname (i.e. ollama-tungsten, ollama-iron, etc.). Example:
```bash
  python episodic_ipd_game.py --host-0 ollama-tungsten --host-1 ollama-tungsten --episodes 5 --rounds 10 --temperature 0.2
```

When running experiments against the containerized infrastructure from bare-metal (outside the FORGE container), the research code must be configured to use the containerized service ports. 

The easiest way to accomplish this is to source the environment variables file from the primary research code directory before running experiments. Alternatively, users can update their `.bashrc` files to incorporate the variables listed in the `forge_k3s.env` file.

```bash
source work/forge/llm/IPD-LLM-Agents2/forge_k3s.env
```

This sets the database host, port (30432 instead of 5432), and Ollama port (12434 instead of 11434) used by the containerized services. To return to bare-metal defaults, run:

```bash
source work/forge/llm/IPD-LLM-Agents2/forge_k3s_unset.env
```

### Restarting Deployments

To restart a single deployment (for example, if an Ollama agent becomes unresponsive):

```bash
./k3s_restart_deployment.sh ollama-copper
```
Note: the <deployment> name can be found by running the following command:
```bash
kubectl get deployments
```

To restart all deployments:
```bash
./k3s_restart_all_deployments.sh
```

Restarts typically take 30-60 seconds. There will be a brief period of downtime during the restart.

### Stopping the Cluster

To stop all resources running on the cluster, execute the following shell script:

```bash
./k3s_stop_cluster.sh
```
This removes all deployments, services, pods, and storage resources. PostgreSQL data is preserved on disk at `/var/lib/forge/postgres` and will be available when the cluster is restarted.

**NOTE**: This stops K3s workloads only. To stop the K3s infrastructure itself (the K3s services on each node), use `ansible/shutdown_k3s_cluster.sh` instead. 

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