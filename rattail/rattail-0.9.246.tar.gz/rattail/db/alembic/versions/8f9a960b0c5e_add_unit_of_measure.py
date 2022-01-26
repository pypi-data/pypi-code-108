# -*- coding: utf-8 -*-
"""add unit_of_measure

Revision ID: 8f9a960b0c5e
Revises: a3a6e2f7c9a5
Create Date: 2021-01-21 14:06:50.220316

"""

# revision identifiers, used by Alembic.
revision = '8f9a960b0c5e'
down_revision = 'a3a6e2f7c9a5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # unit_of_measure
    op.create_table('unit_of_measure',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('abbreviation', sa.String(length=20), nullable=False),
                    sa.Column('sil_code', sa.String(length=4), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('abbreviation', name='unit_of_measure_uq_abbreviation')
    )
    op.create_table('unit_of_measure_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('abbreviation', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('sil_code', sa.String(length=4), autoincrement=False, nullable=True),
                    sa.Column('notes', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_unit_of_measure_version_end_transaction_id'), 'unit_of_measure_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_unit_of_measure_version_operation_type'), 'unit_of_measure_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_unit_of_measure_version_transaction_id'), 'unit_of_measure_version', ['transaction_id'], unique=False)


def downgrade():

    # unit_of_measure
    op.drop_index(op.f('ix_unit_of_measure_version_transaction_id'), table_name='unit_of_measure_version')
    op.drop_index(op.f('ix_unit_of_measure_version_operation_type'), table_name='unit_of_measure_version')
    op.drop_index(op.f('ix_unit_of_measure_version_end_transaction_id'), table_name='unit_of_measure_version')
    op.drop_table('unit_of_measure_version')
    op.drop_table('unit_of_measure')
