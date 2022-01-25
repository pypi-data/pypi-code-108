"""Add webhook type

Revision ID: 02aa20f04fa4
Revises: f2eff2e29545
Create Date: 2021-12-01 09:30:01.939155

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '02aa20f04fa4'
down_revision = 'f2eff2e29545'
branch_labels = None
depends_on = None


def upgrade():
    webhooktype = sa.Enum('STRAWBERRY', 'DISCORD', name='webhooktype')
    webhooktype.create(op.get_bind(), checkfirst=True)

    op.alter_column('applications', 'webhook', new_column_name='webhook_url')
    op.add_column('applications', sa.Column('webhook_type', webhooktype, nullable=False, server_default="STRAWBERRY"))


def downgrade():
    op.alter_column('applications', 'webhook_url', new_column_name='webhook')
    op.drop_column('applications', 'webhook_type')
    op.execute("DROP TYPE webhooktype")
