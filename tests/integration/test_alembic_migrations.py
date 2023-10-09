import pathlib
import time

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

wait_lsn = text("select pglogical.wait_slot_confirm_lsn(NULL, NULL)")


@pytest.mark.flaky(max_runs=3)
def test_create_with_alembic(clean_primary, clean_secondary):
    primary_engine = create_engine(clean_primary)
    PrimarySession = sessionmaker(primary_engine)
    logical_engine = create_engine(clean_secondary)
    LogicalSession = sessionmaker(logical_engine)
    config = Config(pathlib.Path(__file__).parent / "alembic.ini")
    command.upgrade(config, "b67a71ccf11e")
    # confirm the tables got made
    table_query = text(
        """
    SELECT table_schema||'.'||table_name AS full_rel_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'"""
    )

    with PrimarySession() as primary_session:
        primary_session.execute(wait_lsn)
        primary_tables = primary_session.execute(table_query)
        primary_table = primary_tables.first()
    for _ in range(30):
        # make the session inside the loop to make sure we're not holding any cursors, etc.
        with LogicalSession() as logical_session:
            logical_session.execute(wait_lsn)
            logical_tables = logical_session.execute(table_query)
            logical_table = logical_tables.first()
            if logical_table is not None:
                break
            time.sleep(0.5)

    assert primary_table is not None
    assert logical_table is not None


@pytest.mark.flaky(max_runs=3)
def test_add_column_with_alembic(clean_primary, clean_secondary):
    config = Config(pathlib.Path(__file__).parent / "alembic.ini")
    command.upgrade(config, "4b361a7c7bf3")
    primary_engine = create_engine(clean_primary)
    PrimarySession = sessionmaker(primary_engine)
    logical_engine = create_engine(clean_secondary)
    LogicalSession = sessionmaker(logical_engine)

    column_query = text(
        """SELECT
                    column_name
                FROM
                    information_schema.columns
                WHERE
                    table_name = 'account'
                    and column_name = 'new_column';"""
    )

    with PrimarySession() as primary_session:
        primary_session.execute(wait_lsn)
        primary_columns = primary_session.execute(column_query)
        primary_column = primary_columns.first()
    for _ in range(30):
        with LogicalSession() as logical_session:
            logical_session.execute(wait_lsn)
            logical_columns = logical_session.execute(column_query)
            logical_column = logical_columns.first()
            if logical_column is not None:
                break
            time.sleep(0.5)

    assert primary_column is not None
    assert logical_column is not None
