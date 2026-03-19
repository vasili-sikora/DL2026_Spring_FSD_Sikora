"""renamed id_admin to id_admin

Revision ID: 1ff16d01d6b9
Revises: 1bc6715ed4b7
Create Date: 2026-03-17 18:49:28.837306

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1ff16d01d6b9"
down_revision: Union[str, Sequence[str], None] = "1bc6715ed4b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("id_admin", new_column_name="is_admin")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("is_admin", new_column_name="id_admin")
