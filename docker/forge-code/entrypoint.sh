#!/bin/bash
# Ref: https://www.docker.com/blog/docker-best-practices-choosing-between-run-cmd-and-entrypoint/

# Create the user for the Docker container
FORGE_USER=${FORGE_USER:-mcp}
#useradd -d /app -s /bin/bash "$FORGE_USER"
useradd -u "$FORGE_UID" -d /app -s /bin/bash "$FORGE_USER"

# Preserve K3s environment variables for the user's login shell
env | grep -E '^(FORGE_|OLLAMA_)' >> /app/.bashrc

# Set user's permissions on the research code
chown -R "$FORGE_USER":"$FORGE_USER" /app

# Open login shell as the user
exec su "$FORGE_USER"