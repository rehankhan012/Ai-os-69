"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  Globe, FileText, Plus, Search, FolderOpen, Tags, Image, X,
  Loader2, Pencil, Trash2, CheckCircle2, Send, Sparkles,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import api from "@/lib/api";
import { ensureAuth } from "@/lib/auth";
import PublishPanel from "@/components/publish/publish-panel";

/* ============================================================
 * Types & helpers
 * ============================================================ */

interface ArticleItem {
  id: string;
  title: string;
  slug: string | null;
  excerpt: string | null;
  status: string;
  seo_score: number;
  ai_generated: boolean;
  view_count: number;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

interface Category {
  id: string;
  name: string;
  slug?: string;
  color?: string;
  article_count?: number;
}

const STATUS_BADGE: Record<string, "outline" | "success" | "warning" | "secondary"> = {
  draft: "secondary",
  review: "warning",
  approved: "outline",
  published: "success",
  archived: "outline",
};

const statusLabel = (s: string) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : "Draft");

function timeAgo(iso: string | null): string {
  if (!iso) return "—";
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const mins = Math.floor(seconds / 60);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return days === 1 ? "1 day ago" : `${days} days ago`;
}

const inputCls =
  "flex h-10 w-full rounded-xl border border-border bg-background/50 px-4 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-all";
const labelCls = "text-xs font-medium text-muted-foreground mb-1.5 block";

/* ============================================================
 * Page
 * ============================================================ */

export default function CMSPage() {
  const [articles, setArticles] = useState<ArticleItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState("");
  const [editorOpen, setEditorOpen] = useState(false);
  const [editing, setEditing] = useState<ArticleItem | null>(null);
  const [catModalOpen, setCatModalOpen] = useState(false);
  const [tagModalOpen, setTagModalOpen] = useState(false);
  const [publishFor, setPublishFor] = useState<string | null>(null);
  const searchDebounce = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Guards against out-of-order responses overwriting newer search results.
  const loadSeq = useRef(0);

  const loadArticles = useCallback(async (query = "") => {
    const seq = ++loadSeq.current;
    try {
      const params: Record<string, string | number> = { limit: 100, offset: 0 };
      if (query.trim()) params.search = query.trim();
      const res = await api.get<ArticleItem[]>("/articles/", params);
      if (seq === loadSeq.current) setArticles(res);
    } catch (e) {
      if (seq === loadSeq.current) {
        toast.error(e instanceof Error ? e.message : "Failed to load articles");
      }
    } finally {
      if (seq === loadSeq.current) setLoading(false);
    }
  }, []);

  const loadCategories = useCallback(async () => {
    try {
      const res = await api.get<Category[]>("/cms/categories");
      setCategories(res);
    } catch {
      // Categories are optional — silently skip
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await ensureAuth();
      if (cancelled) return;
      await Promise.all([loadArticles(), loadCategories()]);
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Debounced search against the API (skips the initial mount so the init
  // effect below owns the first load).
  const firstRender = useRef(true);
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    if (searchDebounce.current) clearTimeout(searchDebounce.current);
    searchDebounce.current = setTimeout(() => {
      setLoading(true);
      loadArticles(searchInput);
    }, 350);
    return () => {
      if (searchDebounce.current) clearTimeout(searchDebounce.current);
    };
  }, [searchInput, loadArticles]);

  const handleDelete = async (article: ArticleItem) => {
    if (!window.confirm(`Delete "${article.title}"? This cannot be undone.`)) return;
    try {
      await api.delete(`/articles/${article.id}`);
      toast.success("Article deleted");
      setArticles((prev) => prev.filter((a) => a.id !== article.id));
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Delete failed");
    }
  };

  const totalSeo = articles.length
    ? (articles.reduce((sum, a) => sum + (a.seo_score || 0), 0) / articles.length).toFixed(0)
    : "0";
  const publishedCount = articles.filter((a) => a.status === "published").length;
  const draftCount = articles.filter((a) => a.status === "draft").length;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Globe className="w-6 h-6 text-emerald-400" />
            <h1 className="section-title">Website CMS</h1>
          </div>
          <p className="section-subtitle">Manage your website content, categories, and media</p>
        </div>
        <Button className="gap-2" onClick={() => { setEditing(null); setEditorOpen(true); }}>
          <Plus className="w-4 h-4" /> New Article
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Articles", value: articles.length, color: "text-foreground" },
          { label: "Published", value: publishedCount, color: "text-emerald-400" },
          { label: "Drafts", value: draftCount, color: "text-amber-400" },
          { label: "Avg SEO Score", value: `${totalSeo}%`, color: "text-violet-400" },
        ].map((s, i) => (
          <Card key={i} className="glass-card-hover">
            <CardContent className="p-4">
              <p className={cn("text-2xl font-bold", s.color)}>{String(s.value)}</p>
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center justify-between">
                Categories
                <Button variant="ghost" size="icon" className="w-6 h-6" onClick={() => setCatModalOpen(true)} title="Add category">
                  <Plus className="w-3.5 h-3.5" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {categories.length === 0 && (
                <p className="text-xs text-muted-foreground py-2">No categories yet — add one to organize articles.</p>
              )}
              {categories.map((cat) => (
                <div key={cat.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-glass-hover transition-colors cursor-pointer">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color || "#6366F1" }} />
                    <span className="text-sm">{cat.name}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{cat.article_count ?? 0}</span>
                </div>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="glass" className="w-full justify-start gap-2 text-sm" onClick={() => setCatModalOpen(true)}>
                <FolderOpen className="w-4 h-4" /> Add Category
              </Button>
              <Button variant="glass" className="w-full justify-start gap-2 text-sm" onClick={() => setTagModalOpen(true)}>
                <Tags className="w-4 h-4" /> Add Tag
              </Button>
              <Button variant="glass" className="w-full justify-start gap-2 text-sm" onClick={() => window.open("/media", "_self")}>
                <Image className="w-4 h-4" /> Media Library
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search articles..."
              className="pl-10"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
            />
          </div>

          {loading && articles.length === 0 ? (
            <div className="flex items-center justify-center py-16 text-muted-foreground gap-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Loading articles...
            </div>
          ) : articles.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-glass-border p-12 text-center space-y-3">
              <FileText className="w-10 h-10 text-muted-foreground mx-auto" />
              <p className="text-sm font-medium">No articles found</p>
              <p className="text-xs text-muted-foreground">
                {searchInput ? "Try a different search term." : "Create your first article to get started."}
              </p>
              {!searchInput && (
                <Button className="gap-2 mt-2" onClick={() => { setEditing(null); setEditorOpen(true); }}>
                  <Plus className="w-4 h-4" /> New Article
                </Button>
              )}
            </div>
          ) : (
            articles.map((article, i) => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(i * 0.04, 0.4) }}
                className="glass-card-hover p-4 flex items-start justify-between gap-4"
              >
                <div className="flex items-start gap-4 min-w-0">
                  <div className={cn("p-2 rounded-lg shrink-0", article.ai_generated ? "bg-violet-500/10 text-violet-400" : "bg-muted text-muted-foreground")}>
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{article.title}</p>
                    {article.excerpt && (
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">{article.excerpt}</p>
                    )}
                    <div className="flex flex-wrap items-center gap-2 mt-1.5">
                      {article.ai_generated && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-violet-500/10 text-violet-400 flex items-center gap-1">
                          <CheckCircle2 className="w-2.5 h-2.5" /> AI
                        </span>
                      )}
                      <Badge variant="outline" className="text-[10px]">
                        SEO {Math.round(article.seo_score || 0)}%
                      </Badge>
                      <span className="text-[10px] text-muted-foreground">Updated {timeAgo(article.updated_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <Badge variant={STATUS_BADGE[article.status] || "secondary"} className="text-[10px] capitalize">
                    {statusLabel(article.status)}
                  </Badge>
                  <Button variant="ghost" size="icon" className="w-7 h-7 text-primary" title="Publish to website & Pinterest" onClick={() => setPublishFor(article.id)}>
                    <Send className="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="w-7 h-7" title="Edit" onClick={() => { setEditing(article); setEditorOpen(true); }}>
                    <Pencil className="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="w-7 h-7 text-red-400 hover:text-red-400" title="Delete" onClick={() => handleDelete(article)}>
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Editor modal */}
      <AnimatePresence>
        {editorOpen && (
          <ArticleEditor
            article={editing}
            categories={categories}
            onClose={() => setEditorOpen(false)}
            onSaved={() => {
              setEditorOpen(false);
              loadArticles(searchInput);
            }}
          />
        )}
      </AnimatePresence>

      {/* Category modal */}
      <AnimatePresence>
        {catModalOpen && (
          <CategoryModal
            onClose={() => setCatModalOpen(false)}
            onCreated={() => {
              setCatModalOpen(false);
              loadCategories();
            }}
          />
        )}
      </AnimatePresence>

      {/* Tag modal */}
      <AnimatePresence>
        {tagModalOpen && (
          <TagModal
            onClose={() => setTagModalOpen(false)}
            onCreated={() => setTagModalOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Publish modal */}
      <AnimatePresence>
        {publishFor && (
          <ModalShell
            title="Publish Article"
            subtitle="Upload to your website & Pinterest, then track analytics live"
            onClose={() => setPublishFor(null)}
          >
            <PublishPanel articleId={publishFor} />
          </ModalShell>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ============================================================
 * Modal shell
 * ============================================================ */

function ModalShell({ title, subtitle, onClose, children }: {
  title: string;
  subtitle?: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 12 }}
        transition={{ duration: 0.2 }}
        className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-glass-border bg-card p-6 shadow-2xl"
      >
        <div className="flex items-start justify-between mb-5">
          <div>
            <h2 className="text-lg font-semibold">{title}</h2>
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
          <Button variant="ghost" size="icon" className="w-8 h-8" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        {children}
      </motion.div>
    </motion.div>
  );
}

/* ============================================================
 * Article editor (create / edit)
 * ============================================================ */

function ArticleEditor({ article, categories, onClose, onSaved }: {
  article: ArticleItem | null;
  categories: Category[];
  onClose: () => void;
  onSaved: () => void;
}) {
  const [title, setTitle] = useState(article?.title ?? "");
  const [excerpt, setExcerpt] = useState(article?.excerpt ?? "");
  const [content, setContent] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [status, setStatus] = useState(article?.status ?? "draft");
  const [saving, setSaving] = useState(false);
  // Tracks the persisted article so AI generation can switch the editor to
  // the draft the pipeline already saved (avoiding duplicate articles).
  const [savedId, setSavedId] = useState<string | null>(article?.id ?? null);
  // AI generation
  const [aiTopic, setAiTopic] = useState("");
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiDone, setAiDone] = useState(false);
  const [aiSeo, setAiSeo] = useState(0);

  // Load full content when editing (list endpoint omits it)
  useEffect(() => {
    let cancelled = false;
    if (article) {
      api.get<{ content: string | null }>(`/articles/${article.id}`).then((res) => {
        if (!cancelled) setContent(res.content ?? "");
      }).catch(() => {});
    }
    return () => {
      cancelled = true;
    };
  }, [article]);

  const generateWithAI = async () => {
    if (!aiTopic.trim() || aiGenerating) return;
    setAiGenerating(true);
    setAiDone(false);
    try {
      // Full pipeline: Trend → SEO → Content → Design → Quality → Schedule,
      // saves the article + pin + queue as a draft, then we load it in.
      const gen = await api.post<{
        article_id: string;
        quality_score: number;
      }>("/workflow/generate", {
        topic: aiTopic.trim(),
        niche: "",
        tone: "professional",
      });
      const art = await api.get<{
        title: string;
        excerpt: string | null;
        content: string | null;
        seo_score: number;
      }>(`/articles/${gen.article_id}`);
      setSavedId(gen.article_id);
      setTitle(art.title);
      setExcerpt(art.excerpt ?? "");
      setContent(art.content ?? "");
      setAiSeo(art.seo_score || gen.quality_score || 0);
      setAiDone(true);
      toast.success("Article generated with AI — review it, then publish");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "AI generation failed");
    } finally {
      setAiGenerating(false);
    }
  };

  const save = async () => {
    if (!title.trim() || saving) return;
    setSaving(true);
    try {
      const body = {
        title: title.trim(),
        excerpt: excerpt.trim() || null,
        content: content || null,
        category_id: categoryId || null,
        status,
      };
      if (savedId) {
        await api.patch(`/articles/${savedId}`, body);
        toast.success("Article updated");
      } else {
        const res = await api.post<{ id: string }>("/articles/", body);
        setSavedId(res.id);
        toast.success("Article created");
      }
      onSaved();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalShell
      title={savedId ? "Edit Article" : "New Article"}
      subtitle={savedId ? "Review the draft, then publish" : "Create or AI-generate an article for your website"}
      onClose={onClose}
    >
      <div className="space-y-4">
        {/* AI generation */}
        {!savedId && (
          <div className="rounded-xl border border-primary/25 bg-primary/5 p-4 space-y-3">
            <p className="text-xs font-semibold flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-primary" /> Generate with AI
            </p>
            <div className="flex gap-2">
              <Input
                placeholder="Enter a topic, e.g. '10 best coffee brewing methods'..."
                value={aiTopic}
                onChange={(e) => setAiTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && generateWithAI()}
              />
              <Button onClick={generateWithAI} disabled={!aiTopic.trim() || aiGenerating} className="shrink-0 gap-2">
                {aiGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                {aiGenerating ? "Generating..." : "Generate"}
              </Button>
            </div>
            <p className="text-[10px] text-muted-foreground">
              Runs the full AI pipeline (Trend → SEO → Content → Design → Quality → Schedule) and saves the article as a draft.
            </p>
          </div>
        )}

        {aiDone && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 flex items-center gap-2 text-xs text-emerald-400">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            AI-generated draft ready · SEO score {Math.round(aiSeo)} · review below, then publish
          </div>
        )}

        <div>
          <label className={labelCls}>Title *</label>
          <Input
            placeholder="Enter article title..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
            className="h-11 text-base"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Category</label>
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className={cn(inputCls, "appearance-none bg-background/50")}
            >
              <option value="">Uncategorized</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className={cn(inputCls, "appearance-none bg-background/50")}
            >
              <option value="draft">Draft</option>
              <option value="review">Review</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>

        <div>
          <label className={labelCls}>Excerpt</label>
          <textarea
            rows={2}
            placeholder="Short summary shown in article lists..."
            value={excerpt}
            onChange={(e) => setExcerpt(e.target.value)}
            className="w-full rounded-xl border border-border bg-background/50 px-4 py-2.5 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-all resize-none"
          />
        </div>

        <div>
          <label className={labelCls}>Content</label>
          <textarea
            rows={8}
            placeholder={"Write your article here. Plain text or HTML (<h2>, <p>, <ul>...) both work."}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full rounded-xl border border-border bg-background/50 px-4 py-2.5 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-all resize-y font-mono"
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button onClick={save} disabled={!title.trim() || saving} className="gap-2 min-w-[120px]">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
            {savedId ? "Save Changes" : "Create Article"}
          </Button>
        </div>

        {/* Publish flow — appears once the article exists */}
        {savedId && (
          <div className="border-t border-glass-border pt-4">
            <PublishPanel articleId={savedId} />
          </div>
        )}
      </div>
    </ModalShell>
  );
}

/* ============================================================
 * Category modal
 * ============================================================ */

function CategoryModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState("");
  const [color, setColor] = useState("#6366F1");
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (!name.trim() || saving) return;
    setSaving(true);
    try {
      await api.post(
        `/cms/categories?name=${encodeURIComponent(name.trim())}&color=${encodeURIComponent(color)}`,
      );
      toast.success("Category created");
      onCreated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to create category");
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalShell title="Add Category" subtitle="Organize your articles into categories" onClose={onClose}>
      <div className="space-y-4">
        <div>
          <label className={labelCls}>Name *</label>
          <Input placeholder="e.g. Technology, Marketing, SEO..." value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </div>
        <div>
          <label className={labelCls}>Color</label>
          <div className="flex items-center gap-3">
            <input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              className="h-10 w-14 rounded-lg border border-border bg-transparent cursor-pointer"
            />
            <span className="text-xs text-muted-foreground font-mono">{color}</span>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button onClick={save} disabled={!name.trim() || saving} className="gap-2">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />} Create Category
          </Button>
        </div>
      </div>
    </ModalShell>
  );
}

/* ============================================================
 * Tag modal
 * ============================================================ */

function TagModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (!name.trim() || saving) return;
    setSaving(true);
    try {
      await api.post(`/cms/tags?name=${encodeURIComponent(name.trim())}`);
      toast.success("Tag created");
      onCreated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to create tag");
    } finally {
      setSaving(false);
    }
  };

  return (
    <ModalShell title="Add Tag" subtitle="Tag articles for easier discovery" onClose={onClose}>
      <div className="space-y-4">
        <div>
          <label className={labelCls}>Tag name *</label>
          <Input placeholder="e.g. SEO, AI, Marketing..." value={name} onChange={(e) => setName(e.target.value)} autoFocus onKeyDown={(e) => e.key === "Enter" && save()} />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button onClick={save} disabled={!name.trim() || saving} className="gap-2">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Tags className="w-4 h-4" />} Create Tag
          </Button>
        </div>
      </div>
    </ModalShell>
  );
}
