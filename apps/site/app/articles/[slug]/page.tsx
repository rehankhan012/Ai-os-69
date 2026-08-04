import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Clock, Eye, Calendar } from "lucide-react";
import { getArticle, getArticles, formatDate } from "@/lib/api";
import ReadingProgress from "@/components/reading-progress";
import ShareButtons from "@/components/share-buttons";
import TableOfContents, {
  type TocHeading,
} from "@/components/table-of-contents";
import { ArticleCard } from "@/components/article-card";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  try {
    const article = await getArticle(slug);
    return {
      title: article.title,
      description: article.excerpt || undefined,
      openGraph: {
        title: article.title,
        description: article.excerpt || undefined,
        type: "article",
        publishedTime: article.published_at || undefined,
        images: article.featured_image_url
          ? [{ url: article.featured_image_url }]
          : undefined,
      },
    };
  } catch {
    return { title: "Article" };
  }
}

/** Inject stable ids into h2/h3 headings so the TOC can deep-link to them.
 * Headings inside <pre>/<code> blocks are skipped, and any pre-existing id
 * attribute is replaced to avoid duplicates. */
function withHeadingIds(html: string): { html: string; headings: TocHeading[] } {
  const headings: TocHeading[] = [];
  let counter = 0;

  // Split on code blocks so headings inside samples are never indexed.
  const parts = html.split(/(<pre[\s\S]*?<\/pre>)/gi);
  const out = parts
    .map((part) => {
      if (/^<pre/i.test(part)) return part;
      return part.replace(
        /<h([23])([^>]*)>([\s\S]*?)<\/h\1>/gi,
        (match, level: string, attrs: string, inner: string) => {
          const id = `section-${counter}`;
          counter += 1;
          const text = inner.replace(/<[^>]*>/g, "").trim();
          if (text) headings.push({ id, text, level: Number(level) });
          const cleanAttrs = attrs.replace(
            /\s+id\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi,
            "",
          );
          return `<h${level} id="${id}"${cleanAttrs}>${inner}</h${level}>`;
        },
      );
    })
    .join("");

  return { html: out, headings };
}

export default async function ArticlePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  let article;
  try {
    article = await getArticle(slug);
  } catch {
    notFound();
  }

  let more: Awaited<ReturnType<typeof getArticles>>["articles"] = [];
  try {
    const res = await getArticles({});
    const others = res.articles.filter((a) => a.id !== article.id);
    // Prefer same-category stories, then fill with the latest.
    const sameCategory = article.category
      ? others.filter((a) => a.category?.slug === article.category!.slug)
      : [];
    more = [...sameCategory, ...others.filter((a) => !sameCategory.includes(a))].slice(
      0,
      3,
    );
  } catch {
    /* ignore */
  }

  const { html: contentHtml, headings } = withHeadingIds(
    article.content || "<p>This article has no content yet.</p>",
  );

  return (
    <div className="max-w-5xl mx-auto px-5 sm:px-8">
      <ReadingProgress />

      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mt-10 mb-8"
      >
        <ArrowLeft className="w-4 h-4" /> All articles
      </Link>

      <article>
        <header className="mb-10">
          {article.category && (
            <span
              className="text-[11px] font-medium uppercase tracking-[0.2em]"
              style={{ color: article.category.color }}
            >
              {article.category.name}
            </span>
          )}
          <h1 className="mt-3 font-serif text-3xl sm:text-5xl font-bold leading-tight tracking-tight">
            {article.title}
          </h1>
          {article.excerpt && (
            <p className="mt-5 text-lg text-muted-foreground leading-relaxed">
              {article.excerpt}
            </p>
          )}
          <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-3 text-xs text-muted-foreground border-y border-border py-4">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" /> {formatDate(article.published_at)}
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" /> {article.reading_time_minutes} min read
            </span>
            <span className="flex items-center gap-1.5">
              <Eye className="w-3.5 h-3.5" /> {article.view_count} views
            </span>
            <span className="ml-auto">
              <ShareButtons title={article.title} />
            </span>
          </div>
        </header>

        {article.featured_image_url && (
          <div className="relative mb-10 rounded-3xl overflow-hidden border border-border">
            <img
              src={article.featured_image_url}
              alt={article.title}
              className="w-full max-h-[420px] object-cover"
            />
          </div>
        )}

        <div className="lg:flex lg:gap-12">
          <TableOfContents headings={headings} />

          <div className="min-w-0 flex-1">
            <div
              className="prose-dark"
              dangerouslySetInnerHTML={{ __html: contentHtml }}
            />

            {/* Article footer */}
            <div className="mt-14 pt-6 border-t border-border">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <p className="text-sm text-muted-foreground">
                  Enjoyed this? Share it with someone who needs it.
                </p>
                <ShareButtons title={article.title} />
              </div>
            </div>
          </div>
        </div>

        {/* Related */}
        {more.length > 0 && (
          <div className="mt-20">
            <h2 className="font-serif text-xl font-semibold mb-6">
              Keep reading
              {article.category && (
                <span className="text-muted-foreground font-normal">
                  {" "}
                  — more {article.category.name.toLowerCase()}
                </span>
              )}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              {more.map((a, i) => (
                <ArticleCard key={a.id} article={a} index={i} />
              ))}
            </div>
          </div>
        )}
      </article>
    </div>
  );
}
