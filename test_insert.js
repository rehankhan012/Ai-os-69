import { neon } from '@neondatabase/serverless';

const sql = neon('postgresql://neondb_owner:npg_2oxH1RDbWJCK@ep-spring-bird-axqxrk06-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require');

async function run() {
  try {
    const data = {
      id: "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      title: "Test Publish",
      slug: "test-publish",
      excerpt: "This is a test publish.",
      content: "Hello world.",
      featured_image_url: null,
      seo_score: 95.5,
      view_count: 0,
      reading_time_minutes: 5,
      published_at: new Date().toISOString(),
      category: { name: "Technology" }
    };

    const res = await sql`
      INSERT INTO site_articles (
        id, title, slug, excerpt, content, featured_image_url, seo_score, 
        view_count, reading_time_minutes, published_at, category_name
      )
      VALUES (
        ${data.id}, ${data.title}, ${data.slug}, ${data.excerpt}, 
        ${data.content}, ${data.featured_image_url}, ${data.seo_score}, 
        ${data.view_count}, ${data.reading_time_minutes}, 
        ${data.published_at}, 
        ${data.category?.name}
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
    console.log("Success:", res);
  } catch (err) {
    console.error("Error:", err);
  }
}

run();
