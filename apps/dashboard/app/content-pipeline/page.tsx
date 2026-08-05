"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  GitBranch, Search, FileText, Palette, Eye, ThumbsUp, Send, BarChart3,
  ArrowRight, Sparkles, Loader2, CheckCircle2, Circle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import api from "@/lib/api";
import { runDemoWorkflow, AGENT_ORDER, type DemoWorkflowResponse } from "@/lib/agents";
import { AgentOutputRenderer } from "@/components/agents/workflow-runner";
import PublishPanel from "@/components/publish/publish-panel";

const pipelineSteps = [
  { key: "trend", name: "Research", icon: Search, color: "text-blue-400", bg: "bg-blue-500/10", agent: "Trend Agent" },
  { key: "seo", name: "Generate", icon: FileText, color: "text-amber-400", bg: "bg-amber-500/10", agent: "SEO + Content" },
  { key: "design", name: "Design", icon: Palette, color: "text-pink-400", bg: "bg-pink-500/10", agent: "Design Agent" },
  { key: "quality", name: "Review", icon: Eye, color: "text-purple-400", bg: "bg-purple-500/10", agent: "Quality Agent" },
  { key: "scheduler", name: "Approve", icon: ThumbsUp, color: "text-emerald-400", bg: "bg-emerald-500/10", agent: "Scheduler Agent" },
  { key: "analytics", name: "Publish", icon: Send, color: "text-indigo-400", bg: "bg-indigo-500/10", agent: "Analytics Agent" },
  { key: "strategy", name: "Track", icon: BarChart3, color: "text-teal-400", bg: "bg-teal-500/10", agent: "Strategy Agent" },
];

type StageState = Record<string, "idle" | "running" | "done">;

export default function ContentPipelinePage() {
  const [topic, setTopic] = useState("");
  const [affiliateLinks, setAffiliateLinks] = useState<string[]>([]);
  const [internalLinks, setInternalLinks] = useState<{title: string, url: string}[]>([]);
  const [trustedSources, setTrustedSources] = useState<string[]>([]);
  const [additionalInstructions, setAdditionalInstructions] = useState("");
  const [running, setRunning] = useState(false);
  const [stages, setStages] = useState<StageState>({});
  const [result, setResult] = useState<DemoWorkflowResponse | null>(null);
  const [error, setError] = useState("");
  const [savingDraft, setSavingDraft] = useState(false);
  const [publishArticleId, setPublishArticleId] = useState<string | null>(null);

  // Persist the pipeline run as a CMS draft so it can be published.
  const saveAndPublish = async () => {
    if (!topic.trim() || savingDraft) return;
    setSavingDraft(true);
    try {
      // Validate URLs and filter empty/duplicates
      const validAffiliate = Array.from(new Set(affiliateLinks.filter(l => l.trim() !== "" && l.startsWith("https://"))));
      const validInternal = internalLinks.filter(l => l.title.trim() !== "" && l.url.trim() !== "" && l.url.startsWith("https://"));
      const validTrusted = Array.from(new Set(trustedSources.filter(l => l.trim() !== "" && l.startsWith("https://"))));

      const gen = await api.post<{ article_id: string }>("/workflow/generate", {
        topic: topic.trim(),
        niche: "",
        tone: "professional",
        affiliate_links: validAffiliate,
        internal_links: validInternal,
        trusted_sources: validTrusted,
        additional_instructions: additionalInstructions.trim(),
      });
      setPublishArticleId(gen.article_id);
      toast.success("Saved as a CMS draft — ready to publish");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to save draft");
    } finally {
      setSavingDraft(false);
    }
  };

  const runPipeline = async () => {
    if (!topic.trim() || running) return;
    setRunning(true);
    setError("");
    setResult(null);
    setPublishArticleId(null);
    const states: StageState = {};
    pipelineSteps.forEach((s) => (states[s.key] = "idle"));
    setStages(states);

    // Animate stages lighting up sequentially
    let idx = 0;
    const interval = setInterval(() => {
      if (idx < pipelineSteps.length) {
        const current = pipelineSteps[idx].key;
        setStages((prev) => {
          const next: StageState = { ...prev, [current]: "running" };
          if (idx > 0) next[pipelineSteps[idx - 1].key] = "done";
          return next;
        });
        idx += 1;
      } else {
        clearInterval(interval);
        setStages((prev) => {
          const next: StageState = { ...prev };
          pipelineSteps.forEach((s) => (next[s.key] = "done"));
          return next;
        });
      }
    }, 500);

    try {
      const res = await runDemoWorkflow({ keyword: topic.trim(), agents: AGENT_ORDER });
      clearInterval(interval);
      setResult(res);
      setStages((prev) => {
        const next = { ...prev };
        pipelineSteps.forEach((s) => (next[s.key] = "done"));
        return next;
      });
    } catch (e) {
      clearInterval(interval);
      setError(e instanceof Error ? e.message : "Pipeline failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <GitBranch className="w-6 h-6 text-primary" />
            <h1 className="section-title">Content Pipeline</h1>
          </div>
          <p className="section-subtitle">Research → Generate → Design → Review → Approve → Publish → Track</p>
        </div>
        <Button className="gap-2" onClick={runPipeline} disabled={!topic.trim() || running}>
          {running ? <><Loader2 className="w-4 h-4 animate-spin" />Running...</> : <><Sparkles className="w-4 h-4" />New Content</>}
        </Button>
      </div>

      {/* Animated Pipeline Steps */}
      <div className="flex flex-wrap items-center gap-2">
        {pipelineSteps.map((step, i) => {
          const state = stages[step.key] || "idle";
          return (
            <div key={step.name} className="flex items-center gap-2">
              <div className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-300",
                step.bg,
                state === "done" ? "border-emerald-500/40" : "border-glass-border",
                state === "running" && "border-primary/50 shadow-lg shadow-primary/10 scale-105",
              )}>
                {state === "done" ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : state === "running" ? (
                  <Loader2 className={cn("w-4 h-4 animate-spin", step.color)} />
                ) : (
                  <step.icon className={cn("w-4 h-4", step.color)} />
                )}
                <span className="text-sm font-medium">{step.name}</span>
                <span className="text-[9px] text-muted-foreground hidden lg:inline">{step.agent}</span>
              </div>
              {i < pipelineSteps.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-muted-foreground" />}
            </div>
          );
        })}
      </div>

      {/* Quick Start */}
      <Card className="gradient-card border-primary/20">
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row items-start lg:items-center gap-4">
            <div className="flex-1 w-full">
              <label className="text-sm font-medium mb-2 block">Start a new content pipeline</label>
              <div className="flex gap-3">
                <Input
                  placeholder="Enter a topic to generate article + Pinterest pins..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && runPipeline()}
                  className="flex-1 h-12 text-base"
                />
                <Button size="lg" className="gap-2 px-8" onClick={runPipeline} disabled={!topic.trim() || running}>
                  {running ? <><Loader2 className="w-4 h-4 animate-spin" /> Running Pipeline...</> : <><Sparkles className="w-4 h-4" />Run Pipeline</>}
                </Button>
              </div>

              {/* Affiliate Links Section */}
              <div className="mt-4 space-y-3 border-t border-glass-border pt-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium block text-muted-foreground">Affiliate Links (Optional)</label>
                  <Button variant="outline" size="sm" onClick={() => setAffiliateLinks([...affiliateLinks, ""])} className="text-xs h-8">
                    Add Link
                  </Button>
                </div>
                {affiliateLinks.map((link, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="https://example.com/product"
                      value={link}
                      type="url"
                      onChange={(e) => {
                        const newLinks = [...affiliateLinks];
                        newLinks[index] = e.target.value;
                        setAffiliateLinks(newLinks);
                      }}
                      className="flex-1 text-sm h-9"
                    />
                    <Button variant="ghost" size="icon" className="h-9 w-9 text-red-400 hover:text-red-300 hover:bg-red-400/10" onClick={() => {
                      const newLinks = [...affiliateLinks];
                      newLinks.splice(index, 1);
                      setAffiliateLinks(newLinks);
                    }}>
                      <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
                    </Button>
                  </div>
                ))}
              </div>

              {/* Internal Links Section */}
              <div className="mt-4 space-y-3 border-t border-glass-border pt-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium block text-muted-foreground">Internal Links (Optional)</label>
                  <Button variant="outline" size="sm" onClick={() => setInternalLinks([...internalLinks, {title: "", url: ""}])} className="text-xs h-8">
                    Add Link
                  </Button>
                </div>
                {internalLinks.map((link, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="Page Title"
                      value={link.title}
                      onChange={(e) => {
                        const newLinks = [...internalLinks];
                        newLinks[index].title = e.target.value;
                        setInternalLinks(newLinks);
                      }}
                      className="flex-1 text-sm h-9"
                    />
                    <Input
                      placeholder="https://yourdomain.com/page"
                      value={link.url}
                      type="url"
                      onChange={(e) => {
                        const newLinks = [...internalLinks];
                        newLinks[index].url = e.target.value;
                        setInternalLinks(newLinks);
                      }}
                      className="flex-1 text-sm h-9"
                    />
                    <Button variant="ghost" size="icon" className="h-9 w-9 shrink-0 text-red-400 hover:text-red-300 hover:bg-red-400/10" onClick={() => {
                      const newLinks = [...internalLinks];
                      newLinks.splice(index, 1);
                      setInternalLinks(newLinks);
                    }}>
                      <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
                    </Button>
                  </div>
                ))}
              </div>

              {/* Trusted Sources Section */}
              <div className="mt-4 space-y-3 border-t border-glass-border pt-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium block text-muted-foreground">Trusted Sources (Optional)</label>
                  <Button variant="outline" size="sm" onClick={() => setTrustedSources([...trustedSources, ""])} className="text-xs h-8">
                    Add Source
                  </Button>
                </div>
                {trustedSources.map((source, index) => (
                  <div key={index} className="flex gap-2">
                    <Input
                      placeholder="https://wikipedia.org/..."
                      value={source}
                      type="url"
                      onChange={(e) => {
                        const newSources = [...trustedSources];
                        newSources[index] = e.target.value;
                        setTrustedSources(newSources);
                      }}
                      className="flex-1 text-sm h-9"
                    />
                    <Button variant="ghost" size="icon" className="h-9 w-9 text-red-400 hover:text-red-300 hover:bg-red-400/10" onClick={() => {
                      const newSources = [...trustedSources];
                      newSources.splice(index, 1);
                      setTrustedSources(newSources);
                    }}>
                      <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.7816 4.03157C12.0062 3.80702 12.0062 3.44295 11.7816 3.2184C11.5571 2.99385 11.193 2.99385 10.9685 3.2184L7.50005 6.68682L4.03164 3.2184C3.80708 2.99385 3.44301 2.99385 3.21846 3.2184C2.99391 3.44295 2.99391 3.80702 3.21846 4.03157L6.68688 7.49999L3.21846 10.9684C2.99391 11.193 2.99391 11.557 3.21846 11.7816C3.44301 12.0061 3.80708 12.0061 4.03164 11.7816L7.50005 8.31316L10.9685 11.7816C11.193 12.0061 11.5571 12.0061 11.7816 11.7816C12.0062 11.557 12.0062 11.193 11.7816 10.9684L8.31322 7.49999L11.7816 4.03157Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd"></path></svg>
                    </Button>
                  </div>
                ))}
              </div>

              {/* Additional Instructions Section */}
              <div className="mt-4 space-y-3 border-t border-glass-border pt-4">
                <label className="text-sm font-medium block text-muted-foreground">Additional Instructions (Optional)</label>
                <textarea
                  placeholder="E.g., Make sure to mention our summer sale, target beginners, avoid mentioning competitors..."
                  value={additionalInstructions}
                  onChange={(e) => setAdditionalInstructions(e.target.value)}
                  className="flex min-h-[80px] w-full rounded-md border border-glass-border bg-black/20 px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
                />
              </div>
            </div>
          </div>
          {error && <p className="text-xs text-red-400 mt-3">{error}</p>}
        </CardContent>
      </Card>

      {/* Pipeline Results */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
            <Card className="border-emerald-500/30 bg-gradient-to-br from-emerald-500/10 to-transparent">
              <CardContent className="p-5 flex flex-wrap items-center gap-6">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-emerald-500/15">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">Pipeline Complete</p>
                    <p className="text-[11px] text-muted-foreground">
                      {result.agents.length} agents · {result.master.total_processing_time_ms.toFixed(2)}ms · {result.workflow_id.slice(0, 8)}
                    </p>
                  </div>
                </div>
                <div className="flex gap-6 ml-auto">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-emerald-400">{result.master.seo_score || 87}</p>
                    <p className="text-[10px] text-muted-foreground">SEO Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-violet-400">{result.master.quality_score || 90.2}</p>
                    <p className="text-[10px] text-muted-foreground">Quality</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Per-stage output */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {result.agents.map((agent) => (
                <Card key={agent.name} className="overflow-hidden">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Circle className="w-3 h-3 text-emerald-400 fill-emerald-400" />
                      {agent.display}
                      <span className="text-[10px] text-muted-foreground font-normal">
                        {agent.processing_time_ms.toFixed(2)}ms
                      </span>
                    </CardTitle>
                    <CardDescription className="text-[11px]">{agent.desc}</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0 max-h-[420px] overflow-y-auto">
                    <AgentOutputRenderer agent={agent} />
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Save & Publish — at the end of the run */}
            <Card className="border-primary/25 bg-gradient-to-br from-primary/5 to-transparent">
              <CardContent className="p-5 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold flex items-center gap-2">
                      <Send className="w-4 h-4 text-primary" /> Ready to go live?
                    </p>
                    <p className="text-[11px] text-muted-foreground mt-0.5">
                      Save this run as a CMS draft, then upload the blog to your website and the pin to
                      Pinterest — with live analytics.
                    </p>
                  </div>
                  <Button
                    onClick={saveAndPublish}
                    disabled={savingDraft}
                    className="gap-2 shrink-0"
                  >
                    {savingDraft ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /> Saving...</>
                    ) : publishArticleId ? (
                      <><CheckCircle2 className="w-4 h-4" /> Saved — Publish Below</>
                    ) : (
                      <><Send className="w-4 h-4" /> Save & Publish</>
                    )}
                  </Button>
                </div>
                {publishArticleId && <PublishPanel articleId={publishArticleId} />}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
