"""added strict rule for user_id not null

Revision ID: 8277fa1f0728
Revises: cef04dfe0059
Create Date: 2026-03-20 10:31:46.206221

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8277fa1f0728"
down_revision: Union[str, Sequence[str], None] = "cef04dfe0059"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("generated_images") as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("generated_images") as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=True)
