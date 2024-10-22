"""added time an days to medication

Revision ID: 6fdffdb9aa91
Revises: 4e1bd7f4b540
Create Date: 2024-10-22 15:47:58.302404

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6fdffdb9aa91"
down_revision = "4e1bd7f4b540"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("medications", schema=None) as batch_op:
        batch_op.alter_column(
            "time_of_day",
            existing_type=sa.VARCHAR(length=50),
            nullable=False,
            server_default="as Needed",
        )
        batch_op.alter_column(
            "days_of_week",
            existing_type=sa.VARCHAR(length=50),
            nullable=False,
            server_default="all",
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("medications", schema=None) as batch_op:
        batch_op.alter_column(
            "days_of_week", existing_type=sa.VARCHAR(length=50), nullable=True
        )
        batch_op.alter_column(
            "time_of_day", existing_type=sa.VARCHAR(length=50), nullable=True
        )

    # ### end Alembic commands ###