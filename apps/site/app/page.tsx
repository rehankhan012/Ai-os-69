import Link from "next/link";
import { ArrowRight, Clock, Compass, Eye } from "lucide-react";
import { getArticles, getCategories, getSiteInfo, formatDate } from "@/lib/api";
import { ArticleCard } from "@/components/article-card";
import Newsletter from "@/components/newsletter";

export const dynamic = "force-dynamic";

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string; q?: string }>;
}) {
  const { category, q } = await searchParams;

  let info = { name: "Darkverse", tagline: "", description: "" };
  let categories: Awaited<ReturnType<typeof getCategories>> = [];
  let data: Awaited<ReturnType<typeof getArticles>> = {
    articles: [],
    total: 0,
    limit: 50,
    offset: 0,
  };

  try {
    info = await getSiteInfo();
  } catch {
    /* defaults above */
  }
  try {
    categories = await getCategories();
  } catch {
    /* ignore */
  }
  try {
    data = await getArticles({ category, search: q });
  } catch {
    /* keep empty state */
  }

  const { articles } = data;
  const [featured, ...rest] = articles;

  return (
    <div className="max-w-5xl mx-auto px-5 sm:px-8">
      {/* Hero */}
      <section className="py-14 sm:py-20 text-center animate-fade-in-up relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[560px] h-[360px] -z-10 bg-gradient-to-r from-accent/10 via-purple-500/10 to-blue-500/10 blur-3xl rounded-full pointer-events-none" />
        <p className="text-xs uppercase tracking-[0.3em] text-accent font-medium mb-4">
          {info.tagline || "A publication"}
        </p>
        <h1 className="font-serif text-4xl sm:text-6xl font-bold tracking-tight leading-tight">
          Stories worth
          <br />
          <span className="bg-gradient-to-r from-accent via-purple-500 to-blue-500 bg-clip-text text-transparent">
            stopping for
          </span>
        </h1>
        <p className="mt-6 text-muted-foreground text-lg max-w-xl mx-auto">
          {info.description}
        </p>

        {/* Search */}
        <form method="get" action="/" className="mt-10 max-w-md mx-auto">
          <div className="relative">
            <input
              type="text"
              name="q"
              defaultValue={q || ""}
              placeholder="Search articles..."
              className="w-full h-12 rounded-2xl bg-card border border-border pl-5 pr-24 text-sm outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent/50 transition-all placeholder:text-muted-foreground"
            />
            <button
              type="submit"
              className="absolute right-1.5 top-1/2 -translate-y-1/2 h-9 px-4 rounded-xl bg-accent text-white text-sm font-medium hover:bg-accent/90 transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </section>

      {/* Categories */}
      {categories.length > 0 && (
        <section id="categories" className="mb-14 scroll-mt-24">
          <div className="flex flex-wrap items-center justify-center gap-2">
            <Link
              href="/"
              className={`px-4 py-2 rounded-full text-sm transition-all ${
                !category
                  ? "bg-accent text-white shadow-lg shadow-accent/20"
                  : "bg-card border border-border text-muted-foreground hover:text-foreground hover:border-accent/40"
              }`}
            >
              All
            </Link>
            {categories.map((c) => (
              <Link
                key={c.slug}
                href={`/?category=${encodeURIComponent(c.slug)}`}
                className={`px-4 py-2 rounded-full text-sm transition-all inline-flex items-center gap-1.5 ${
                  category === c.slug
                    ? "bg-accent text-white shadow-lg shadow-accent/20"
                    : "bg-card border border-border text-muted-foreground hover:text-foreground hover:border-accent/40"
                }`}
              >
                {c.name}
                <span
                  className="ml-0.5 text-xs opacity-70"
                  style={category !== c.slug ? { color: c.color } : undefined}
                >
                  {c.article_count}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Featured article */}
      {featured && !category && !q && (
        <Link
          href={`/articles/${featured.slug}`}
          className="group block mb-14 rounded-3xl overflow-hidden border border-border hover:border-accent/40 transition-all duration-300 animate-fade-in-up"
        >
          {featured.featured_image_url ? (
            <div className="grid sm:grid-cols-2">
              <div className="relative h-56 sm:h-full overflow-hidden">
                <img
                  src={featured.featured_image_url}
                  alt={featured.title}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-background hidden sm:block" />
              </div>
              <div className="p-8 sm:p-12 relative">
                <span className="text-[11px] uppercase tracking-[0.25em] text-accent font-medium">
                  Latest Story
                </span>
                <h2 className="mt-4 font-serif text-2xl sm:text-4xl font-bold leading-tight group-hover:text-accent transition-colors">
                  {featured.title}
                </h2>
                {featured.excerpt && (
                  <p className="mt-4 text-muted-foreground line-clamp-2">
                    {featured.excerpt}
                  </p>
                )}
                <div className="mt-6 flex flex-wrap items-center gap-5 text-xs text-muted-foreground">
                  <span>{formatDate(featured.published_at)}</span>
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" /> {featured.reading_time_minutes} min read
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Eye className="w-3.5 h-3.5" /> {featured.view_count}
                  </span>
                  <span className="flex items-center gap-1.5 text-accent font-medium ml-auto group-hover:gap-3 transition-all">
                    Read <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 sm:p-12 relative">
              <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full bg-accent/10 blur-3xl group-hover:bg-accent/20 transition-all" />
              <span className="text-[11px] uppercase tracking-[0.25em] text-accent font-medium">
                Latest Story
              </span>
              <h2 className="mt-4 font-serif text-2xl sm:text-4xl font-bold leading-tight max-w-2xl group-hover:text-accent transition-colors">
                {featured.title}
              </h2>
              {featured.excerpt && (
                <p className="mt-4 text-muted-foreground max-w-2xl line-clamp-2">
                  {featured.excerpt}
                </p>
              )}
              <div className="mt-6 flex items-center gap-5 text-xs text-muted-foreground">
                <span>{formatDate(featured.published_at)}</span>
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5" /> {featured.reading_time_minutes} min read
                </span>
                <span className="flex items-center gap-1.5">
                  <Eye className="w-3.5 h-3.5" /> {featured.view_count}
                </span>
                <span className="flex items-center gap-1.5 text-accent font-medium ml-auto group-hover:gap-3 transition-all">
                  Read <ArrowRight className="w-4 h-4" />
                </span>
              </div>
            </div>
          )}
        </Link>
      )}

      {/* Article grid */}
      <section>
        <div className="flex items-end justify-between mb-8">
          <h2 className="font-serif text-2xl font-semibold flex items-center gap-2.5">
            {category ? (
              <>
                <Compass className="w-5 h-5 text-accent" />
                {categories.find((c) => c.slug === category)?.name || category}
              </>
            ) : q ? (
              <>Results for &ldquo;{q}&rdquo;</>
            ) : (
              "All Articles"
            )}
          </h2>
          <span className="text-xs text-muted-foreground">
            {articles.length} article{articles.length === 1 ? "" : "s"}
          </span>
        </div>

        {articles.length === 0 ? (
          <div className="py-24 text-center animate-fade-in-up">
            <div className="w-20 h-20 mx-auto rounded-3xl bg-card border border-border flex items-center justify-center mb-6">
              <Compass className="w-8 h-8 text-muted-foreground/60" />
            </div>
            <p className="font-serif text-2xl font-semibold">
              {q ? `No results for "${q}"` : "Nothing here yet"}
            </p>
            <p className="text-muted-foreground text-sm mt-2 max-w-sm mx-auto">
              {q
                ? "Try a different search term, or browse the latest stories below."
                : "New stories are being written — check back soon."}
            </p>
            {q && (
              <Link
                href="/"
                className="inline-flex items-center gap-2 mt-8 px-6 py-3 rounded-2xl bg-accent text-white text-sm font-medium hover:bg-accent/90 transition-colors"
              >
                Browse all articles <ArrowRight className="w-4 h-4" />
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {(featured && !category && !q ? rest : articles).map((a, i) => (
              <ArticleCard key={a.id} article={a} index={i} />
            ))}
          </div>
        )}
      </section>

      <Newsletter />
    </div>
  );
}
