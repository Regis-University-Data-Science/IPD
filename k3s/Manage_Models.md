# Managing Ollama Models

---

## Overview

Ollama models must be installed on each GPU node before experiments can be run. Models are stored on the host filesystem and persist across container restarts. This document covers how to install, list, and remove models using Ansible and the Ollama API.

Each section provides commands for both containerized Ollama agents (port `12434`) and natively installed bare-metal agents (port `11434`). Adjust the port number if your configuration differs.

The default path for pulling down models is the same for the Containerized Architecture and Natively installed Ollama agents: `/usr/share/ollama/.ollama`.  

---

## List Installed Models

**Containerized Ollama Agents:**

```bash
# Single node
ansible -K -i ansible/inventory.ini tungsten -m shell -a "curl -s http://localhost:12434/api/tags"

# All nodes
ansible -K -i ansible/inventory.ini all -m shell -a "curl -s http://localhost:12434/api/tags"
```

**Native (bare-metal) Ollama Agents:**

```bash
# Single node
ansible -K -i ansible/inventory.ini tungsten -m shell -a "ollama list"

# All nodes
ansible -K -i ansible/inventory.ini all -m shell -a "ollama list"
```

---

## Install New Models

**Containerized Ollama Agents:**

```bash
# Single node
ansible -K -i ansible/inventory.ini tungsten -m shell -a "curl -s http://localhost:12434/api/pull -d '{\"name\": \"llama3:8b-instruct-q5_K_M\"}'"

# Multiple nodes
ansible -K -i ansible/inventory.ini tungsten,copper,iron -m shell -a "curl -s http://localhost:12434/api/pull -d '{\"name\": \"llama3:8b-instruct-q5_K_M\"}'"

# All nodes
ansible -K -i ansible/inventory.ini all -m shell -a "curl -s http://localhost:12434/api/pull -d '{\"name\": \"llama3:8b-instruct-q5_K_M\"}'"
```

**Native (bare-metal) Ollama Agents:**

```bash
# Single node
ansible -K -i ansible/inventory.ini tungsten -m shell -a "ollama pull llama3:8b-instruct-q5_K_M"

# Multiple nodes
ansible -K -i ansible/inventory.ini tungsten,copper,iron -m shell -a "ollama pull llama3:8b-instruct-q5_K_M"

# All nodes
ansible -K -i ansible/inventory.ini all -m shell -a "ollama pull llama3:8b-instruct-q5_K_M"
```

Note: The Ollama API returns HTTP 200 even if a model name is not found in the registry. Check the output for `"error"` messages to confirm the pull was successful.

---

## Remove Models

**Containerized Ollama Agents:**

```bash
# Single node
ansible -K -i ansible/inventory.ini tungsten -m shell -a "curl -s -X DELETE http://localhost:12434/api/delete -d '{\"name\": \"llama3:8b-instruct-q5_K_M\"}'"

# All nodes
ansible -K -i ansible/inventory.ini all -m shell -a "curl -s -X DELETE http://localhost:12434/api/delete -d '{\"name\": \"llama3:8b-instruct-q5_K_M\"}'"
```

**Native (bare-metal) Ollama Agents:**

```bash
# Single node
ansible -K -i ansible/inventory.ini tungsten -m shell -a "ollama rm llama3:8b-instruct-q5_K_M"

# All nodes
ansible -K -i ansible/inventory.ini all -m shell -a "ollama rm llama3:8b-instruct-q5_K_M"
```

---

## Available Models

Refer to the Ollama model library at [https://ollama.com/library](https://ollama.com/library) for a list of available models. When selecting models, consider the GPU VRAM available on each node. See the node configurations in `ansible/host_vars/` for hardware details.

---

## Changelog

### Version 1.0 (April 2026)
* Initial release of Ollama model management documentation.
* Author:
   * Emily D. Carpenter
   * Marketing & Data Sciences, Anderson College of Business and Computing
   * Regis University, Denver, CO, USA
   * Project: GENESIS - General Emergent Norms, Ethics, and Societies in Silico
   * Advisors: Dr. Douglas Hart, Dr. Kellen Sorauf