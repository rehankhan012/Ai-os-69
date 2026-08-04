"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  Send, Globe, Pin, CheckCircle2, XCircle, Loader2, Radio,
  Eye, MousePointerClick, Bookmark, ExternalLink, RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

/* ============================================================
 * Types
 * ============================================================ */

interface StepResult {
  status: string;
  message: string;
  url?: string;
  site?: string;
  external_id?: string;
  pin_id?: string;
}

interface PublishReport {
  article_id: string;
  cms: StepResult;
  website: StepResult;
  pinterest: StepResult;
  article: { id: string; status: string };
}

interface AnalyticsSummary {
  total_pins: number;
  total_clicks: number;
  total_impressions: number;
  total_saves: number;
  outbound_clicks: number;
  ctr: number;
  growth_percentage: number;
  best_posting_time?: string | null;
}

/* ============================================================
 * Component
 * ============================================================ */

export default function PublishPanel({ articleId }: { articleId: string }) {
  const [publishing, setPublishing] = useState(false);
  const [report, setReport] = useState<PublishReport | null>(null);
  const [error, setError] = useState("");
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const refreshAnalytics = useCallback(async () => {
    try {
      const res = await api.get<AnalyticsSummary>("/analytics/summary", { days: 30 });
      setAnalytics(res);
      setLastUpdated(new Date());
    } catch {
      // Analytics are best-effort — keep the panel usable if it fails
    }
  }, []);

  // Continuously check analytics once published
  useEffect(() => {
    if (report && pollRef.current === null) {
      refreshAnalytics();
      pollRef.current = setInterval(refreshAnalytics, 5000);
    }
    return stopPolling;
  }, [report, refreshAnalytics, stopPolling]);

  const publish = async () => {
    if (publishing) return;
    setPublishing(true);
    setError("");
    setReport(null);
    try {
      const res = await api.post<PublishReport>(`/articles/${articleId}/publish`);
      setReport(res);
      const failed = [res.cms, res.website, res.pinterest].some((s) => s.status === "error");
      toast.success(failed ? "Published with some steps pending" : "Published successfully");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Publish failed");
      toast.error(e instanceof Error ? e.message : "Publish failed");
    } finally {
      setPublishing(false);
    }
  };

  const stepStatus = (s: StepResult | undefined) => {
    if (!s) return "idle";
    return s.status; // published | skipped | local_only | error
  };

  const StepRow = ({ icon, label, step }: { icon: React.ReactNode; label: string; step: StepResult | undefined }) => {
    const status = stepStatus(step);
    return (
      <div className="flex items-start gap-3 rounded-xl border border-glass-border bg-glass p-3">
        <div className={cn(
          "p-1.5 rounded-lg shrink-0",
          status === "published" && "bg-emerald-500/10 text-emerald-400",
          status === "error" && "bg-red-500/10 text-red-400",
          (status === "skipped" || status === "local_only") && "bg-amber-500/10 text-amber-400",
          status === "idle" && "bg-muted text-muted-foreground",
        )}>
          {status === "published"
            ? <CheckCircle2 className="w-4 h-4" />
            : status === "error"
              ? <XCircle className="w-4 h-4" />
              : icon}
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <p className="text-xs font-semibold">{label}</p>
            <span className={cn(
              "text-[10px] px-1.5 py-0.5 rounded-full font-medium capitalize",
              status === "published" && "bg-emerald-500/15 text-emerald-400",
              status === "error" && "bg-red-500/15 text-red-400",
              (status === "skipped" || status === "local_only") && "bg-amber-500/15 text-amber-400",
            )}>
              {status === "local_only" ? "local" : status}
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground mt-1">{step?.message || "Waiting..."}</p>
          {step?.url && (
            <a href={step.url} target="_blank" rel="noreferrer" className="text-[11px] text-primary hover:underline inline-flex items-center gap-1 mt-1">
              <ExternalLink className="w-3 h-3" /> View on site
            </a>
          )}
        </div>
      </div>
    );
  };

  const metrics = [
    { label: "Impressions", value: analytics?.total_impressions ?? 0, icon: Eye, color: "text-blue-400" },
    { label: "Saves", value: analytics?.total_saves ?? 0, icon: Bookmark, color: "text-pink-400" },
    { label: "Clicks", value: analytics?.total_clicks ?? 0, icon: MousePointerClick, color: "text-emerald-400" },
    { label: "CTR", value: analytics ? `${analytics.ctr}%` : "0%", icon: RefreshCw, color: "text-violet-400" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold flex items-center gap-2">
            <Send className="w-4 h-4 text-primary" /> Publish to Website & Pinterest
          </p>
          <p className="text-[11px] text-muted-foreground mt-0.5">
            Upload the blog to your website and the pin to Pinterest, then track analytics live.
          </p>
        </div>
        <Button onClick={publish} disabled={publishing} className="gap-2 shrink-0">
          {publishing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          {publishing ? "Publishing..." : report ? "Publish Again" : "Publish"}
        </Button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">{error}</div>
      )}

      <AnimatePresence>
        {publishing && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex items-center gap-2 text-xs text-muted-foreground">
            <Loader2 className="w-3.5 h-3.5 animate-spin" /> Publishing article, uploading pin, and notifying channels...
          </motion.div>
        )}
      </AnimatePresence>

      {report && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-2">
          <StepRow icon={<Globe className="w-4 h-4" />} label="Website (darkverseblog.vercel.app)" step={report.website} />
          <StepRow icon={<Pin className="w-4 h-4" />} label="Pinterest pin" step={report.pinterest} />
          <StepRow icon={<CheckCircle2 className="w-4 h-4" />} label="CMS" step={report.cms} />
        </motion.div>
      )}

      {/* Live analytics */}
      {report && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-primary/20 bg-gradient-to-br from-primary/5 to-transparent p-4 space-y-3"
        >
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold flex items-center gap-2">
              <Radio className="w-3.5 h-3.5 text-primary animate-pulse" /> Live Analytics
            </p>
            <span className="text-[10px] text-muted-foreground flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              auto-refresh every 5s{lastUpdated && ` · ${lastUpdated.toLocaleTimeString()}`}
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {metrics.map((m) => (
              <div key={m.label} className="rounded-lg bg-glass border border-glass-border p-2.5 text-center">
                <m.icon className={cn("w-4 h-4 mx-auto mb-1", m.color)} />
                <p className="text-lg font-bold leading-none">{String(m.value)}</p>
                <p className="text-[9px] uppercase tracking-wide text-muted-foreground mt-1">{m.label}</p>
              </div>
            ))}
          </div>
          {analytics && analytics.growth_percentage > 0 && (
            <p className="text-[11px] text-emerald-400">
              ▲ {analytics.growth_percentage}% growth · {analytics.total_pins} total pins
              {analytics.best_posting_time ? ` · best time ${analytics.best_posting_time}` : ""}
            </p>
          )}
        </motion.div>
      )}
    </div>
  );
}
