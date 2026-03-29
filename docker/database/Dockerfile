# Ref: https://hub.docker.com/_/postgres
# Example build: 
#   docker build -t test-database -f docker/database/Dockerfile .
# Example to run: 
#   docker run -e POSTGRES_PASSWORD=forge -v ./data/postgres:/var/lib/postgresql/data -p 5433:5432 test-database
# Access test-database from shell:
#   psql -h platinum -p 5433 -U postgres -d forge

FROM postgres:16

ENV POSTGRES_DB=forge
ENV POSTGRES_PASSWORD=forge

COPY work/forge/llm/IPD-LLM-Agents2/database/setup_forge_db.sql /docker-entrypoint-initdb.d/