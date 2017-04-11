"""m2m relation between profs and levels

Revision ID: 131b2610ac8c
Revises: 9e0573a19b93
Create Date: 2017-04-10 12:38:16.458843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '131b2610ac8c'
down_revision = '9e0573a19b93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('levels_profs',
    sa.Column('level_id', sa.Integer(), nullable=True),
    sa.Column('prof_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['level_id'], ['levels.id'], ),
    sa.ForeignKeyConstraint(['prof_id'], ['profs.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('levels_profs')
    # ### end Alembic commands ###
