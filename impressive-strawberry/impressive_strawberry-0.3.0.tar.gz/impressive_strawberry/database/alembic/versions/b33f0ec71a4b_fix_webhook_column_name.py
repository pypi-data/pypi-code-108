"""Fix webhook column name

Revision ID: b33f0ec71a4b
Revises: e8df1cc27545
Create Date: 2022-01-07 04:37:26.487484

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b33f0ec71a4b'
down_revision = 'e8df1cc27545'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('webhooks', 'type', new_column_name='kind')


def downgrade():
    op.alter_column('webhooks', 'kind', new_column_name='type')
