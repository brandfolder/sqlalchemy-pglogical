#!/usr/bin/env bash

if [[ -z "$1" || -z "$2" ]]; then
    echo "Usage: $0 <this host> <downstream host>"
    exit 1
fi

publisher=$1
subscriber=$2
psql -U me -d mydb -c "SELECT pglogical.create_node(
    node_name := '${publisher}',
    dsn := 'host=${publisher} port=5432 dbname=mydb user=me password=veryinsecure'
);" 
psql -U me -d mydb -c "SELECT pglogical.replication_set_add_all_tables('default', ARRAY['public']);"

# automatically assign new tables to the replication set.
# https://github.com/2ndQuadrant/pglogical#automatic-assignment-of-replication-sets-for-new-tables
psql -U me -d mydb -c "$(cat << 'EOF'
CREATE OR REPLACE FUNCTION pglogical_assign_repset()
RETURNS event_trigger AS $$
DECLARE obj record;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        IF obj.object_type = 'table' THEN
            IF obj.schema_name = 'config' THEN
                PERFORM pglogical.replication_set_add_table('configuration', obj.objid);
            ELSIF NOT obj.in_extension THEN
                PERFORM pglogical.replication_set_add_table('default', obj.objid);
            END IF;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER pglogical_assign_repset_trg
    ON ddl_command_end
    WHEN TAG IN ('CREATE TABLE', 'CREATE TABLE AS')
    EXECUTE PROCEDURE pglogical_assign_repset();
EOF
)"