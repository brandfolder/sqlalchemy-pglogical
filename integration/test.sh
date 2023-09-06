#!/usr/bin/env bash -ex

#
# Usage: start the containers with `docker compose up`, then run `test.sh``
#

docker compose down && docker compose rm -f 

pushd "$(git rev-parse --show-toplevel)"
rm dist/sqlalchemy_pglogical-*
poetry build

mv dist/sqlalchemy_pglogical-*.whl dist/sqlalchemy_pglogical-0.1.0-py3-none-any.whl

pushd integration

docker compose down && docker compose rm -f 
docker compose up --build -d

for host in primary logical; do
    timeout --foreground 90s bash -c "until docker compose exec ${host} pg_isready ; do sleep 0.5 ; done"
    sleep 0.5  # sometimes pg_isready is over-optimistic
    docker compose exec ${host} psql -U me -d mydb -c "CREATE EXTENSION IF NOT EXISTS pglogical;"
done

# set up pglogical replication
docker compose exec primary /scripts/create_publication.sh primary logical
docker compose exec logical /scripts/create_subscription.sh logical primary

exec docker compose exec app nox