# GENESIS - Iterated Prisoner's Dilemma (IPD) Research Platform

---

## Overview

GENESIS (General Emergent Norms, Ethics, and Societies in Silico) is a research platform that investigates whether cooperative behaviors and moral reasoning can emerge from LLM agents interacting through the Iterated Prisoner's Dilemma. Agents powered by Ollama play repeated rounds of the IPD, and their decisions, reasoning, and reflections are captured for analysis.

The platform supports two deployment modes: **bare-metal** (direct execution on the cluster) and **containerized** (Docker images orchestrated by K3s). Both modes use the same application code. Environment variables control which infrastructure the code connects to.

---

## Repository Structure

* **Primary GENESIS research project code:**
   * `work/forge/llm/` - Contains files, documentation, and scripts for managing the Regis University Compute Cluster.
   * `work/forge/llm/IPD-LLM-Agents2/` - Contains files, code, and documentation for conducting experiments to support the research project.
* **Containerized Architecture:** The following files and folders are intended for use when conducting research experiments on a cluster outside of the Regis University Data Science Compute Cluster. Start in the `ansible/` directory for instructions on how to configure the project on your own cluster.
   * `ansible/` - Installation and configuration of compute cluster.
   * `docker/` - Contains configuration for Docker images used in containerized (portable) architecture. Images are hosted on GitHub in ghcr.io.
   * `k3s/` - Configuration and operation of lightweight Kubernetes (K3s) for portable architecture.
   * `.github/` - GitHub Actions workflows that build and publish container images to `ghcr.io` on push to `main` branch of repository.
   * `.dockerignore` - Controls which files are included or excluded in the Docker container build context.

---

## Documentation

Detailed documentation lives alongside the code it describes. Refer to the markdown files within each directory for guidance on cluster operations, running experiments, and working with the database.

---

## Quick Start

1. **Regis University Compute Cluster operations** - Start in `work/forge/llm/` for cluster management documentation and scripts.
2. **Conducting research experiments** - Start in `work/forge/llm/IPD-LLM-Agents2/` for game code, analysis tools, and the ForgeDB ETL pipeline.
3. **Portable deployment at another institution** - Start in `ansible/` to install and configure the containerized architecture on your own compute cluster.

---

## Compute Cluster

The reference deployment runs on a six-node GPU compute cluster with the following hostnames: **copper**, **iron**, **nickel**, **platinum** (control node), **tungsten**, and **zinc**.

A portable Containerized Architecture was configured to allow research teams to execute code on systems other than the reference deployment cluster.

---

## Changelog

### Version 1.0 (April 2026)
* Initial release of repository README.
* README Submitted By:
   * Emily D. Carpenter
   * Marketing & Data Sciences, Anderson College of Business and Computing
   * Regis University, Denver, CO, USA
   * Project: GENESIS - General Emergent Norms, Ethics, and Societies in Silico
   * Advisors: Dr. Douglas Hart, Dr. Kellen Sorauf