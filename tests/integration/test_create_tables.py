import time

from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

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
