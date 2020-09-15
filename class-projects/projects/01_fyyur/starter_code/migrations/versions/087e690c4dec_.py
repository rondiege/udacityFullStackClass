"""empty message

Revision ID: 087e690c4dec
Revises: 05ca741c9686
Create Date: 2020-09-07 12:01:24.363035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '087e690c4dec'
down_revision = '05ca741c9686'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('venues', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'website')
    op.drop_column('artists', 'website')
    # ### end Alembic commands ###