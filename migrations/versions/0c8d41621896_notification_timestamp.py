"""Notification timestamp

Revision ID: 0c8d41621896
Revises: a40b43ef91a0
Create Date: 2017-03-30 20:53:50.782560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c8d41621896'
down_revision = 'a40b43ef91a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notifications', sa.Column('timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notifications', 'timestamp')
    # ### end Alembic commands ###
