"""Add authorID to Archives

Revision ID: 9566d7c9501f
Revises: 8c84acc3a1ee
Create Date: 2022-04-25 12:14:55.693304

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9566d7c9501f'
down_revision = '8c84acc3a1ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('archives', sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(None, 'archives', 'users', ['author_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'archives', type_='foreignkey')
    op.drop_column('archives', 'author_id')
    # ### end Alembic commands ###
