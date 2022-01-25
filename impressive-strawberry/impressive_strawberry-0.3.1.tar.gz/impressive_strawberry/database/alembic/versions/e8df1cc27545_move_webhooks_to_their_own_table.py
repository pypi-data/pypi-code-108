"""Move webhooks to their own table

Revision ID: e8df1cc27545
Revises: 00755101936c
Create Date: 2022-01-05 00:22:01.771728

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e8df1cc27545'
down_revision = '00755101936c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('webhooks',
                    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('url', sa.String(), nullable=False),
                    sa.Column('type', sa.Enum('STRAWBERRY', 'DISCORD', name='webhookkind'), nullable=False),
                    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.drop_column('applications', 'webhook_type')
    op.drop_column('applications', 'webhook_url')
    op.execute("DROP TYPE webhooktype")


def downgrade():
    op.drop_table('webhooks')
    op.execute("DROP TYPE webhookkind")
    webhooktype = sa.Enum('STRAWBERRY', 'DISCORD', name='webhooktype')
    webhooktype.create(op.get_bind(), checkfirst=True)
    op.add_column('applications', sa.Column('webhook_url', sa.String(), nullable=False))
    op.add_column('applications', sa.Column('webhook_type', webhooktype, nullable=False, server_default="STRAWBERRY"))
