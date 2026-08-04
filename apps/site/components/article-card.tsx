import Link from "next/link";
import { Clock, Eye } from "lucide-react";
import { formatDate, type PublicArticle } from "@/lib/api";

export function ArticleCard({
  article,
  index = 0,
}: {
  article: PublicArticle;
  index?: number;
}) {
  const color = article.category?.color || "#6366F1";

  return (
    <Link
      href={`/articles/${article.slug}`}
      className="group flex flex-col rounded-2xl border border-border bg-card/60 hover:bg-card hover:border-accent/40 hover:-translate-y-1 transition-all duration-300 overflow-hidden animate-fade-in-up"
      style={{ animationDelay: `${Math.min(index * 60, 400)}ms` }}
    >
      {article.featured_image_url ? (
        <div className="relative h-44 overflow-hidden">
          <img
            src={article.featured_image_url}
            alt={article.title}
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-card/80 via-transparent to-transparent" />
        </div>
      ) : (
        <div
          className="relative h-24 overflow-hidden flex items-end"
          style={{
            background: `radial-gradient(120% 160% at 20% 0%, ${color}22 0%, transparent 60%), linear-gradient(180deg, transparent, hsl(var(--card)))`,
          }}
        >
          <span
            className="absolute left-5 bottom-4 font-serif text-5xl font-bold opacity-25 group-hover:opacity-40 transition-opacity"
            style={{ color }}
          >
            {article.title.charAt(0).toUpperCase()}
          </span>
        </div>
      )}

      <div className="flex flex-col flex-1 p-6 pt-5">
        {article.category && (
          <span
            className="text-[11px] font-medium uppercase tracking-wider mb-3 flex items-center gap-1.5"
            style={{ color }}
          >
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: color }}
            />
            {article.category.name}
          </span>
        )}
        <h3 className="font-serif text-lg font-semibold leading-snug group-hover:text-accent transition-colors line-clamp-3">
          {article.title}
        </h3>
        {article.excerpt && (
          <p className="mt-2.5 text-sm text-muted-foreground line-clamp-2 flex-1">
            {article.excerpt}
          </p>
        )}
        <div className="mt-5 pt-4 border-t border-border/60 flex items-center gap-4 text-[11px] text-muted-foreground">
          <span>{formatDate(article.published_at)}</span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" /> {article.reading_time_minutes} min
          </span>
          <span className="ml-auto flex items-center gap-1">
            <Eye className="w-3 h-3" /> {article.view_count}
          </span>
        </div>
      </div>
    </Link>
  );
}
