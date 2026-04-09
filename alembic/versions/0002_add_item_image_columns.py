"""Add item image columns."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_add_item_image_columns"
down_revision = "0001_create_items_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("items") as batch_op:
        batch_op.add_column(sa.Column("image_data", sa.LargeBinary(), nullable=True))
        batch_op.add_column(sa.Column("image_mime_type", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("image_filename", sa.String(length=255), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("items") as batch_op:
        batch_op.drop_column("image_filename")
        batch_op.drop_column("image_mime_type")
        batch_op.drop_column("image_data")
