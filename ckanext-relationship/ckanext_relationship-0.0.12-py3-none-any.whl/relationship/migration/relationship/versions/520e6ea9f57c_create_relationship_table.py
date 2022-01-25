'''Create relationship table

Revision ID: aca2ff1d3ce4
Revises:
Create Date: 2021-07-02 14:40:37.719003

'''
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'aca2ff1d3ce4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'relationship_relationship',
        sa.Column('id', sa.Text, primary_key=True),
        sa.Column('subject_id', sa.Text, nullable=False),
        sa.Column('object_id', sa.Text, nullable=False),
        sa.Column('relation_type', sa.Text, nullable=False),
    )


def downgrade():
    op.drop_table('relationship_relationship')
