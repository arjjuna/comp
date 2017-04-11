"""added experience model

Revision ID: 0b8243afa390
Revises: b0e095620eee
Create Date: 2017-03-25 23:14:16.144873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b8243afa390'
down_revision = 'b0e095620eee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('experiences',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.String(length=250), nullable=True),
    sa.Column('company', sa.String(length=250), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(length=2500), nullable=True),
    sa.Column('prof_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['prof_id'], ['profs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('experiences')
    # ### end Alembic commands ###