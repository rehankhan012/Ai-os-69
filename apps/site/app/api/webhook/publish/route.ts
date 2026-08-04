import { NextRequest, NextResponse } from "next/server";
import { neon } from "@neondatabase/serverless";

export async function POST(req: NextRequest) {
  try {
    // 1. Verify Authentication
    const authHeader = req.headers.get("authorization");
    const token = process.env.SITE_PUBLISH_TOKEN;
    
    if (token && authHeader !== `Bearer ${token}`) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // 2. Parse payload
    const data = await req.json();
    
    if (!data.slug || !data.title) {
      return NextResponse.json({ error: "Missing required fields (slug, title)" }, { status: 400 });
    }

    // 3. Connect to Neon
    if (!process.env.DATABASE_URL) {
      console.error("DATABASE_URL is not set");
      return NextResponse.json({ error: "Server database configuration missing" }, { status: 500 });
    }
    
    const sql = neon(process.env.DATABASE_URL);

    // 4. Upsert Article into Neon Postgres
    await sql`
      INSERT INTO site_articles (
        id, title, slug, excerpt, content, featured_image_url, seo_score, 
        view_count, reading_time_minutes, published_at, category_name
      )
      VALUES (
        ${data.id}, ${data.title}, ${data.slug}, ${data.excerpt || null}, 
        ${data.content || null}, ${data.featured_image_url || null}, ${data.seo_score || 0}, 
        ${data.view_count || 0}, ${data.reading_time_minutes || 1}, 
        ${data.published_at ? new Date(data.published_at) : new Date()}, 
        ${data.category?.name || null}
      )
      ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        slug = EXCLUDED.slug,
        excerpt = EXCLUDED.excerpt,
        content = EXCLUDED.content,
        featured_image_url = EXCLUDED.featured_image_url,
        seo_score = EXCLUDED.seo_score,
        reading_time_minutes = EXCLUDED.reading_time_minutes,
        published_at = EXCLUDED.published_at,
        category_name = EXCLUDED.category_name;
    `;

    return NextResponse.json({ status: "success", message: "Article saved to Neon" });
  } catch (error: any) {
    console.error("Webhook error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
