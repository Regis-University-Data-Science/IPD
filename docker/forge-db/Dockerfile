# Ref: https://hub.docker.com/_/postgres
#
# Example build: 
#   docker build -t test-forge-db -f docker/forge-db/Dockerfile .
# Example to run: 
#   docker run -v ./data/postgres:/var/lib/postgresql/data -p 5433:5432 test-forge-db
# Access forge-db from shell:
#   psql -h platinum -p 5433 -U postgres -d forge

FROM postgres:16

ENV POSTGRES_DB=forge
ENV POSTGRES_HOST_AUTH_METHOD=trust

COPY work/forge/llm/IPD-LLM-Agents2/database/setup_forge_db.sql /docker-entrypoint-initdb.d/01_db_setup.sql
COPY docker/forge-db/setup_forge_db_grants.sql /docker-entrypoint-initdb.d/02_db_grants.sql
