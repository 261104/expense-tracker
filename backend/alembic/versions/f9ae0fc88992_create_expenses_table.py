"""create expenses table

Revision ID: f9ae0fc88992
Revises:
Create Date: 2026-09-10 13:05:51.899482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9ae0fc88992'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    if not sa.inspect(connection).has_table("expenses"):
        op.create_table(
            "expenses",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("payment_method", sa.String(length=30), nullable=True),
            sa.Column("date", sa.Date(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("expenses")
