# -*- coding: utf-8; -*-
"""add ifps_plu

Revision ID: ef398701ffc6
Revises: c8981df473d0
Create Date: 2020-12-06 16:54:34.622596

"""

# revision identifiers, used by Alembic.
revision = 'ef398701ffc6'
down_revision = 'c8981df473d0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # ifps_plu
    op.create_table('ifps_plu',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('plu', sa.Integer(), nullable=False),
                    sa.Column('category', sa.String(length=100), nullable=True),
                    sa.Column('commodity', sa.String(length=100), nullable=True),
                    sa.Column('variety', sa.Text(), nullable=True),
                    sa.Column('size', sa.String(length=100), nullable=True),
                    sa.Column('measurements_north_america', sa.String(length=255), nullable=True),
                    sa.Column('measurements_rest_of_world', sa.String(length=255), nullable=True),
                    sa.Column('restrictions_notes', sa.Text(), nullable=True),
                    sa.Column('botanical_name', sa.String(length=100), nullable=True),
                    sa.Column('aka', sa.Text(), nullable=True),
                    sa.Column('revision_date', sa.DateTime(), nullable=True),
                    sa.Column('date_added', sa.DateTime(), nullable=True),
                    sa.Column('gpc', sa.String(length=100), nullable=True),
                    sa.Column('image', sa.String(length=255), nullable=True),
                    sa.Column('image_source', sa.String(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('plu', name='ifps_plu_uq_plu')
    )
    op.create_table('ifps_plu_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('plu', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('category', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('commodity', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('variety', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('size', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('measurements_north_america', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('measurements_rest_of_world', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('restrictions_notes', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('botanical_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('aka', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('revision_date', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('date_added', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('gpc', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('image', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('image_source', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_ifps_plu_version_end_transaction_id'), 'ifps_plu_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_ifps_plu_version_operation_type'), 'ifps_plu_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_ifps_plu_version_transaction_id'), 'ifps_plu_version', ['transaction_id'], unique=False)


def downgrade():

    # ifps_plu
    op.drop_index(op.f('ix_ifps_plu_version_transaction_id'), table_name='ifps_plu_version')
    op.drop_index(op.f('ix_ifps_plu_version_operation_type'), table_name='ifps_plu_version')
    op.drop_index(op.f('ix_ifps_plu_version_end_transaction_id'), table_name='ifps_plu_version')
    op.drop_table('ifps_plu_version')
    op.drop_table('ifps_plu')
