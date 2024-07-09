"""Adicionando coluna repet

Revision ID: 3e73a9410a8b
Revises: 
Create Date: 2022-06-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3e73a9410a8b'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('lembretestodos', sa.Column('repet', sa.String(), nullable=False))

def downgrade():
    op.drop_column('lembretestodos', 'repet')
