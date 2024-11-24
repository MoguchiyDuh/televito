"""

Revision ID: 9dccd62f6e2c
Revises: 8cb6f373d618
Create Date: 2024-11-20 05:24:42.396617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dccd62f6e2c'
down_revision: Union[str, None] = '8cb6f373d618'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('categories', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'categories', 'categories', ['parent_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'categories', type_='foreignkey')
    op.drop_column('categories', 'parent_id')
    # ### end Alembic commands ###
