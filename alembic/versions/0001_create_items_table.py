"""Create items table."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_create_items_table"
down_revision = None
branch_labels = None
depends_on = None

item_type_enum = sa.Enum("LOST", "FOUND", name="itemtype")
item_status_enum = sa.Enum("OPEN", "RESOLVED", name="itemstatus")


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("location", sa.String(length=120), nullable=False),
        sa.Column("contact", sa.String(length=120), nullable=False),
        sa.Column("item_type", item_type_enum, nullable=False),
        sa.Column("status", item_status_enum, nullable=False, server_default="OPEN"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_items_id", "items", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_items_id", table_name="items")
    op.drop_table("items")
    item_status_enum.drop(op.get_bind(), checkfirst=True)
    item_type_enum.drop(op.get_bind(), checkfirst=True)
