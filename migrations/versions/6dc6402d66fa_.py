"""empty message

Revision ID: 6dc6402d66fa
Revises: 3acb6c221afa
Create Date: 2017-03-26 01:26:20.043495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6dc6402d66fa'
down_revision = '3acb6c221afa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profs', sa.Column('city_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'profs', 'cities', ['city_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'profs', type_='foreignkey')
    op.drop_column('profs', 'city_id')
    # ### end Alembic commands ###