"""empty message

Revision ID: a21b737d811f
Revises: 45b46e720f7e
Create Date: 2024-12-15 23:38:07.484631

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a21b737d811f"
down_revision = "45b46e720f7e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "actions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", name="action_status"),
            nullable=True,
        ),
        sa.Column("is_enabled", sa.Boolean(), nullable=True),
        sa.Column("values", sa.ARRAY(sa.String()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    op.add_column("messages", sa.Column("tag_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "messages", "tags", ["tag_id"], ["id"])
    op.add_column("tags", sa.Column("mainflux_channel_uuid", sa.UUID(), nullable=True))
    op.create_unique_constraint(None, "tags", ["name"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "tags", type_="unique")
    op.drop_column("tags", "mainflux_channel_uuid")
    op.drop_constraint(None, "messages", type_="foreignkey")
    op.drop_column("messages", "tag_id")
    op.drop_table("actions")
    # ### end Alembic commands ###