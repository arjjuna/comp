"""empty message

Revision ID: 311f6d891a22
Revises: c4f6618fc778
Create Date: 2017-02-25 11:18:32.403504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '311f6d891a22'
down_revision = 'c4f6618fc778'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('seen', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'seen')
    # ### end Alembic commands ###