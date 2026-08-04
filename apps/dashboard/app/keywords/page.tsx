"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, TrendingUp, Filter, Download, Loader2, Target } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AgentOutputRenderer } from "@/components/agents/workflow-runner";
import { runDemoWorkflow, type DemoWorkflowResponse } from "@/lib/agents";

export default function KeywordsPage() {
  const [keyword, setKeyword] = useState("");
  const [result, setResult] = useState<DemoWorkflowResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const research = async () => {
    if (!keyword.trim() || running) return;
    setRunning(true);
    setError("");
    try {
      const res = await runDemoWorkflow({ keyword: keyword.trim(), agents: ["seo", "trend"] });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Research failed");
    } finally {
      setRunning(false);
    }
  };

  const seoAgent = result?.agents.find((a) => a.name === "seo");
  const trendAgent = result?.agents.find((a) => a.name === "trend");

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Search className="w-6 h-6 text-emerald-400" />
            <h1 className="section-title">Keyword Research</h1>
          </div>
          <p className="section-subtitle">Powered by the SEO Agent — live research runs</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2" disabled><Filter className="w-4 h-4" />Filters</Button>
          <Button variant="outline" className="gap-2" disabled><Download className="w-4 h-4" />Export</Button>
        </div>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1 max-w-2xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search for keywords... e.g., pinterest marketing"
            className="pl-10 h-12 text-base"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && research()}
          />
        </div>
        <Button size="lg" className="gap-2 px-8" onClick={research} disabled={!keyword.trim() || running}>
          {running ? <><Loader2 className="w-4 h-4 animate-spin" />Researching...</> : <><TrendingUp className="w-4 h-4" />Research</>}
        </Button>
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}

      <Card>
        <CardHeader>
          <CardTitle>Keyword Suggestions</CardTitle>
          <CardDescription>
            {result
              ? `${result.keyword} — SEO Agent found clusters, long-tail terms, intent, and difficulty in ${result.master.total_processing_time_ms.toFixed(2)}ms`
              : "Enter a keyword to see related terms and analytics"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!result ? (
            <div className="text-center py-16 text-muted-foreground">
              <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Enter a keyword to start researching</p>
              <p className="text-sm">Get keyword clusters, long-tail suggestions, and SEO scores</p>
            </div>
          ) : (
            <div className="space-y-4">
              {seoAgent && (
                <div className="rounded-xl border border-glass-border overflow-hidden">
                  <div className="px-4 py-3 bg-emerald-500/5 border-b border-glass-border flex items-center gap-2">
                    <Target className="w-4 h-4 text-emerald-400" />
                    <p className="text-xs font-semibold">SEO Agent — Full Keyword Analysis</p>
                  </div>
                  <div className="p-4"><AgentOutputRenderer agent={seoAgent} /></div>
                </div>
              )}
              {trendAgent && (
                <div className="rounded-xl border border-glass-border overflow-hidden">
                  <div className="px-4 py-3 bg-blue-500/5 border-b border-glass-border flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-blue-400" />
                    <p className="text-xs font-semibold">Trend Agent — Opportunity Context</p>
                  </div>
                  <div className="p-4"><AgentOutputRenderer agent={trendAgent} /></div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
