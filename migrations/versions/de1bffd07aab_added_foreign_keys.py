"""added foreign keys

Revision ID: de1bffd07aab
Revises: 72df2fcbf99c
Create Date: 2024-10-22 13:30:35.010475

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "de1bffd07aab"
down_revision = "72df2fcbf99c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("medications", schema=None) as batch_op:
        batch_op.add_column(sa.Column("medication_data", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_medications_medication_data",
            "medicationData",
            ["medication_data"],
            ["id"],
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("medications", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_column("medication_data")

    # ### end Alembic commands ###
