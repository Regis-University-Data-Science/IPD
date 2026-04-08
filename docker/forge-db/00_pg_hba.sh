#!/bin/bash
# Replace password auth with trust for all connections
sed -i 's/host all all all scram-sha-256/host all all all trust/' "$PGDATA/pg_hba.conf"