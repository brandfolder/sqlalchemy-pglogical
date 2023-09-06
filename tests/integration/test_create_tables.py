import time
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
        session.execute(text(f'DROP DATABASE IF EXISTS "{db_name}" '))
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


@pytest.fixture(scope="session")
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
    return connection_string


@pytest.fixture(scope="session")
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
    return connection_string


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)


def test_creates_tables(clean_primary, clean_secondary):
    from sqlalchemy_pglogical import replicate_ddl

    primary_engine = create_engine(clean_primary)
    PrimarySession = sessionmaker(primary_engine)
    logical_engine = create_engine(clean_secondary)
    LogicalSession = sessionmaker(logical_engine)

    table_query = text(
        """
    SELECT table_schema||'.'||table_name AS full_rel_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'"""
    )

    for Session in (PrimarySession, LogicalSession):
        # clean the database
        with Session() as session:
            session.execute(text("""DROP TABLE IF EXISTS users CASCADE"""))
            session.commit()
            session.close()
        # confirm it's really clean
        with Session() as session:
            tables = session.execute(table_query)
            assert tables.first() is None

    # make the tables
    Base.metadata.create_all(primary_engine)

    # confirm the tables got made
    with LogicalSession() as session:
        for _ in range(10):
            logical_tables = session.execute(table_query)
            table = logical_tables.first()
            if table is not None:
                break
            time.sleep(0.5)
    assert table is not None
