"""Create Balances and Trades tables

Revision ID: 7d42c6c69b3a
Revises: 
Create Date: 2021-02-12 17:25:44.640224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d42c6c69b3a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'balances',
        sa.Column('balance_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('time_frame', sa.String(), nullable=False),
        sa.Column('free', sa.Numeric(), nullable=False),
        sa.Column('locked', sa.Numeric(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()))

    op.create_table(
        'trades',
        sa.Column('trade_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('time_frame', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Numeric(), nullable=False),
        sa.Column('stop_loss', sa.Numeric(), nullable=False),
        sa.Column('buy_price', sa.Numeric(), nullable=False),
        sa.Column('sell_price', sa.Numeric(), nullable=True),
        sa.Column('profit', sa.Numeric(), nullable=True),
        sa.Column('side', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('balance_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        constraint_name='trades_balance_id_fkey',
        source_table='trades',
        referent_table='balances',
        local_cols=['balance_id'],
        remote_cols=['balance_id'])


def downgrade():
    op.drop_table('trades')
    op.drop_table('balances')
