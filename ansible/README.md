# Cluster Provisioning for Containerized Architecture on GENESIS using Ansible

---

## Overview

This directory contains Ansible playbooks and shell scripts for provisioning a compute cluster to run the GENESIS research platform in a containerized deployment. The playbooks install Docker, the NVIDIA Container Toolkit, and lightweight Kubernetes (K3s) across all nodes (as defined in `inventory.ini` and the `group_vars/` variables), then configure GPU scheduling for Ollama agent containers.

These files are intended for use when deploying the research platform on a cluster outside of the Regis University Data Science Compute Cluster. For Regis cluster operations, refer to the documentation in `work/forge/llm/`.

### Directory Structure

* `group_vars/` - Cluster-wide Ansible variables (shared settings applied to all nodes).
   * `all.yml` - Institution-specific variables for cluster deployment. Edit this file to match your environment.
* `host_vars/` - Per-node Ansible variables.
   * `_node_template.yml` - Template for adding new nodes. Copy this file to `<hostname>.yml` and edit GPU values to match your hardware.
   * `copper.yml`, `iron.yml`, `nickel.yml`, `platinum.yml`, `tungsten.yml`, `zinc.yml` - Node configurations for the Regis University reference deployment.
* `inventory.ini` - Defines cluster membership and node roles. Edit hostnames to match your cluster nodes.

### Shell Scripts

Shell scripts provide lifecycle management for the cluster infrastructure. Run these from the `ansible/` directory.

1. `install_k3s_cluster.sh` - Full infrastructure setup. Configures `/etc/hosts` and installs Docker, NVIDIA Toolkit, and K3s across all nodes.
2. `restart_k3s_cluster.sh` - Restart K3s services on all nodes after a shutdown.
3. `shutdown_k3s_cluster.sh` - Stop K3s services on all nodes without uninstalling.
4. `uninstall_k3s_cluster.sh` - Completely remove K3s from all nodes.
5. `uninstall_nvidia_toolkit.sh` - Remove NVIDIA Container Toolkit from all nodes.

### Ansible Playbooks

Ansible is a configuration management tool that automates software installation across multiple machines over SSH.  Playbooks are listed in the order they are executed by `install_k3s_cluster.sh` and `main.yml`. Individual playbooks can also be run standalone using `ansible-playbook -K -i inventory.ini <playbook>.yml`.

1. `manage_hosts.yml` - Standardize `/etc/hosts` entries across all nodes using managed markers.
2. `main.yml` - Primary controller playbook. Imports and runs the following playbooks in order:
   1. `install_docker.yml` - Install Docker Engine (required for NVIDIA Toolkit).
   2. `install_nvidia_toolkit.yml` - Install NVIDIA Container Toolkit on all nodes.
   3. `install_k3s.yml` - Install K3s server on the control node and K3s agents on all other nodes.
   4. `configure_k3s.yml` - Label nodes with GPU capabilities and install the NVIDIA device plugin.
3. `uninstall_k3s.yml` - Cleanly uninstall K3s from all nodes.
4. `uninstall_nvidia_toolkit.yml` - Remove NVIDIA Container Toolkit from all nodes.

---

## 1. Configuration

### Prerequisites

Before running the playbooks, ensure the following requirements are met:

1. A minimum of two computing resources (physical or virtual) capable of running Ubuntu Linux. One node serves as the cluster controller, and at least one additional node must have a GPU sufficient to run an Ollama agent. These can be the same resource, but placing the Ollama agent on a separate node from the controller is recommended. Each node running Ollama should have a minimum of 10 GB of disk storage for a single model; 50 GB or more is recommended to accommodate multiple models.
2. All nodes must be running Ubuntu Linux. Other Debian-based distributions may work with modifications to the Docker repository URL in `install_docker.yml`.
3. SSH key-based authentication from the control node to all other nodes.
4. Sudo privileges on all nodes.
5. NVIDIA GPU drivers installed on all GPU nodes. Verify with: `nvidia-smi`
6. Ansible installed on the control node. Verify with: `ansible --version`
7. SSH keys generated and loaded prior to execution: `ssh-add`

All configuration files in this directory are set for the Regis University reference deployment. Update the following files to match your own cluster before running any playbooks or scripts.

### Inventory (`inventory.ini`)

Define your cluster membership by listing all node hostnames. The control node should use `ansible_connection=local` since Ansible runs directly on it. Every hostname listed here must have a matching file in `host_vars/`.

For example, the Regis University reference cluster is configured with one controlling node (platinum) and five additional machines serving as agent nodes. To configure for your own cluster, replace the hostnames with the hostnames from your own computing resources and remove any not used. The `[control]` group must contain exactly one host.  

```ini
[all]
platinum ansible_connection=local
nickel
zinc
copper
iron
tungsten

# This is the primary cluster controller, add only ONE host in this section
[control]
platinum ansible_connection=local
```
**NOTE**: it is _**strongly**_ recommended to retain `tungsten` as a hostname. If changed, then either the primary Python research code needs to be updated to use a default hostname, or the environment variables files (forge_k3s.env, forge_k3s_unset.env) contained with the primary research code must be updated and used.  


### Cluster Variables (`group_vars/all.yml`)

This file contains institution-specific settings shared across all nodes. Do not rename variable keys without updating the corresponding playbooks. The default settings listed below should be sufficient for most installations.

```yaml
# PostgreSQL persistent storage location on the control node
forge_db_storage_path: /var/lib/forge/postgres

# NVIDIA K8s device plugin version
# Ref: https://github.com/NVIDIA/k8s-device-plugin/releases
nvidia_device_plugin_version: v0.17.0
```

### Node Variables (`host_vars/`)

Each node requires its own configuration file in `host_vars/`, and the node filename **must** match the hostname listed in the `inventory.ini` configuration file. Use `nvidia-smi` on each node to identify GPU model and memory.

To add a new node, replace one of the existing reference cluster nodes or make a copy of the template provided:
1. Copy `_node_template.yml` to `<hostname>.yml`. Alternatively, replace one of the Regis University reference nodes (i.e. copper, nickel, zinc, etc.).
2. Uncomment and fill in the IP address and GPU details.
3. Add the hostname to `inventory.ini`.

It is important to note that the IP address listed in each playbook will be added to the node `/etc/hosts` file in a block that is recognized by Ansible. Users are advised to review their `/etc/hosts` file before and after installing the research cluster and remove any entries that duplicate those added by Ansible.  Entries added to `/etc/hosts` by Ansible should not be directly updated in the `hosts` file but instead be managed through Ansible. Example:

```bash
# BEGIN FORGE CLUSTER
100.110.101.75    tungsten
100.116.129.84    platinum
# END FORGE CLUSTER
```

**Single GPU example** (`tungsten.yml`):

```yaml
host_ip: 100.110.101.75

gpu_primary: rtx-6000-ada
gpu_primary_mib: 49140
gpu_count: 1
gpu_vram_total_mib: 49140
```

**Multiple GPU example** (`nickel.yml`):

```yaml
host_ip: 100.77.78.99

gpu_primary: titan-x-pascal
gpu_primary_mib: 12288
gpu_secondary: gtx-1080ti
gpu_secondary_mib: 11264
gpu_tertiary: gtx-1080ti
gpu_tertiary_mib: 11264
gpu_count: 3
gpu_vram_total_mib: 34816
```

---

## 2. Usage

### Installation

Once the Ansible configuration has been updated, ensure your SSH keys are loaded (ssh-add) and then run the installation script provided in the `ansible/` directory on the control node:

```bash
./install_k3s_cluster.sh
```

This script runs two steps:
1. Configures `/etc/hosts` across all nodes (`manage_hosts.yml`).
2. Installs Docker, NVIDIA Container Toolkit, and K3s (`main.yml`).

The `-K` flag will prompt for your sudo password. To preview changes without applying them, add `--check` to the `ansible-playbook` commands inside the script.

Users should note any errors that occur during installation and address as necessary. Troubleshooting specific issues requires detailed knowledge of the Linux operating system and is thus outside the scope of this documentation.

Once the installation has completed successfully, change to the `k3s/` directory and review the `README.md` file for starting up the cluster.

### Cluster Lifecycle

Use the following shell scripts provided in the `ansible/` folder for managing the software installation:

1. `restart_k3s_cluster.sh` - Restart K3s services on all nodes after a shutdown.
2. `shutdown_k3s_cluster.sh` - Stop K3s services on all nodes without uninstalling.


### Running Individual Playbooks

Any playbook can be run independently. While individual playbook execution is possible, it is only recommended for troubleshooting:

```bash
ansible-playbook -K -i inventory.ini <playbook>.yml
```

### Uninstallation

Execute the following shell scripts in the `ansible/` folder to uninstall all software added for the Containerized Architecture. 

1. `uninstall_k3s_cluster.sh` - Completely remove K3s from all nodes.
2. `uninstall_nvidia_toolkit.sh` - Remove NVIDIA Container Toolkit from all nodes.

Note: Removal of Ansible and Docker will require users to assess and manually remove as required. To remove Docker and Ansible, review the following commands and run as appropriate:

```bash
# Use Ansible to remove Docker
ansible -K -i inventory.ini all -m shell -a "apt purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin" --become

# Remove Ansible from controlling node
sudo apt remove ansible

# OR, remove Ansible and Ansible configuration files from controlling node
sudo apt purge ansible
```

---

## Changelog

### Version 1.0 (April 2026)
* Initial release of Ansible cluster provisioning documentation.
* Author:
   * Emily D. Carpenter, Anderson College of Business and Computing, Regis University
   * Project: GENESIS - General Emergent Norms, Ethics, and Societies in Silico
   * Advisors: Dr. Douglas Hart, Dr. Kellen Sorauf