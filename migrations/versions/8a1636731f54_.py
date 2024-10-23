"""empty message

Revision ID: 8a1636731f54
Revises: 41af7d46ac02
Create Date: 2024-10-23 07:16:50.130882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a1636731f54'
down_revision = '41af7d46ac02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medications', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
