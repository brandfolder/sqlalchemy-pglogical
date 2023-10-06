"""add column - this replicates a real-world bug

Revision ID: 4b361a7c7bf3
Revises: b67a71ccf11e
Create Date: 2023-09-27 12:37:43.934215

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from sqlalchemy_pglogical import replicate_alembic

# revision identifiers, used by Alembic.
revision: str = "4b361a7c7bf3"
down_revision: Union[str, None] = "b67a71ccf11e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "account",
        sa.Column("new_column", sa.String(), server_default=""),
        schema="public",
    )


def downgrade() -> None:
    op.drop_column("users")
