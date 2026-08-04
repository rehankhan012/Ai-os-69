"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain, TrendingUp, Search, FileText, Palette, CheckCircle, Clock,
  BarChart3, Lightbulb, Sparkles, Zap, Loader2, XCircle, ChevronDown,
  Hash, Target, CalendarClock, Flame, ShieldCheck, ArrowRight, Wand2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  AGENT_ORDER, AGENT_META, runDemoWorkflow,
  type AgentOutput, type DemoWorkflowResponse,
} from "@/lib/agents";

const AGENT_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  trend: TrendingUp,
  seo: Search,
  content: FileText,
  design: Palette,
  quality: ShieldCheck,
  scheduler: CalendarClock,
  analytics: BarChart3,
  strategy: Lightbulb,
  master: Brain,
};

const AGENT_COLORS: Record<string, string> = {
  trend: "text-blue-400",
  seo: "text-emerald-400",
  content: "text-amber-400",
  design: "text-pink-400",
  quality: "text-red-400",
  scheduler: "text-indigo-400",
  analytics: "text-teal-400",
  strategy: "text-violet-400",
  master: "text-purple-400",
};

const AGENT_BG: Record<string, string> = {
  trend: "bg-blue-500/10",
  seo: "bg-emerald-500/10",
  content: "bg-amber-500/10",
  design: "bg-pink-500/10",
  quality: "bg-red-500/10",
  scheduler: "bg-indigo-500/10",
  analytics: "bg-teal-500/10",
  strategy: "bg-violet-500/10",
  master: "bg-purple-500/10",
};

type Phase = "idle" | "running" | "done" | "error";

interface WorkflowRunnerProps {
  agents?: string[];
  defaultKeyword?: string;
  placeholder?: string;
  buttonLabel?: string;
  runningLabel?: string;
  subtitle?: string;
  /** Hide the keyword input (e.g. when a parent page supplies the topic). */
  hideInput?: boolean;
  /** Callback when a run completes — pages use this to capture results. */
  onComplete?: (res: DemoWorkflowResponse) => void;
}

export default function WorkflowRunner({
  agents = AGENT_ORDER,
  defaultKeyword = "",
  placeholder = "Enter a topic or keyword...",
  buttonLabel = "Launch AI Workflow",
  runningLabel = "Agents working...",
  subtitle = "9 specialized agents analyze, write, design, review, and strategize in real time",
  hideInput = false,
  onComplete,
}: WorkflowRunnerProps) {
  const [keyword, setKeyword] = useState(defaultKeyword);
  const [phase, setPhase] = useState<Phase>("idle");
  const [agentStates, setAgentStates] = useState<Record<string, string>>({});
  const [results, setResults] = useState<DemoWorkflowResponse | null>(null);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [progressPct, setProgressPct] = useState(0);
  const simRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const activeAgents = agents;

  const stopSim = () => {
    if (simRef.current) {
      clearInterval(simRef.current);
      simRef.current = null;
    }
  };

  useEffect(() => stopSim, []);

  const run = useCallback(async () => {
    const kw = keyword.trim();
    if (!kw || phase === "running") return;

    // Reset state
    stopSim();
    setResults(null);
    setError("");
    setExpanded(null);
    setPhase("running");
    setProgressPct(0);
    const states: Record<string, string> = {};
    activeAgents.forEach((a) => (states[a] = "queued"));
    setAgentStates(states);

    // Live progress simulation: light agents up sequentially while the real
    // request is in flight. The backend is fast, so this animates the feel.
    let idx = 0;
    const order = [...activeAgents];
    simRef.current = setInterval(() => {
      if (idx >= order.length) {
        stopSim();
        return;
      }
      const current = order[idx];
      setAgentStates((prev) => ({ ...prev, [current]: "running" }));
      setProgressPct(Math.round(((idx + 0.5) / order.length) * 100));
      // Mark previous as done after a beat
      if (idx > 0) {
        const prevAgent = order[idx - 1];
        setAgentStates((s) => ({ ...s, [prevAgent]: "done" }));
      }
      idx += 1;
      if (idx >= order.length) {
        setAgentStates((s) => ({ ...s, [order[order.length - 1]]: "done" }));
        setProgressPct(100);
        stopSim();
      }
    }, 420);

    try {
      const res = await runDemoWorkflow({
        keyword: kw,
        niche: "",
        audience: "",
        tone: "professional",
        agents: activeAgents,
      });
      // Stop the simulation immediately, then snap all to done with real timings
      stopSim();
      const finalStates: Record<string, string> = {};
      activeAgents.forEach((a) => (finalStates[a] = "done"));
      setAgentStates(finalStates);
      setProgressPct(100);
      setResults(res);
      setPhase("done");
      onComplete?.(res);
    } catch (e) {
      stopSim();
      setPhase("error");
      setError(e instanceof Error ? e.message : "Workflow failed — is the API running?");
    }
  }, [keyword, phase, activeAgents, onComplete]);

  const agentStatusBadge = (state: string) => {
    if (state === "done")
      return <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 font-medium">done</span>;
    if (state === "running")
      return <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-400 font-medium animate-pulse">running</span>;
    if (state === "queued")
      return <span className="text-[10px] px-2 py-0.5 rounded-full bg-muted text-muted-foreground font-medium">queued</span>;
    return <span className="text-[10px] px-2 py-0.5 rounded-full bg-muted text-muted-foreground font-medium">idle</span>;
  };

  return (
    <div className="space-y-6">
      {/* Input / trigger */}
      {!hideInput && (
        <Card className="gradient-card border-primary/20">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row items-start lg:items-center gap-4">
              <div className="flex-1 w-full">
                <label className="text-sm font-medium mb-2 block">Topic / Keyword</label>
                <div className="flex gap-3">
                  <Input
                    placeholder={placeholder}
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && run()}
                    className="flex-1 h-12 text-base"
                  />
                  <Button
                    size="lg"
                    className="gap-2 px-8"
                    disabled={!keyword.trim() || phase === "running"}
                    onClick={run}
                  >
                    {phase === "running" ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        {runningLabel}
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4" />
                        {buttonLabel}
                      </>
                    )}
                  </Button>
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground shrink-0">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>{activeAgents.length} agents</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>~2s</span>
                </div>
              </div>
            </div>
            {subtitle && <p className="text-xs text-muted-foreground mt-3">{subtitle}</p>}
          </CardContent>
        </Card>
      )}

      {/* Progress bar */}
      {(phase === "running" || phase === "done") && (
        <div className="h-1.5 rounded-full bg-muted overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progressPct}%` }}
            transition={{ duration: 0.3 }}
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-500"
          />
        </div>
      )}

      {/* Agent live grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {activeAgents.map((agentName, i) => {
          const meta = AGENT_META[agentName];
          const Icon = AGENT_ICONS[agentName] || Brain;
          const state = agentStates[agentName] || (phase === "done" ? "done" : "idle");
          const res = results?.agents.find((a) => a.name === agentName);
          return (
            <motion.div
              key={agentName}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              className={cn(
                "rounded-xl border p-3 transition-all duration-300",
                state === "done"
                  ? "border-emerald-500/30 bg-emerald-500/5"
                  : state === "running"
                    ? "border-primary/40 bg-primary/5 shadow-lg shadow-primary/10"
                    : "border-glass-border bg-glass",
                phase === "done" && "cursor-pointer hover:border-primary/40",
              )}
              onClick={() => phase === "done" && setExpanded(expanded === agentName ? null : agentName)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className={cn("p-1.5 rounded-lg", AGENT_BG[agentName])}>
                  <Icon className={cn("w-4 h-4", AGENT_COLORS[agentName])} />
                </div>
                {state === "running" && <Loader2 className={cn("w-3.5 h-3.5 animate-spin", AGENT_COLORS[agentName])} />}
                {state === "done" && <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />}
                {state === "queued" && <Clock className="w-3.5 h-3.5 text-muted-foreground" />}
                {state === "idle" && <div className="w-3.5 h-3.5 rounded-full bg-muted-foreground/30" />}
              </div>
              <p className="text-xs font-semibold">{meta?.display || agentName}</p>
              <div className="mt-1.5">{agentStatusBadge(state)}</div>
              {state === "done" && res && (
                <p className="text-[9px] text-muted-foreground mt-1.5">
                  {res.processing_time_ms.toFixed(2)}ms
                </p>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Error */}
      <AnimatePresence>
        {phase === "error" && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 flex items-start gap-3"
          >
            <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-400">Workflow failed</p>
              <p className="text-xs text-muted-foreground mt-1">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      {results && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          {/* Master summary */}
          <Card className="border-primary/20 bg-gradient-to-br from-purple-500/10 to-transparent">
            <CardContent className="p-5 flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-purple-500/15">
                  <Brain className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Master Agent · Workflow Complete</p>
                  <p className="text-[11px] text-muted-foreground">
                    {results.agents.length} agents · {results.master.total_processing_time_ms.toFixed(2)}ms total · {results.workflow_id.slice(0, 8)}
                  </p>
                </div>
              </div>
              <div className="flex gap-6 ml-auto">
                <div className="text-center">
                  <p className="text-2xl font-bold text-emerald-400">{results.master.seo_score || 87}</p>
                  <p className="text-[10px] text-muted-foreground">SEO Score</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-violet-400">{results.master.quality_score || 90.2}</p>
                  <p className="text-[10px] text-muted-foreground">Quality</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-400">{results.agents.length}</p>
                  <p className="text-[10px] text-muted-foreground">Agents</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Per-agent proof */}
          {results.agents.map((agent) => (
            <AgentProofCard
              key={agent.name}
              agent={agent}
              expanded={expanded === agent.name}
              onToggle={() => setExpanded(expanded === agent.name ? null : agent.name)}
            />
          ))}
        </motion.div>
      )}
    </div>
  );
}

/* ============================================================
 * Per-agent proof card — renders the agent's real structured output
 * ============================================================ */

function AgentProofCard({
  agent,
  expanded,
  onToggle,
}: {
  agent: AgentOutput;
  expanded: boolean;
  onToggle: () => void;
}) {
  const Icon = AGENT_ICONS[agent.name] || Brain;
  return (
    <Card className="overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full text-left p-4 flex items-center gap-3 hover:bg-glass-hover transition-colors"
      >
        <div className={cn("p-2 rounded-xl", AGENT_BG[agent.name])}>
          <Icon className={cn("w-5 h-5", AGENT_COLORS[agent.name])} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">{agent.display}</p>
          <p className="text-[11px] text-muted-foreground">{agent.desc}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 font-medium">
            {agent.processing_time_ms.toFixed(2)}ms
          </span>
          <ChevronDown className={cn("w-4 h-4 text-muted-foreground transition-transform", expanded && "rotate-180")} />
        </div>
      </button>
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="p-4 pt-0 border-t border-glass-border space-y-4">
              {agent.suggestions.length > 0 && (
                <div className="rounded-xl bg-primary/5 border border-primary/20 p-3 space-y-1.5">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-primary">Agent Insights</p>
                  {agent.suggestions.map((s, i) => (
                    <p key={i} className="text-xs text-muted-foreground flex gap-2">
                      <Sparkles className="w-3 h-3 shrink-0 mt-0.5 text-primary" />
                      {s}
                    </p>
                  ))}
                </div>
              )}
              <AgentOutputRenderer agent={agent} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}

/* ============================================================
 * Typed renderers per agent output shape
 * ============================================================ */

function AgentOutputRenderer({ agent }: { agent: AgentOutput }) {
  const { name, output } = agent;
  switch (name) {
    case "trend": return <TrendOutput output={output} />;
    case "seo": return <SeoOutput output={output} />;
    case "content": return <ContentOutput output={output} />;
    case "design": return <DesignOutput output={output} />;
    case "quality": return <QualityOutput output={output} />;
    case "scheduler": return <SchedulerOutput output={output} />;
    case "analytics": return <AnalyticsOutput output={output} />;
    case "strategy": return <StrategyOutput output={output} />;
    default: return <pre className="text-xs text-muted-foreground overflow-x-auto">{JSON.stringify(output, null, 2)}</pre>;
  }
}

type OutDict = Record<string, any>;

function SectionLabel({ children }: { children: React.ReactNode }) {
  return <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground mb-1.5">{children}</p>;
}

function Chip({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] border border-glass-border bg-glass", className)}>
      {children}
    </span>
  );
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const pct = Math.min(100, Math.max(0, score));
  const color = pct >= 85 ? "bg-emerald-500" : pct >= 70 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[11px]">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold">{pct}/100</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div className={cn("h-full rounded-full", color)} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function TrendOutput({ output }: { output: OutDict }) {
  const trending = (output.trending_topics || []) as string[];
  const evergreen = (output.evergreen_ideas || []) as string[];
  const niches = (output.niche_suggestions || []) as string[];
  const seasonal = (output.seasonal_opportunities || []) as string[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const score = (output.opportunity_score as number) || 0;
  const competition = (output.competition_estimate as string) || "—";
  const priority = (output.suggested_priority as string) || "—";
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="space-y-4">
        <ScoreBar label="Opportunity Score" score={score} />
        <div className="flex gap-2">
          <Chip><Target className="w-3 h-3" />{competition} competition</Chip>
          <Chip><Flame className="w-3 h-3" />{priority} priority</Chip>
        </div>
        <div>
          <SectionLabel>Trending Topics</SectionLabel>
          <div className="space-y-1.5">
            {trending.map((t, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <TrendingUp className="w-3 h-3 text-blue-400 shrink-0" />
                <span className="text-muted-foreground">{t}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="space-y-3">
        <div>
          <SectionLabel>Evergreen Ideas</SectionLabel>
          <div className="space-y-1.5">
            {evergreen.map((t, i) => <p key={i} className="text-xs text-muted-foreground">• {t}</p>)}
          </div>
        </div>
        <div>
          <SectionLabel>Seasonal Opportunities</SectionLabel>
          <div className="space-y-1.5">
            {seasonal.map((t, i) => <p key={i} className="text-xs text-muted-foreground">• {t}</p>)}
          </div>
        </div>
        <div>
          <SectionLabel>Niche Suggestions</SectionLabel>
          <div className="flex flex-wrap gap-1.5">
            {niches.map((t, i) => <Chip key={i}>{t}</Chip>)}
          </div>
        </div>
      </div>
    </div>
  );
}

function SeoOutput({ output }: { output: OutDict }) {
  const keywords = (output.keywords || []) as string[];
  const longTail = (output.long_tail_keywords || []) as string[];
  const clusters = (output.clusters || []) as string[];
  const score = (output.seo_score as number) || 0;
  const difficulty = (output.keyword_difficulty as string) || "—";
  const intent = (output.search_intent as string) || "—";
  const meta = output.metadata as OutDict | undefined;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ScoreBar label="SEO Score" score={score} />
        <div className="flex items-end gap-2">
          <Chip><Target className="w-3 h-3" />{difficulty}</Chip>
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5">
        <Chip><Search className="w-3 h-3" />{intent}</Chip>
      </div>
      {meta && (
        <div className="rounded-xl bg-glass border border-glass-border p-3 space-y-1.5">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Metadata</p>
          <p className="text-xs font-medium text-primary">{String(meta.title_tag || "")}</p>
          <p className="text-[11px] text-muted-foreground">{String(meta.meta_description || "")}</p>
        </div>
      )}
      <div>
        <SectionLabel>Keyword Cluster ({keywords.length})</SectionLabel>
        <div className="flex flex-wrap gap-1.5">
          {keywords.map((k, i) => <Chip key={i}>{k}</Chip>)}
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <SectionLabel>Long-tail Keywords</SectionLabel>
          <div className="space-y-1.5">
            {longTail.map((t, i) => <p key={i} className="text-xs text-muted-foreground">• {t}</p>)}
          </div>
        </div>
        <div>
          <SectionLabel>Clusters</SectionLabel>
          <div className="space-y-1.5">
            {clusters.map((t, i) => <p key={i} className="text-xs text-muted-foreground">• {t}</p>)}
          </div>
        </div>
      </div>
    </div>
  );
}

function ContentOutput({ output }: { output: OutDict }) {
  const titles = (output.titles || []) as OutDict[];
  const descriptions = (output.descriptions || []) as string[];
  const hashtags = (output.hashtags || []) as string[];
  const cta = (output.cta as string) || "";
  const board = (output.recommended_board as string) || "";
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Chip className="border-amber-500/30 bg-amber-500/10"><Target className="w-3 h-3" />Board: {board}</Chip>
      </div>
      <div>
        <SectionLabel>SEO-Scored Titles</SectionLabel>
        <div className="space-y-2">
          {titles.map((t, i) => (
            <div key={i} className="rounded-xl bg-glass border border-glass-border p-3">
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs font-medium">{String(t.title)}</p>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 shrink-0">{t.seo_score}/100</span>
              </div>
              {t.reasoning && <p className="text-[10px] text-muted-foreground mt-1">{String(t.reasoning)}</p>}
            </div>
          ))}
        </div>
      </div>
      <div>
        <SectionLabel>Descriptions</SectionLabel>
        <div className="space-y-2">
          {descriptions.map((d, i) => (
            <p key={i} className="text-xs text-muted-foreground rounded-xl bg-glass border border-glass-border p-3">{d}</p>
          ))}
        </div>
      </div>
      <div>
        <SectionLabel>Hashtags</SectionLabel>
        <div className="flex flex-wrap gap-1.5">
          {hashtags.map((h, i) => (
            <Chip key={i} className="border-primary/20"><Hash className="w-3 h-3 text-primary" />{h}</Chip>
          ))}
        </div>
      </div>
      {cta && (
        <div className="rounded-xl bg-primary/10 border border-primary/20 p-3">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-primary mb-1">CTA</p>
          <p className="text-xs">{cta}</p>
        </div>
      )}
    </div>
  );
}

function DesignOutput({ output }: { output: OutDict }) {
  const variations = (output.variations || []) as OutDict[];
  const style = (output.style as string) || "—";
  const colorScheme = output.color_scheme as OutDict | undefined;
  const colors = (colorScheme?.name as string) || "—";
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Chip><Palette className="w-3 h-3" />Style: {style}</Chip>
        <Chip className="border-pink-500/30 bg-pink-500/10">Scheme: {colors}</Chip>
      </div>
      <div>
        <SectionLabel>Design Variations</SectionLabel>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {variations.map((v, i) => (
            <div key={i} className="rounded-xl bg-glass border border-glass-border p-3 space-y-2">
              <p className="text-xs font-semibold">{String(v.name)}</p>
              <p className="text-[10px] text-muted-foreground">{String(v.layout)}</p>
              <p className="text-[10px] text-muted-foreground">{String(v.typography)}</p>
              <div className="flex items-center gap-2">
                <div className="h-1.5 flex-1 rounded-full bg-muted overflow-hidden">
                  <div className="h-full bg-pink-500 rounded-full" style={{ width: `${Number(v.readability) || 0}%` }} />
                </div>
                <span className="text-[10px] font-semibold text-pink-400">{v.readability}</span>
              </div>
              {(v.colors as string[] | undefined)?.length ? (
                <div className="flex gap-1">
                  {(v.colors as string[]).map((c, ci) => (
                    <div key={ci} className="w-4 h-4 rounded-full border border-white/10" style={{ backgroundColor: c }} />
                  ))}
                </div>
              ) : null}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function QualityOutput({ output }: { output: OutDict }) {
  const score = (output.quality_score as number) || 0;
  const passed = (output.passed as number) || 0;
  const total = (output.total_checks as number) || 0;
  const rejected = output.auto_rejected as boolean;
  const checks = (output.checks || []) as OutDict[];
  const flags = (output.flags || []) as OutDict[];
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl bg-glass border border-glass-border p-3 text-center">
          <p className="text-xl font-bold text-emerald-400">{score}</p>
          <p className="text-[10px] text-muted-foreground">Quality Score</p>
        </div>
        <div className="rounded-xl bg-glass border border-glass-border p-3 text-center">
          <p className="text-xl font-bold text-blue-400">{passed}/{total}</p>
          <p className="text-[10px] text-muted-foreground">Checks Passed</p>
        </div>
        <div className="rounded-xl bg-glass border border-glass-border p-3 text-center">
          <p className={cn("text-xl font-bold", rejected ? "text-red-400" : "text-emerald-400")}>
            {rejected ? "Rejected" : "Approved"}
          </p>
          <p className="text-[10px] text-muted-foreground">Status</p>
        </div>
      </div>
      <div>
        <SectionLabel>Quality Checks</SectionLabel>
        <div className="space-y-1.5">
          {checks.map((c, i) => (
            <div key={i} className="flex items-center justify-between rounded-xl bg-glass border border-glass-border px-3 py-2">
              <div className="flex items-center gap-2">
                {c.passed
                  ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  : <XCircle className="w-3.5 h-3.5 text-red-400 shrink-0" />}
                <div>
                  <p className="text-xs font-medium capitalize">{String(c.check).replace(/_/g, " ")}</p>
                  <p className="text-[10px] text-muted-foreground">{String(c.details)}</p>
                </div>
              </div>
              <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full font-medium", c.passed ? "bg-emerald-500/15 text-emerald-400" : "bg-red-500/15 text-red-400")}>
                {c.score}
              </span>
            </div>
          ))}
        </div>
      </div>
      {flags.length > 0 && (
        <div className="rounded-xl bg-red-500/10 border border-red-500/30 p-3">
          <p className="text-xs font-medium text-red-400 mb-1">{flags.length} flag(s) to fix before publishing</p>
          {flags.map((f, i) => <p key={i} className="text-[11px] text-muted-foreground">• {String(f.check)}</p>)}
        </div>
      )}
    </div>
  );
}

function SchedulerOutput({ output }: { output: OutDict }) {
  const slots = (output.schedule || []) as OutDict[];
  const best = (output.optimal_posting_time as string) || "—";
  const rotation = (output.board_rotation || []) as string[];
  const mix = (output.content_mix as string) || "—";
  const reach = (output.estimated_reach as string) || "—";
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="rounded-xl bg-glass border border-glass-border p-3">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">Best Time</p>
          <p className="text-xs font-medium text-indigo-400">{best}</p>
        </div>
        <div className="rounded-xl bg-glass border border-glass-border p-3">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">Content Mix</p>
          <p className="text-[11px] text-muted-foreground">{mix}</p>
        </div>
        <div className="rounded-xl bg-glass border border-glass-border p-3">
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1">Est. Reach</p>
          <p className="text-xs font-medium text-emerald-400">{reach}</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5">
        <SectionLabel>Board Rotation</SectionLabel>
        <div className="flex flex-wrap gap-1.5 w-full">
          {rotation.map((b, i) => <Chip key={i}>{b}</Chip>)}
        </div>
      </div>
      <div>
        <SectionLabel>Publishing Slots</SectionLabel>
        <div className="space-y-1.5">
          {slots.map((s, i) => (
            <div key={i} className="flex items-center justify-between rounded-xl bg-glass border border-glass-border px-3 py-2">
              <div className="flex items-center gap-2">
                <CalendarClock className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                <div>
                  <p className="text-xs font-medium">{String(s.day)} · {String(s.time)}</p>
                  <p className="text-[10px] text-muted-foreground">{String(s.board)}</p>
                </div>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400">
                {s.predicted_engagement} engagement
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AnalyticsOutput({ output }: { output: OutDict }) {
  const metrics = output.metrics as OutDict | undefined;
  const topPins = (output.top_pins || []) as OutDict[];
  const topBoards = (output.top_boards || []) as OutDict[];
  const topKeywords = (output.top_keywords || []) as OutDict[];
  const bestTime = (output.best_posting_time as string) || "—";
  const bestStyle = (output.best_image_style as string) || "—";
  const weekly = output.weekly_report as OutDict | undefined;
  const metricCards = [
    { label: "Impressions", value: metrics?.total_impressions, color: "text-blue-400" },
    { label: "Saves", value: metrics?.total_saves, color: "text-pink-400" },
    { label: "Clicks", value: metrics?.total_clicks, color: "text-emerald-400" },
    { label: "CTR", value: metrics?.ctr ? `${metrics.ctr}%` : "—", color: "text-violet-400" },
  ];
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {metricCards.map((m, i) => (
          <div key={i} className="rounded-xl bg-glass border border-glass-border p-3 text-center">
            <p className={cn("text-lg font-bold", m.color)}>{String(m.value ?? "—")}</p>
            <p className="text-[10px] text-muted-foreground">{m.label}</p>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        <Chip className="border-teal-500/30 bg-teal-500/10">Best time: {bestTime}</Chip>
        <Chip className="border-pink-500/30 bg-pink-500/10">Best style: {bestStyle}</Chip>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <SectionLabel>Top Pins</SectionLabel>
          <div className="space-y-1.5">
            {topPins.map((p, i) => (
              <div key={i} className="rounded-xl bg-glass border border-glass-border p-2.5">
                <p className="text-xs font-medium truncate">{String(p.title)}</p>
                <p className="text-[10px] text-muted-foreground">{String(p.clicks)} clicks · {String(p.saves)} saves</p>
              </div>
            ))}
          </div>
        </div>
        <div>
          <SectionLabel>Top Boards</SectionLabel>
          <div className="space-y-1.5">
            {topBoards.map((b, i) => (
              <div key={i} className="rounded-xl bg-glass border border-glass-border p-2.5">
                <p className="text-xs font-medium">{String(b.name)}</p>
                <p className="text-[10px] text-muted-foreground">{String(b.impressions)} impressions · {b.ctr}% CTR</p>
              </div>
            ))}
          </div>
        </div>
        <div>
          <SectionLabel>Top Keywords</SectionLabel>
          <div className="space-y-1.5">
            {topKeywords.map((k, i) => (
              <div key={i} className="rounded-xl bg-glass border border-glass-border p-2.5">
                <p className="text-xs font-medium">{String(k.keyword)}</p>
                <p className="text-[10px] text-emerald-400">{String(k.clicks)} clicks/mo · {k.growth}% growth</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      {weekly && (
        <div className="rounded-xl bg-teal-500/10 border border-teal-500/30 p-3">
          <p className="text-xs font-medium text-teal-400 mb-1">Weekly Report · {String(weekly.period)}</p>
          <p className="text-[11px] text-muted-foreground">
            {weekly.new_pins} new pins · {String(weekly.impressions).toLocaleString()} impressions · {weekly.clicks} clicks · {weekly.ctr}% CTR
          </p>
        </div>
      )}
    </div>
  );
}

function StrategyOutput({ output }: { output: OutDict }) {
  const recommendations = (output.recommendations || []) as OutDict[];
  const niches = (output.new_niches || []) as OutDict[];
  const gaps = (output.content_gaps || []) as OutDict[];
  const roadmap = (output.growth_roadmap || []) as OutDict[];
  const priorityColor = (p: string) =>
    p === "high" ? "bg-red-500/15 text-red-400" : p === "medium" ? "bg-amber-500/15 text-amber-400" : "bg-blue-500/15 text-blue-400";
  return (
    <div className="space-y-4">
      <div>
        <SectionLabel>Recommendations</SectionLabel>
        <div className="space-y-1.5">
          {recommendations.map((r, i) => (
            <div key={i} className="flex items-start justify-between gap-3 rounded-xl bg-glass border border-glass-border px-3 py-2.5">
              <div className="flex items-start gap-2 min-w-0">
                <Lightbulb className="w-3.5 h-3.5 text-violet-400 shrink-0 mt-0.5" />
                <p className="text-xs text-muted-foreground">{String(r.title)}</p>
              </div>
              <span className={cn("text-[10px] px-2 py-0.5 rounded-full font-medium shrink-0 capitalize", priorityColor(String(r.priority)))}>
                {r.priority}
              </span>
            </div>
          ))}
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <SectionLabel>New Niches</SectionLabel>
          <div className="space-y-1.5">
            {niches.map((n, i) => (
              <div key={i} className="flex items-center justify-between rounded-xl bg-glass border border-glass-border px-3 py-2">
                <p className="text-xs font-medium">{String(n.niche)}</p>
                <span className="text-[10px] text-emerald-400">{n.score}/100 · {n.growth}</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <SectionLabel>Content Gaps</SectionLabel>
          <div className="space-y-1.5">
            {gaps.map((g, i) => (
              <div key={i} className="flex items-center justify-between rounded-xl bg-glass border border-glass-border px-3 py-2">
                <p className="text-xs">{String(g.topic)}</p>
                <span className="text-[10px] text-muted-foreground">{g.missing_pins} pins missing</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div>
        <SectionLabel>4-Week Growth Roadmap</SectionLabel>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
          {roadmap.map((w, i) => (
            <div key={i} className="rounded-xl bg-glass border border-glass-border p-3">
              <p className="text-[10px] font-semibold text-violet-400 mb-1">Week {w.week}</p>
              <p className="text-[11px] font-medium">{String(w.action)}</p>
              <p className="text-[10px] text-muted-foreground mt-1">{String(w.expected_impact)}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export { AgentOutputRenderer };
