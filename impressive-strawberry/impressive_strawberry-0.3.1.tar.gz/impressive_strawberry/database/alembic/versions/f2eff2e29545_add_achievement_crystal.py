"""Add achievement crystal

Revision ID: f2eff2e29545
Revises: 713b76b25d40
Create Date: 2021-11-23 18:27:10.144177

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f2eff2e29545'
down_revision = '713b76b25d40'
branch_labels = None
depends_on = None

counter = 0


def generate_crystal():
    global counter
    counter += 1
    return f"legacy-{counter}"


def upgrade():
    op.add_column('achievements',
                  sa.Column('crystal', sa.String(), nullable=False, server_default=sa.func.substr(sa.func.md5(sa.func.random().cast(sa.String)), 0, 25)))
    op.alter_column('achievements', 'crystal', server_default=None)
    op.create_unique_constraint('achievements_group_id_crystal_key', 'achievements', ['group_id', 'crystal'])


def downgrade():
    op.drop_constraint('achievements_group_id_crystal_key', 'achievements', type_='unique')
    op.drop_column('achievements', 'crystal')
