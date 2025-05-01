$Name = docker -c u-Boulanger container ls --format '{{.Names}}' | Select-String -Pattern '(?i)postgres$'
docker -c u-Boulanger exec -it $Name sh -c 'PGPASSWORD=postgres psql -U postgres -d postgres'
