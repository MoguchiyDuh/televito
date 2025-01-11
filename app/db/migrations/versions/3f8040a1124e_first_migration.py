"""first migration

Revision ID: 3f8040a1124e
Revises: 
Create Date: 2025-01-11 17:19:47.820179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f8040a1124e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_table('tg_posts',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('google_maps_url', sa.String(), nullable=True),
    sa.Column('location', sa.String(length=150), nullable=False),
    sa.Column('status', sa.Date(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('is_new', sa.Boolean(), nullable=True),
    sa.Column('rooms', sa.Float(), nullable=True),
    sa.Column('room_description', sa.String(length=100), nullable=True),
    sa.Column('area', sa.Float(), nullable=True),
    sa.Column('floor', sa.Integer(), nullable=True),
    sa.Column('floors_in_building', sa.Integer(), nullable=True),
    sa.Column('pets_allowed', sa.Boolean(), nullable=True),
    sa.Column('parking', sa.String(length=100), nullable=True),
    sa.Column('images', sa.ARRAY(sa.String(length=100)), nullable=True),
    sa.Column('publication_datetime', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tg_posts_id'), 'tg_posts', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('profile_photo', sa.String(length=100), nullable=True),
    sa.Column('description', sa.String(length=300), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('posts',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('location', sa.String(length=150), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_new', sa.Boolean(), nullable=True),
    sa.Column('images', sa.ARRAY(sa.String(length=100)), nullable=True),
    sa.Column('publication_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('subcategory_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['subcategory_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_id'), 'posts', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_posts_id'), table_name='posts')
    op.drop_table('posts')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_tg_posts_id'), table_name='tg_posts')
    op.drop_table('tg_posts')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
