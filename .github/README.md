# GitHub Actions Workflows for GENESIS Containerized Architecture

---

## Overview

This directory contains GitHub Actions workflows that automatically build and publish Docker container images to the GitHub Container Registry (ghcr.io) whenever changes are pushed to the `main` branch of the repository.

For details on the container images themselves, refer to the `docker/` README.

### Workflows

* `workflows/build-forge-code.yml` - Builds and publishes the FORGE research code container image (`forge-code`).
* `workflows/build-forge-db.yml` - Builds and publishes the ForgeDB PostgreSQL database container image (`forge-db`).

Both workflows use the same process: checkout the repository, authenticate with ghcr.io, build the Docker image, push the image, and generate an artifact attestation for supply chain security.

### Adapting for Your Own Repository

If you fork or clone this repository to a new GitHub organization, the workflows will automatically publish images under your organization's ghcr.io namespace. No changes to the workflow files are required. The `IMAGE_NAME` variable uses `github.repository_owner` to determine the organization name at build time.

---

## Changelog

### Version 1.0 (April 2026)
* Initial release of GitHub Actions workflow documentation.
* Author:
   * Emily D. Carpenter
   * Marketing & Data Sciences, Anderson College of Business and Computing
   * Regis University, Denver, CO, USA
   * Project: GENESIS - General Emergent Norms, Ethics, and Societies in Silico
   * Advisors: Dr. Douglas Hart, Dr. Kellen Sorauf