from contextlib import contextmanager

import pytest
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


@contextmanager
def transactionless_session(sessionmaker_):
    # break out of our transaction. see https://stackoverflow.com/questions/57186725/can-i-execute-query-via-sqlalchemy-without-transaction
    with sessionmaker_() as session:
        session.connection().execute(text("COMMIT"))
        yield session


def create_database_with_node(db_name):
    """
    Create a database in an existing postgres instance, enable pglogical, and create a pglogical node
    """
    username = "me"
    password = "veryinsecure"
    hostname = "localhost"
    dsn = f"host={hostname} port=5432 dbname={db_name} user={username} password={password}"
    connection_string = f"postgresql://me:veryinsecure@localhost/{db_name}"

    # connect with another db
    mydb_engine = create_engine("postgresql://me:veryinsecure@localhost/mydb")
    MyDBSession = sessionmaker(mydb_engine)

    with transactionless_session(MyDBSession) as session:
        session.execute(
            text(
                f"""
        SELECT 
            pg_terminate_backend(pid) 
        FROM 
            pg_stat_activity 
        WHERE 
            -- don't kill my own connection!
            pid <> pg_backend_pid()
            -- don't kill the connections to other databases
            AND datname = '{db_name}'
    """
            )
        )
        session.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
        session.execute(text(f'CREATE DATABASE "{db_name}"'))

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)

    with transactionless_session(Session) as session:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS pglogical"))
    with transactionless_session(Session) as session:
        session.execute(
            text(
                f"""SELECT pglogical.create_node(
                        node_name := '{db_name}_node',
                        dsn := '{dsn}'
                        )"""
            )
        )

    return connection_string


@pytest.fixture(scope="function")
def clean_primary():
    connection_string = create_database_with_node("primary")
    engine = create_engine(connection_string)
    Session = sessionmaker(engine)

    with transactionless_session(Session) as session:
        session.execute(
            text(
                f"SELECT pglogical.replication_set_add_all_tables('default', ARRAY['public'])"
            )
        )
    yield connection_string

    with transactionless_session(Session) as session:
        session.execute(text(f"SELECT pglogical.drop_node('primary_node')"))


@pytest.fixture(scope="function")
def clean_secondary():
    connection_string = create_database_with_node("secondary")

    engine = create_engine(connection_string)
    Session = sessionmaker(engine)

    with transactionless_session(Session) as session:
        session.execute(
            text(
                """SELECT pglogical.create_subscription(
        subscription_name := 'secondary_node',
        provider_dsn := 'host=localhost port=5432 dbname=primary user=me password=veryinsecure'
        );"""
            )
        )
    yield connection_string
    with transactionless_session(Session) as session:
        session.execute(
            text(
                "SELECT pglogical.drop_subscription(subscription_name := 'secondary_node')"
            )
        )
        session.execute(text("SELECT pglogical.drop_node('secondary_node')"))
