"""Add achievement token

Revision ID: 00755101936c
Revises: 02aa20f04fa4
Create Date: 2021-12-18 01:23:37.686505

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '00755101936c'
down_revision = '02aa20f04fa4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('achievements',
                  sa.Column('token', sa.String(), nullable=False, server_default=sa.func.substr(sa.func.md5(sa.func.random().cast(sa.String)), 0, 25)))


def downgrade():
    op.drop_column('achievements', 'token')
