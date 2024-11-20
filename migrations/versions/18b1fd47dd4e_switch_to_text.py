"""switch to text

Revision ID: 18b1fd47dd4e
Revises: f2f951d55927
Create Date: 2024-11-19 17:29:50.333153

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '18b1fd47dd4e'
down_revision = 'f2f951d55927'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medications', schema=None) as batch_op:
        batch_op.alter_column('days_taken',
               existing_type=sqlite.JSON(),
               type_=sa.String(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medications', schema=None) as batch_op:
        batch_op.alter_column('days_taken',
               existing_type=sa.String(),
               type_=sqlite.JSON(),
               existing_nullable=True)

    # ### end Alembic commands ###