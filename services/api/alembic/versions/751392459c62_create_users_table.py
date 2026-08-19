"""create users table

Revision ID: 751392459c62
Revises: 
Create Date: 2026-08-18 13:12:31.845872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '751392459c62'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("role", sa.Enum('CTO', 'PM', 'DEV', name='user_role'), server_default='DEV', nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username")
    )

    op.create_index(op.f("idx_users_email"), "users", ["email"])
    op.create_index(op.f("idx_users_username"), "users", ["username"])

    op.execute("""
        CREATE TRIGGER trg_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS trg_users_updated_at ON users;")
    
    op.drop_index(op.f('idx_users_username'), table_name='users')
    op.drop_index(op.f('idx_users_email'), table_name='users')
    op.drop_table('users')
    
    op.execute("DROP FUNCTION IF EXISTS fn_update_updated_at();")

    op.execute("DROP TYPE IF EXISTS user_role;")
