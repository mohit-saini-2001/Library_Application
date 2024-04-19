"""empty message

Revision ID: c7695a9e032f
Revises: 4ec43438a776
Create Date: 2024-04-13 14:39:19.268270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7695a9e032f'
down_revision = '4ec43438a776'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('requ')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('requ',
    sa.Column('r_id', sa.INTEGER(), nullable=False),
    sa.Column('book_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('permission', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('r_id')
    )
    # ### end Alembic commands ###