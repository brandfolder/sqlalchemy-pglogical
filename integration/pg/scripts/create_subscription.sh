#!/usr/bin/env bash

if [[ -z "$1" || -z "$2" ]]; then 
    echo "Usage: $0 <subscriber hostname> <publisher hostname>"
    exit 1
fi

subscriber=$1
publisher=$2


psql -U me -d mydb -c "SELECT pglogical.create_node(
    node_name := '${subscriber}',
    dsn := 'host=${subscriber} port=5432 dbname=mydb user=me password=veryinsecure'
);"

psql -U me -d mydb -c "SELECT pglogical.create_subscription(
    subscription_name := '${subscriber}',
    provider_dsn := 'host=${publisher} port=5432 dbname=mydb user=me password=veryinsecure'
);"

psql -U me -d mydb -c "SELECT pglogical.wait_for_subscription_sync_complete('${subscriber}');"