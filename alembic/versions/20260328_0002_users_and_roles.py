"""users and roles

Revision ID: 20260328_0002
Revises: 20260328_0001
Create Date: 2026-03-28 19:35:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260328_0002"
down_revision = "20260328_0001"
branch_labels = None
depends_on = None


user_role_enum_pg = postgresql.ENUM("ADMIN", "EDITOR", "READER", name="userrole", create_type=False)
user_role_enum_generic = sa.Enum("ADMIN", "EDITOR", "READER", name="userrole")


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        user_role_enum_pg.create(bind, checkfirst=True)
        role_column_type = user_role_enum_pg
    else:
        role_column_type = user_role_enum_generic

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", role_column_type, nullable=False, server_default="READER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        user_role_enum_pg.drop(bind, checkfirst=True)
