"""add role

Revision ID: e2476d2ab052
Revises: 6764cf66f538
Create Date: 2026-04-22 11:18:28.432092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql  # Added this import


# revision identifiers, used by Alembic.
revision: str = 'e2476d2ab052'
down_revision: Union[str, Sequence[str], None] = '6764cf66f538'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the ENUM type in Postgres first
    role_enum = postgresql.ENUM('USER', 'ADMIN', 'SUPERUSER', name='role')
    role_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add the columns. (Added server_default to role to prevent NOT NULL errors on existing rows)
    op.add_column('users', sa.Column('role', role_enum, nullable=False, server_default='USER'))
    op.add_column('users', sa.Column('resetpass_code', sa.String(), nullable=True))
    op.add_column('users', sa.Column('resetpass_expire', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'resetpass_expire')
    op.drop_column('users', 'resetpass_code')
    op.drop_column('users', 'role')
    
    # Drop the ENUM type
    role_enum = postgresql.ENUM('USER', 'ADMIN', 'SUPERUSER', name='role')
    role_enum.drop(op.get_bind(), checkfirst=True)