"""initial revision

Revision ID: b67a71ccf11e
Revises: 
Create Date: 2023-09-27 12:07:53.989729

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from sqlalchemy_pglogical import replicate_alembic

# revision identifiers, used by Alembic.
revision: str = "b67a71ccf11e"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.Unicode(200)),
        schema="public",
    )


def downgrade() -> None:
    op.drop_table("account")
