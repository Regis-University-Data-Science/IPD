# Ref: https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/
# Example build: docker build -t test-forge -f docker/forge/Dockerfile .
# Example to run: docker run -it -e FORGE_USER=carpenter test-forge

FROM python:3.12

WORKDIR /app

# Install the application dependencies (i.e. Python Libraries)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code from the repo to the Docker Image Working Directory
COPY work/forge/llm/IPD-LLM-Agents2/ .
#EXPOSE 8080

# Copy the entrypoint script and make it executable
COPY docker/forge/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# User creation and code deployment handled at runtime by entrypoint script
# Default username is 'mcp' if FORGE_USER is not provided
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]