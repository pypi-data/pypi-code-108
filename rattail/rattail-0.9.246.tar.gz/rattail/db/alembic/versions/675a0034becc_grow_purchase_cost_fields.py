# -*- coding: utf-8 -*-
"""grow purchase cost fields

Revision ID: 675a0034becc
Revises: c10adeff4117
Create Date: 2021-10-10 19:57:33.360590

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '675a0034becc'
down_revision = 'c10adeff4117'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_item
    op.alter_column('purchase_item', 'catalog_unit_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('purchase_item', 'po_unit_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('purchase_item', 'invoice_case_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('purchase_item', 'invoice_unit_cost', type_=sa.Numeric(precision=10, scale=5))

    # purchase_credit
    op.alter_column('purchase_credit', 'invoice_case_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('purchase_credit', 'invoice_unit_cost', type_=sa.Numeric(precision=10, scale=5))

    # batch_purchase_row
    op.alter_column('batch_purchase_row', 'catalog_unit_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('batch_purchase_row', 'po_unit_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('batch_purchase_row', 'invoice_case_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('batch_purchase_row', 'invoice_unit_cost', type_=sa.Numeric(precision=10, scale=5))

    # batch_purchase_credit
    op.alter_column('batch_purchase_credit', 'invoice_case_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('batch_purchase_credit', 'invoice_unit_cost', type_=sa.Numeric(precision=10, scale=5))


def downgrade():

    # batch_purchase_credit
    op.alter_column('batch_purchase_credit', 'invoice_unit_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('batch_purchase_credit', 'invoice_case_cost', type_=sa.Numeric(precision=7, scale=3))

    # batch_purchase_row
    op.alter_column('batch_purchase_row', 'invoice_unit_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('batch_purchase_row', 'invoice_case_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('batch_purchase_row', 'po_unit_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('batch_purchase_row', 'catalog_unit_cost', type_=sa.Numeric(precision=7, scale=3))

    # purchase_credit
    op.alter_column('purchase_credit', 'invoice_unit_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('purchase_credit', 'invoice_case_cost', type_=sa.Numeric(precision=7, scale=3))

    # purchase_item
    op.alter_column('purchase_item', 'invoice_unit_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('purchase_item', 'invoice_case_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('purchase_item', 'po_unit_cost', type_=sa.Numeric(precision=7, scale=3))
    op.alter_column('purchase_item', 'catalog_unit_cost', type_=sa.Numeric(precision=7, scale=3))
