"""empty message

Revision ID: df2e021c3714
Revises: d04aa2b7ba2c
Create Date: 2020-09-28 09:06:26.655748

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'df2e021c3714'
down_revision = 'd04aa2b7ba2c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('shows', 'date', new_column_name='start_time')

def downgrade():
    op.alter_column('shows', 'start_time', new_column_name='date')
