"""Added day-month-year added to medication

Revision ID: 212c9da80a7b
Revises: 8a1636731f54
Create Date: 2024-11-06 16:17:44.685520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '212c9da80a7b'
down_revision = '8a1636731f54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.Date(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medications', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###