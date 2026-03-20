"""added user_id in generated images

Revision ID: cef04dfe0059
Revises: 1ff16d01d6b9
Create Date: 2026-03-20 10:22:41.634710

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cef04dfe0059"
down_revision: Union[str, Sequence[str], None] = "1ff16d01d6b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("generated_images") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_generated_images_user_id",
            "users",
            ["user_id"],
            ["id"],
        )
        batch_op.create_index("ind_generated_images_user_id", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("generated_images") as batch_op:
        batch_op.drop_index("ind_generated_images_user_id")
        batch_op.drop_constraint("fk_generated_images_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
