"""original picture

Revision ID: f7acddbf88fe
Revises: 1930dfe33ef7
Create Date: 2017-03-28 16:25:05.954391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7acddbf88fe'
down_revision = '1930dfe33ef7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('original_picture', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'original_picture')
    # ### end Alembic commands ###
