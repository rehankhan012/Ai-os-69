/**
 * Data fetching for the Darkverse blog site.
 * Reads published articles from the Neon Serverless Postgres database.
 */
import { neon } from "@neondatabase/serverless";

export interface PublicArticle {
  id: string;
  title: string;
  slug: string;
  excerpt: string | null;
  content: string | null;
  featured_image_url: string | null;
  seo_score: number;
  view_count: number;
  reading_time_minutes: number;
  published_at: string | null;
  category: {
    name: string;
    slug: string;
    color: string;
  } | null;
}

export interface ArticleListResponse {
  articles: PublicArticle[];
  total: number;
  limit: number;
  offset: number;
}

export interface PublicCategory {
  name: string;
  slug: string;
  color: string;
  article_count: number;
}

export interface SiteInfo {
  name: string;
  tagline: string;
  description: string;
}

export function formatDate(iso: string | null): string {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return "";
  }
}

function getDb() {
  if (!process.env.DATABASE_URL) {
    throw new Error("DATABASE_URL is not configured.");
  }
  return neon(process.env.DATABASE_URL);
}

export async function getSiteInfo(): Promise<SiteInfo> {
  // Static site info for now since it's not stored in this articles table
  return {
    name: "Darkverse",
    tagline: "A publication",
    description: "Stories worth stopping for",
  };
}

export async function getArticles(
  opts: { category?: string; search?: string } = {},
): Promise<ArticleListResponse> {
  const sql = getDb();
  const limit = 50;
  const offset = 0;
  
  let articlesQuery;
  
  if (opts.category && opts.search) {
    articlesQuery = await sql`
      SELECT * FROM site_articles 
      WHERE category_name ILIKE ${opts.category} 
      AND (title ILIKE ${'%' + opts.search + '%'} OR excerpt ILIKE ${'%' + opts.search + '%'})
      ORDER BY published_at DESC NULLS LAST 
      LIMIT ${limit} OFFSET ${offset}
    `;
  } else if (opts.category) {
    articlesQuery = await sql`
      SELECT * FROM site_articles 
      WHERE category_name ILIKE ${opts.category} 
      ORDER BY published_at DESC NULLS LAST 
      LIMIT ${limit} OFFSET ${offset}
    `;
  } else if (opts.search) {
    articlesQuery = await sql`
      SELECT * FROM site_articles 
      WHERE title ILIKE ${'%' + opts.search + '%'} OR excerpt ILIKE ${'%' + opts.search + '%'}
      ORDER BY published_at DESC NULLS LAST 
      LIMIT ${limit} OFFSET ${offset}
    `;
  } else {
    articlesQuery = await sql`
      SELECT * FROM site_articles 
      ORDER BY published_at DESC NULLS LAST 
      LIMIT ${limit} OFFSET ${offset}
    `;
  }

  const articles: PublicArticle[] = articlesQuery.map(row => ({
    id: row.id,
    title: row.title,
    slug: row.slug,
    excerpt: row.excerpt,
    content: row.content,
    featured_image_url: row.featured_image_url,
    seo_score: row.seo_score,
    view_count: row.view_count,
    reading_time_minutes: row.reading_time_minutes,
    published_at: row.published_at ? new Date(row.published_at).toISOString() : null,
    category: row.category_name ? {
      name: row.category_name,
      slug: row.category_name.toLowerCase().replace(/\\s+/g, '-'),
      color: "#6b7280" // default color
    } : null
  }));

  return {
    articles,
    total: articles.length,
    limit,
    offset
  };
}

export async function getArticle(slug: string): Promise<PublicArticle> {
  const sql = getDb();
  
  const rows = await sql`
    SELECT * FROM site_articles WHERE slug = ${slug} OR id::text = ${slug} LIMIT 1
  `;
  
  if (rows.length === 0) {
    throw new Error("Article not found");
  }
  
  const row = rows[0];
  
  // Best-effort view count increment
  try {
    await sql`UPDATE site_articles SET view_count = view_count + 1 WHERE id = ${row.id}`;
  } catch (e) {
    // ignore
  }

  return {
    id: row.id,
    title: row.title,
    slug: row.slug,
    excerpt: row.excerpt,
    content: row.content,
    featured_image_url: row.featured_image_url,
    seo_score: row.seo_score,
    view_count: row.view_count + 1,
    reading_time_minutes: row.reading_time_minutes,
    published_at: row.published_at ? new Date(row.published_at).toISOString() : null,
    category: row.category_name ? {
      name: row.category_name,
      slug: row.category_name.toLowerCase().replace(/\\s+/g, '-'),
      color: "#6b7280"
    } : null
  };
}

export async function getCategories(): Promise<PublicCategory[]> {
  const sql = getDb();
  const rows = await sql`
    SELECT category_name, COUNT(*) as count 
    FROM site_articles 
    WHERE category_name IS NOT NULL 
    GROUP BY category_name 
    ORDER BY category_name
  `;
  
  return rows.map(row => ({
    name: row.category_name,
    slug: row.category_name.toLowerCase().replace(/\\s+/g, '-'),
    color: "#6b7280",
    article_count: Number(row.count)
  }));
}
