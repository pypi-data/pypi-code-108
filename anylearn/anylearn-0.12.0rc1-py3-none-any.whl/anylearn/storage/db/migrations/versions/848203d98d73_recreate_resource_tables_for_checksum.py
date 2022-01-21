"""Alter resource tables for checksum

Revision ID: 848203d98d73
Revises: 
Create Date: 2021-05-13 15:40:20.995359

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.schema import Column


# revision identifiers, used by Alembic.
revision = '848203d98d73'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'local_algorithm',
        sa.Column('id', sa.String(length=32), primary_key=True),
        sa.Column('checksum', sa.String(length=128), nullable=False),
    )
    op.create_table(
        'local_dataset',
        sa.Column('id', sa.String(length=32), primary_key=True),
        sa.Column('checksum', sa.String(length=128), nullable=False),
    )
    op.create_table(
        'local_model',
        sa.Column('id', sa.String(length=32), primary_key=True),
        sa.Column('checksum', sa.String(length=128), nullable=False),
    )
    op.create_table(
        'local_train_task',
        sa.Column('id', sa.String(length=32), primary_key=True),
        sa.Column('remote_state_sofar', sa.Integer, nullable=False),
        sa.Column('secret_key', sa.String(length=32), nullable=False),
        sa.Column('project_id', sa.String(length=32), nullable=False),
    )


def downgrade():
    # WARNING: all data will be lost
    op.drop_table('local_algorithm')
    op.drop_table('local_dataset')
    op.drop_table('local_model')
    op.drop_table('local_train_task')
