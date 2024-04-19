"""empty message

Revision ID: beed8da02afb
Revises: 
Create Date: 2024-04-13 05:07:48.778877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'beed8da02afb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('requests', schema=None) as batch_op:
        batch_op.alter_column('permission',
               existing_type=sa.VARCHAR(),
               type_=sa.Boolean(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('requests', schema=None) as batch_op:
        batch_op.alter_column('permission',
               existing_type=sa.Boolean(),
               type_=sa.VARCHAR(),
               existing_nullable=True)

    # ### end Alembic commands ###
