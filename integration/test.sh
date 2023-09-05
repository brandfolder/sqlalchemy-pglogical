#!/usr/bin/env bash -ex

#
# Usage: start the containers with `docker compose up`, then run `test.sh``
#

if [[ "$1" = "rebuild" ]]; then
    docker compose down && docker compose rm -f 
fi
docker compose up --build -d

sleep 5

for host in primary logical; do
    docker compose exec ${host} psql -U me -d mydb -c "CREATE EXTENSION IF NOT EXISTS pglogical;"
done
# set up pglogical replication
docker compose exec primary /scripts/create_publication.sh primary logical
docker compose exec logical /scripts/create_subscription.sh logical primary

docker compose exec app poetry install
exec docker compose exec app poetry run pytest