import time

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from example_app.models import Base


def test_creates_tables():
    from sqlalchemy_pglogical import replicate_ddl

    primary_engine = create_engine("postgresql://me:veryinsecure@primary/mydb")
    PrimarySession = sessionmaker(primary_engine)
    logical_engine = create_engine("postgresql://me:veryinsecure@logical/mydb")
    LogicalSession = sessionmaker(logical_engine)

    table_query = text(
        """
    SELECT table_schema||'.'||table_name AS full_rel_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'"""
    )
    drop_query = text("""DROP TABLE IF EXISTS users CASCADE""")

    for Session in (PrimarySession, LogicalSession):
        # clean the database
        with Session() as session:
            session.execute(drop_query)
            session.commit()
            session.close()
        # confirm it's really clean
        with Session() as session:
            tables = session.execute(table_query)
            assert tables.first() is None

    # make the tables
    Base.metadata.create_all(primary_engine)

    # time.sleep(10)

    # confirm the tables got made
    with LogicalSession() as session:
        for _ in range(10):
            logical_tables = session.execute(table_query)
            table = logical_tables.first()
            if table is not None:
                break
            time.sleep(0.5)
    assert table is not None
