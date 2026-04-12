# Docker Container Images for Containerized Architecture on GENESIS

---

## Overview

This directory contains Dockerfiles and supporting scripts for building the two container images used in the GENESIS Containerized Architecture. These images are automatically built and published to the GitHub Container Registry (ghcr.io) by GitHub Actions workflows in `.github/` whenever changes are pushed to the `main` branch.

Researchers deploying the Containerized Architecture do not need to build these images manually. The K3s manifests in `k3s/` pull the pre-built images directly from ghcr.io. This directory is only relevant if you need to understand or modify how the images are built.

Published images:
* `ghcr.io/regis-university-data-science/forge-code`
* `ghcr.io/regis-university-data-science/forge-db`

### Directory Structure

* `forge-code/` - FORGE research code container.
   * `Dockerfile` - Builds a Python 3.12 image containing the research code, dependencies, and an entrypoint script that creates a user account at runtime.
   * `entrypoint.sh` - Creates a user matching the host account (via `FORGE_USER` and `FORGE_UID` environment variables), preserves K3s-injected environment variables, and opens an interactive shell.
   * `requirements.txt` - Python package dependencies for the research code container.
* `forge-db/` - ForgeDB PostgreSQL database container.
   * `Dockerfile` - Builds a PostgreSQL 16 image with trust authentication and the GENESIS database schema pre-loaded.
   * `setup_forge_db.sql` - Database schema script. Copied from `work/forge/llm/IPD-LLM-Agents2/database/setup_forge_db.sql`.
   * `setup_forge_db_grants.sql` - Grants schema permissions to all database users.

---

## Image Details

### forge-code

The FORGE code image packages the primary research code and all Python dependencies into a ready-to-run container. The Dockerfile copies the following:

* `docker/forge-code/requirements.txt` - Python package dependencies.
* `work/forge/llm/IPD-LLM-Agents2/` - The primary research code directory.

The `entrypoint.sh` script runs at container startup and creates a Linux user matching the researcher's host account, ensuring file ownership consistency between the container and mounted host directories.

### forge-db

The ForgeDB image creates a PostgreSQL 16 database with trust authentication (no password required) and the full GENESIS schema pre-configured. The Dockerfile copies the following from the `docker/forge-db/` directory:

* `setup_forge_db.sql` - The database schema, loaded as `01_db_setup.sql` during container initialization. This file is a copy of the schema script maintained in `work/forge/llm/IPD-LLM-Agents2/database/setup_forge_db.sql`.
* `setup_forge_db_grants.sql` - Loaded as `02_db_grants.sql` to grant permissions after the schema is created.

> ⚠️ **If the database schema is modified, the copy of `setup_forge_db.sql` in this directory must also be updated to keep the containerized database in sync with bare-metal.**

---

## Building Locally

### Pulling Pre-Built Images

Images are automatically built by GitHub Actions on push to `main` and published to the GitHub Container Registry. To pull the pre-built images for your repository:

```bash
docker pull ghcr.io/<your-github-org>/<image-name>:main
```

Replace `<your-github-org>` and `<image-name>` with the values matching your repository's GitHub Actions workflow configuration in `.github/workflows/`.

### Building from Source

If you need to build the images locally for testing or development:

```bash
# Build the FORGE code image (run from the repository root)
docker build -t test-forge-code -f docker/forge-code/Dockerfile .

# Build the ForgeDB image (run from the repository root)
docker build -t test-forge-db -f docker/forge-db/Dockerfile .
```

Both commands must be run from the repository root because the Docker build context (`.`) includes files from `work/` and `docker/`.

---

## Changelog

### Version 1.0 (April 2026)
* Initial release of Docker container documentation.
* Author:
   * Emily D. Carpenter
   * Marketing & Data Sciences, Anderson College of Business and Computing
   * Regis University, Denver, CO, USA
   * Project: GENESIS - General Emergent Norms, Ethics, and Societies in Silico
   * Advisors: Dr. Douglas Hart, Dr. Kellen Sorauf