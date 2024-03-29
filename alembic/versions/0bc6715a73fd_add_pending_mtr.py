"""add_pending_mtr

Revision ID: 0bc6715a73fd
Revises: 40ed282ffb46
Create Date: 2022-10-06 18:35:25.175320

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "0bc6715a73fd"
down_revision = "40ed282ffb46"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "mtr_pending",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("creation_day", sa.Date(), nullable=True),
        sa.Column("file_name", sa.Text(), nullable=True),
        sa.Column("sections", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("mtr_pending")
    # ### end Alembic commands ###
