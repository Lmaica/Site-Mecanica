"""Adicionando coluna repet

Revision ID: 697292944d13
Revises: 3e73a9410a8b
Create Date: 2024-06-07 11:14:12.248683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '697292944d13'
down_revision = '3e73a9410a8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lembretestodos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('repet', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lembretestodos', schema=None) as batch_op:
        batch_op.drop_column('repet')

    # ### end Alembic commands ###
