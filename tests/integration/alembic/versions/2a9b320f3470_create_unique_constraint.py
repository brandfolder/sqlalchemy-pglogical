"""create unique constraint

Revision ID: 2a9b320f3470
Revises: 5907ff9d291e
Create Date: 2023-10-11 10:23:25.627671

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a9b320f3470"
down_revision: Union[str, None] = "5907ff9d291e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "account_name_unique", "account", ["name"], schema="public"
    )


def downgrade() -> None:
    op.drop_constraint("account_name_unique", "account", schema="public")
