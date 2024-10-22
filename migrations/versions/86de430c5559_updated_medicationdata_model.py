"""Updated medicationData model

Revision ID: 86de430c5559
Revises: 262b234637db
Create Date: 2024-10-22 08:12:14.477437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86de430c5559'
down_revision = '262b234637db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medicationData', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.Integer(), nullable=False))
        batch_op.alter_column('drug_name',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               nullable=False)
        batch_op.alter_column('medical_condition',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               nullable=False)
        batch_op.alter_column('medical_condition_description',
               existing_type=sa.TEXT(),
               type_=sa.String(length=200),
               existing_nullable=True)
        batch_op.alter_column('activity',
               existing_type=sa.TEXT(),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('rx_otc',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('pregnancy_category',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('csa',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('alcohol',
               existing_type=sa.TEXT(),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('rating',
               existing_type=sa.TEXT(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('no_of_reviews',
               existing_type=sa.TEXT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('medical_condition_url',
               existing_type=sa.TEXT(),
               type_=sa.String(length=200),
               existing_nullable=True)
        batch_op.alter_column('drug_link',
               existing_type=sa.TEXT(),
               type_=sa.String(length=200),
               existing_nullable=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('medicationData', schema=None) as batch_op:
        batch_op.alter_column('drug_link',
               existing_type=sa.String(length=200),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('medical_condition_url',
               existing_type=sa.String(length=200),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('no_of_reviews',
               existing_type=sa.Integer(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('rating',
               existing_type=sa.Float(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('alcohol',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('csa',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('pregnancy_category',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('rx_otc',
               existing_type=sa.String(length=50),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('activity',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('medical_condition_description',
               existing_type=sa.String(length=200),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('medical_condition',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('drug_name',
               existing_type=sa.String(length=100),
               type_=sa.TEXT(),
               nullable=True)
        batch_op.drop_column('id')

    # ### end Alembic commands ###
