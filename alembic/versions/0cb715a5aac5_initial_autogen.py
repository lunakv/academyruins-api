"""initial_autogen

Revision ID: 0cb715a5aac5
Revises:
Create Date: 2022-09-28 11:30:45.896529

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0cb715a5aac5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cr",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("creation_day", sa.Date(), nullable=True),
        sa.Column("set_code", sa.String(length=5), nullable=True),
        sa.Column("set_name", sa.String(length=50), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("file_name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cr_pending",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("creation_day", sa.Date(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("file_name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ipg",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("creation_day", sa.Date(), nullable=True),
        sa.Column("file_name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ipg_creation_day"), "ipg", ["creation_day"], unique=False)
    op.create_table(
        "mtr",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=True),
        sa.Column("creation_day", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mtr_creation_day"), "mtr", ["creation_day"], unique=False)
    op.create_table(
        "redirects",
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("link", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("resource"),
    )
    op.create_table(
        "redirects_pending",
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("link", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("resource"),
    )
    op.create_table(
        "cr_diffs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("creation_day", sa.Date(), nullable=False),
        sa.Column("changes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("dest_id", sa.Integer(), nullable=False),
        sa.Column("bulletin_url", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dest_id"],
            ["cr.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["cr.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cr_diffs_pending",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("creation_day", sa.Date(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("dest_id", sa.Integer(), nullable=False),
        sa.Column("changes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["dest_id"], ["cr_pending.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["cr.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("cr_diffs_pending")
    op.drop_table("cr_diffs")
    op.drop_table("redirects_pending")
    op.drop_table("redirects")
    op.drop_index(op.f("ix_mtr_creation_day"), table_name="mtr")
    op.drop_table("mtr")
    op.drop_index(op.f("ix_ipg_creation_day"), table_name="ipg")
    op.drop_table("ipg")
    op.drop_table("cr_pending")
    op.drop_table("cr")
    # ### end Alembic commands ###
