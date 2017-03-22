"""empty message

Revision ID: 613d0fdf26e7
Revises: 4a160bc6affe
Create Date: 2017-02-27 14:50:46.329049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '613d0fdf26e7'
down_revision = '4a160bc6affe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bookings', sa.Column('client_validated', sa.Boolean(), nullable=True))
    op.add_column('bookings', sa.Column('prof_validated', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bookings', 'prof_validated')
    op.drop_column('bookings', 'client_validated')
    # ### end Alembic commands ###
