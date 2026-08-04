"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Search, Sparkles, Loader2, Flame } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AgentOutputRenderer } from "@/components/agents/workflow-runner";
import { runDemoWorkflow, type DemoWorkflowResponse } from "@/lib/agents";

export default function TrendsPage() {
  const [keyword, setKeyword] = useState("");
  const [result, setResult] = useState<DemoWorkflowResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const discover = async () => {
    if (!keyword.trim() || running) return;
    setRunning(true);
    setError("");
    try {
      const res = await runDemoWorkflow({ keyword: keyword.trim(), agents: ["trend", "strategy"] });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Trend scan failed");
    } finally {
      setRunning(false);
    }
  };

  const trendAgent = result?.agents.find((a) => a.name === "trend");
  const strategyAgent = result?.agents.find((a) => a.name === "strategy");

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-blue-400" />
            <h1 className="section-title">Trend Discovery</h1>
          </div>
          <p className="section-subtitle">Discover trending topics and content opportunities — live Trend Agent runs</p>
        </div>
        <Button className="gap-2" onClick={discover} disabled={!keyword.trim() || running}>
          {running ? <><Loader2 className="w-4 h-4 animate-spin" />Scanning...</> : <><Sparkles className="w-4 h-4" />Scan Trends</>}
        </Button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1 max-w-2xl">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Enter a niche or keyword to discover trends..."
            className="pl-10 h-12 text-base"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && discover()}
          />
        </div>
        <Button size="lg" className="gap-2 px-8" onClick={discover} disabled={!keyword.trim() || running}>
          {running ? <><Loader2 className="w-4 h-4 animate-spin" />Discovering...</> : <><TrendingUp className="w-4 h-4" />Discover</>}
        </Button>
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}

      <Card>
        <CardHeader>
          <CardTitle>Trending Topics</CardTitle>
          <CardDescription>
            {result
              ? `Trend Agent + Strategy Agent completed in ${result.master.total_processing_time_ms.toFixed(2)}ms`
              : "Powered by the Trend Agent"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!result ? (
            <div className="text-center py-16 text-muted-foreground">
              <Flame className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Enter a keyword to discover trending topics</p>
              <p className="text-sm">Get opportunity scores, competition estimates, and seasonal insights</p>
            </div>
          ) : (
            <div className="space-y-4">
              {trendAgent && (
                <div className="rounded-xl border border-glass-border overflow-hidden">
                  <div className="px-4 py-3 bg-blue-500/5 border-b border-glass-border flex items-center gap-2">
                    <Flame className="w-4 h-4 text-blue-400" />
                    <p className="text-xs font-semibold">Trend Agent — Opportunity Scan</p>
                  </div>
                  <div className="p-4"><AgentOutputRenderer agent={trendAgent} /></div>
                </div>
              )}
              {strategyAgent && (
                <div className="rounded-xl border border-glass-border overflow-hidden">
                  <div className="px-4 py-3 bg-violet-500/5 border-b border-glass-border flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-violet-400" />
                    <p className="text-xs font-semibold">Strategy Agent — Growth Recommendations</p>
                  </div>
                  <div className="p-4"><AgentOutputRenderer agent={strategyAgent} /></div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
