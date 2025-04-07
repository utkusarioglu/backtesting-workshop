#!/bin/bash
set -e

echo 'Running migrations…'

function create_tablespace_path {
  tablespace_abspath=$1
  
  if [ -z "$tablespace_abspath" ]; then
    echo "Error: tablespace_abspath is required"
    exit 1;
  fi

  mkdir -p "$tablespace_abspath"
  chown -R postgres:postgres "$tablespace_abspath"
}

#
# Skipping tablespace path creation because postgres container runs as 999:999
# initcontainers are required to make tablespaces work
#
# create_tablespace_path '/tablespaces/backtesting-workshop'

function main {
  psql \
    -v ON_ERROR_STOP=1 \
    --username "${POSTGRES_USER}" \
    --dbname "${POSTGRES_DB}" \
    -c "\i /sql/migrations/init.sql"
}

main
