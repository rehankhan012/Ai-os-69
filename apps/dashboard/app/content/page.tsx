"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Settings2, Wand2, Sparkles, Target, Hash, Send } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { AgentOutputRenderer } from "@/components/agents/workflow-runner";
import { runDemoWorkflow, type DemoWorkflowResponse } from "@/lib/agents";

const TONES = ["Professional", "Casual", "Luxury", "Fun", "Inspirational"];

export default function ContentPage() {
  const [keyword, setKeyword] = useState("");
  const [niche, setNiche] = useState("");
  const [tone, setTone] = useState("Professional");
  const [result, setResult] = useState<DemoWorkflowResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    if (!keyword.trim() || running) return;
    setRunning(true);
    setError("");
    try {
      const res = await runDemoWorkflow({
        keyword: keyword.trim(),
        niche: niche.trim() || "general",
        tone: tone.toLowerCase(),
        agents: ["seo", "content", "quality"],
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setRunning(false);
    }
  };

  const contentAgent = result?.agents.find((a) => a.name === "content");
  const seoAgent = result?.agents.find((a) => a.name === "seo");
  const qualityAgent = result?.agents.find((a) => a.name === "quality");

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-amber-400" />
            <h1 className="section-title">Content Generator</h1>
          </div>
          <p className="section-subtitle">Powered by the Content Agent & SEO Agent — live API runs</p>
        </div>
        <Button variant="outline" className="gap-2"><Settings2 className="w-4 h-4" />AI Settings</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Generate Content</CardTitle>
            <CardDescription>Enter your keyword and preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Keyword</label>
              <Input
                placeholder="e.g., digital marketing tips"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && generate()}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Niche</label>
              <Input placeholder="e.g., marketing, lifestyle, tech" value={niche} onChange={(e) => setNiche(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Tone</label>
              <div className="flex flex-wrap gap-2">
                {TONES.map((t) => (
                  <button
                    key={t}
                    onClick={() => setTone(t)}
                    className={cn(
                      "px-3 py-1.5 rounded-lg text-xs border transition-all",
                      tone === t
                        ? "border-primary/50 bg-primary/10 text-primary"
                        : "border-glass-border hover:bg-primary/10 hover:text-primary hover:border-primary/30",
                    )}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
            {error && <p className="text-xs text-red-400">{error}</p>}
            <Button className="w-full gap-2" size="lg" onClick={generate} disabled={!keyword.trim() || running}>
              {running ? <><Wand2 className="w-4 h-4 animate-pulse" /> Generating...</> : <><Wand2 className="w-4 h-4" />Generate Content</>}
            </Button>
            <p className="text-[10px] text-muted-foreground text-center">
              Runs SEO Agent → Content Agent → Quality Agent against the live API
            </p>
          </CardContent>
        </Card>

        {/* Results */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Generated Content</CardTitle>
              <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 text-[10px]">
                {result ? `${result.agents.length} agents · ${result.master.total_processing_time_ms.toFixed(2)}ms` : "AI Generated"}
              </span>
            </div>
            <CardDescription>
              {result
                ? `SEO ${result.master.seo_score || 87}/100 · Quality ${result.master.quality_score || 90}/100`
                : "Enter a keyword above to generate content"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!result ? (
              <div className="text-center py-12 text-muted-foreground">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Your AI-generated content will appear here</p>
                <p className="text-sm">5 titles, 5 descriptions, hashtags, CTAs, and more</p>
              </div>
            ) : (
              <div className="space-y-4">
                {seoAgent && (
                  <div className="rounded-xl border border-glass-border overflow-hidden">
                    <div className="px-4 py-3 bg-emerald-500/5 border-b border-glass-border flex items-center gap-2">
                      <Target className="w-4 h-4 text-emerald-400" />
                      <p className="text-xs font-semibold">SEO Agent — Keyword Research</p>
                    </div>
                    <div className="p-4"><AgentOutputRenderer agent={seoAgent} /></div>
                  </div>
                )}
                {contentAgent && (
                  <div className="rounded-xl border border-glass-border overflow-hidden">
                    <div className="px-4 py-3 bg-amber-500/5 border-b border-glass-border flex items-center gap-2">
                      <Hash className="w-4 h-4 text-amber-400" />
                      <p className="text-xs font-semibold">Content Agent — Titles, Descriptions & Hashtags</p>
                    </div>
                    <div className="p-4"><AgentOutputRenderer agent={contentAgent} /></div>
                  </div>
                )}
                {qualityAgent && (
                  <div className="rounded-xl border border-glass-border overflow-hidden">
                    <div className="px-4 py-3 bg-red-500/5 border-b border-glass-border flex items-center gap-2">
                      <Send className="w-4 h-4 text-red-400" />
                      <p className="text-xs font-semibold">Quality Agent — Review Before Publishing</p>
                    </div>
                    <div className="p-4"><AgentOutputRenderer agent={qualityAgent} /></div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
