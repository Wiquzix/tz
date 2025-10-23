"""initial

Revision ID: 001
Revises: 
Create Date: 2025-10-21 09:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    

    op.create_table('customers',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('date_created', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('uuid')
    )


    op.create_table('vegetables',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('weight', sa.Integer(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('length', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('uuid')
    )


    op.create_table('orders',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('vegetable_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.uuid'], ),
        sa.ForeignKeyConstraint(['vegetable_id'], ['vegetables.uuid'], ),
        sa.PrimaryKeyConstraint('uuid')
    )

def downgrade() -> None:

    op.drop_table('orders')
    op.drop_table('vegetables')
    op.drop_table('customers')

    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')