from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import pytest


@pytest.fixture(scope="function")
def primary_session():
    engine = create_engine("postgresql://me:veryinsecure@primary/mydb")
    Session = sessionmaker(engine)
    with Session() as session:
        return session


@pytest.fixture(scope="function")
def logical_session():
    engine = create_engine("postgresql://me:veryinsecure@logical/mydb")
    Session = sessionmaker(engine)
    with Session() as session:
        return session


@pytest.fixture(scope="function")
def clean_logical_db(logical_session):
    logical_session.execute(text("DROP TABLE IF EXISTS users"))
    logical_session.commit()
    logical_session.close()
    return logical_session


@pytest.fixture(scope="function")
def clean_primary_db(primary_session):
    primary_session.execute(text("DROP TABLE IF EXISTS users"))
    primary_session.commit()
    primary_session.close()
    return primary_session