"""add_creation_day_indexes

Revision ID: a1b2c3d4e5f6
Revises: f81d76ccde31
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "f81d76ccde31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_cr_creation_day"), "cr", ["creation_day"], unique=False)
    op.create_index(op.f("ix_cr_diffs_creation_day"), "cr_diffs", ["creation_day"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cr_diffs_creation_day"), table_name="cr_diffs")
    op.drop_index(op.f("ix_cr_creation_day"), table_name="cr")
