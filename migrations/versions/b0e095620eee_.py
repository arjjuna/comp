"""empty message

Revision ID: b0e095620eee
Revises: dab3a6e08826
Create Date: 2017-03-25 19:54:42.225621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0e095620eee'
down_revision = 'dab3a6e08826'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('educations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=250), nullable=True),
    sa.Column('school', sa.String(length=250), nullable=True),
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
    op.drop_table('educations')
    # ### end Alembic commands ###
