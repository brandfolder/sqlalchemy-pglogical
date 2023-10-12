"""create primary key

Revision ID: 5907ff9d291e
Revises: c3d4de521f9a
Create Date: 2023-10-11 09:39:31.717006

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5907ff9d291e"
down_revision: Union[str, None] = "c3d4de521f9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("new_table", sa.Column("id", sa.INTEGER), schema="public")
    op.create_primary_key("new_table_id_pk", "new_table", ["id"], schema="public")


def downgrade() -> None:
    op.drop_table("new_table", schema="public")
