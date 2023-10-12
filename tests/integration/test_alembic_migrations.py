import pathlib
import time

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

wait_lsn = text("select pglogical.wait_slot_confirm_lsn(NULL, NULL)")


def wait_for_query_truthiness(sessionmaker_, query, truthy=True):
    for _ in range(30):
        # make the session inside the loop to make sure we're not holding any cursors, etc.
        with sessionmaker_() as session:
            session.execute(wait_lsn)
            maybe_results = session.execute(query)
            result = maybe_results.first()
            if (result is not None) == truthy:
                break
    return result


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
    logical_table = wait_for_query_truthiness(LogicalSession, table_query)
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
    logical_column = wait_for_query_truthiness(LogicalSession, column_query)
    assert primary_column is not None
    assert logical_column is not None


@pytest.mark.flaky(max_runs=3)
def test_drop_column_with_alembic(clean_primary, clean_secondary):
    config = Config(pathlib.Path(__file__).parent / "alembic.ini")
    command.upgrade(config, "4b361a7c7bf3")
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

    logical_column = wait_for_query_truthiness(LogicalSession, column_query)
    assert logical_column is not None

    command.downgrade(config, "b67a71ccf11e")

    logical_column = wait_for_query_truthiness(
        LogicalSession, column_query, truthy=False
    )
    assert logical_column is None


@pytest.mark.flaky(max_runs=3)
def test_add_and_drop_index(clean_primary, clean_secondary):
    config = Config(pathlib.Path(__file__).parent / "alembic.ini")
    command.upgrade(config, "c3d4de521f9a")
    logical_engine = create_engine(clean_secondary)
    LogicalSession = sessionmaker(logical_engine)

    index_query = text(
        """SELECT
                    indexname
                FROM
                    pg_indexes
                WHERE
                    indexname = 'idx_account_name';"""
    )

    logical_index = wait_for_query_truthiness(LogicalSession, index_query)
    assert logical_index is not None

    command.downgrade(config, "4b361a7c7bf3")

    logical_index = wait_for_query_truthiness(LogicalSession, index_query, truthy=False)
    assert logical_index is None


@pytest.mark.flaky(max_runs=3)
def test_add_and_drop_primary_key(clean_primary, clean_secondary):
    config = Config(pathlib.Path(__file__).parent / "alembic.ini")
    command.upgrade(config, "5907ff9d291e")
    logical_engine = create_engine(clean_secondary)
    LogicalSession = sessionmaker(logical_engine)

    index_query = text(
        """SELECT a.attname
                FROM   pg_index i
                JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                     AND a.attnum = ANY(i.indkey)
                WHERE  i.indrelid = 'new_table'::regclass
                AND    i.indisprimary;"""
    )

    logical_index = wait_for_query_truthiness(LogicalSession, index_query)
    assert logical_index is not None

    # can't test dropping primary keys because it's not a supported `operation`


@pytest.mark.flaky(max_runs=3)
def test_add_and_drop_unique_constraint(clean_primary, clean_secondary):
    config = Config(pathlib.Path(__file__).parent / "alembic.ini")
    command.upgrade(config, "2a9b320f3470")
    logical_engine = create_engine(clean_secondary)
    LogicalSession = sessionmaker(logical_engine)

    constraint_query = text(
        """SELECT constraint_name 
        FROM information_schema.key_column_usage 
        WHERE table_name = 'account' 
        AND constraint_name = 'account_name_unique';"""
    )

    logical_constraint = wait_for_query_truthiness(LogicalSession, constraint_query)
    assert logical_constraint is not None

    command.downgrade(config, "5907ff9d291e")

    logical_constraint = wait_for_query_truthiness(
        LogicalSession, constraint_query, truthy=False
    )
    assert logical_constraint is None
