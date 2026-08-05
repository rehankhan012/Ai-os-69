"""Restore site_articles table

Revision ID: 9abdb66e6f14
Revises: 1ec2f3f28162
Create Date: 2026-08-05 08:47:28.557220
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9abdb66e6f14'
down_revision: Union[str, None] = '1ec2f3f28162'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the site_articles table expected by the frontend webhook
    op.create_table('site_articles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.TEXT(), nullable=False),
        sa.Column('slug', sa.TEXT(), nullable=False),
        sa.Column('excerpt', sa.TEXT(), nullable=True),
        sa.Column('content', sa.TEXT(), nullable=True),
        sa.Column('featured_image_url', sa.TEXT(), nullable=True),
        sa.Column('seo_score', sa.DOUBLE_PRECISION(precision=53), server_default=sa.text('0'), nullable=True),
        sa.Column('view_count', sa.INTEGER(), server_default=sa.text('0'), nullable=True),
        sa.Column('reading_time_minutes', sa.INTEGER(), server_default=sa.text('1'), nullable=True),
        sa.Column('published_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('category_name', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_site_articles_slug', 'site_articles', ['slug'], unique=False)
    op.create_index('idx_site_articles_published_at', 'site_articles', [sa.text('published_at DESC')], unique=False)

    # Backfill the table with published articles
    op.execute("""
        INSERT INTO site_articles (
            id, title, slug, excerpt, content, featured_image_url, 
            seo_score, view_count, published_at, category_name
        )
        SELECT 
            a.id, a.title, a.slug, a.excerpt, a.content, a.featured_image_url,
            a.seo_score, a.view_count, a.published_at, c.name
        FROM articles a
        LEFT JOIN categories c ON a.category_id = c.id
        WHERE a.status = 'published'
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    op.drop_index('idx_site_articles_published_at', table_name='site_articles')
    op.drop_index('idx_site_articles_slug', table_name='site_articles')
    op.drop_table('site_articles')