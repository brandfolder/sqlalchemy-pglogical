"""add index

Revision ID: c3d4de521f9a
Revises: 4b361a7c7bf3
Create Date: 2023-10-10 12:00:08.146646

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4de521f9a"
down_revision: Union[str, None] = "4b361a7c7bf3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        index_name="idx_account_name",
        table_name="account",
        columns=["name"],
        schema="public",
    )


def downgrade() -> None:
    op.drop_index(index_name="idx_account_name", table_name="account", schema="public")
