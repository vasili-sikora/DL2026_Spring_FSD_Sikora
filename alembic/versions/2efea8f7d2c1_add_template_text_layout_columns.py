"""add template text layout columns

Revision ID: 2efea8f7d2c1
Revises: 8277fa1f0728
Create Date: 2026-03-21 17:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op  # type: ignore[attr-defined]

# revision identifiers, used by Alembic.
revision: str = "2efea8f7d2c1"
down_revision: Union[str, Sequence[str], None] = "8277fa1f0728"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("templates") as batch_op:
        batch_op.add_column(sa.Column("top_text_x", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("top_text_y", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("top_text_width", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("bottom_text_x", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("bottom_text_y", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("bottom_text_width", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("templates") as batch_op:
        batch_op.drop_column("bottom_text_width")
        batch_op.drop_column("bottom_text_y")
        batch_op.drop_column("bottom_text_x")
        batch_op.drop_column("top_text_width")
        batch_op.drop_column("top_text_y")
        batch_op.drop_column("top_text_x")
