-- Run this in your Neon SQL Editor to create the articles table for the Vercel site

CREATE TABLE IF NOT EXISTS site_articles (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    excerpt TEXT,
    content TEXT,
    featured_image_url TEXT,
    seo_score FLOAT DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    reading_time_minutes INTEGER DEFAULT 1,
    published_at TIMESTAMPTZ,
    category_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_site_articles_slug ON site_articles(slug);
CREATE INDEX idx_site_articles_published_at ON site_articles(published_at DESC);
