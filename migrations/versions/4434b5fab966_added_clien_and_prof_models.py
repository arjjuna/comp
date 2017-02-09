"""Added Clien and Prof models

Revision ID: 4434b5fab966
Revises: 778fbb2a00c8
Create Date: 2017-02-09 10:58:25.333186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4434b5fab966'
down_revision = '778fbb2a00c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('about_me', sa.String(length=250), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('profs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=250), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profs')
    op.drop_table('clients')
    # ### end Alembic commands ###