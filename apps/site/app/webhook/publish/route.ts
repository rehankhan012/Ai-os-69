import { NextRequest, NextResponse } from "next/server";
import { neon } from "@neondatabase/serverless";

export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json({ status: "ok" });
}

export async function POST(req: NextRequest) {
  try {
    // 0. Server Configuration Check
    if (!process.env.DATABASE_URL || !process.env.SITE_PUBLISH_TOKEN) {
      console.error("CRITICAL: DATABASE_URL or SITE_PUBLISH_TOKEN missing in Vercel Environment Variables");
      return NextResponse.json({ error: "Server configuration missing" }, { status: 500 });
    }

    // 1. Verify Authentication
    const authHeader = req.headers.get("authorization");
    const token = process.env.SITE_PUBLISH_TOKEN;
    
    if (authHeader !== `Bearer ${token}`) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // 2. Parse payload
    const data = await req.json();
    
    if (!data.slug || !data.title || !data.id) {
      return NextResponse.json({ error: "Missing required fields (id, slug, title)" }, { status: 400 });
    }

    // 3. Connect to Neon
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

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error("Webhook error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
