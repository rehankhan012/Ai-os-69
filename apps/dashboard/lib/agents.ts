/**
 * Agent workflow API client — calls the public /agents/demo-workflow endpoint.
 *
 * The backend runs each agent (pure computation, no DB/auth required) and
 * returns the full structured output of every agent for rendering proof.
 */

import api from "./api";

/** Raw structured output of a single agent run. */
export interface AgentOutput {
  name: string;
  display: string;
  desc: string;
  success: boolean;
  processing_time_ms: number;
  /** Parsed JSON from the API — rendered by AgentOutputRenderer. */
  output: Record<string, any>;
  suggestions: string[];
}

/** Response shape of POST /agents/demo-workflow. */
export interface DemoWorkflowResponse {
  success: boolean;
  workflow_id: string;
  keyword: string;
  niche: string;
  agents: AgentOutput[];
  master: {
    seo_score: number;
    quality_score: number;
    total_processing_time_ms: number;
    agents_run: number;
  };
}

export interface WorkflowOptions {
  keyword: string;
  niche?: string;
  audience?: string;
  tone?: string;
  goal?: string;
  /** Subset of agents to run, e.g. ["seo", "content"]. */
  agents?: string[];
}

/** Canonical agent metadata for the dashboard UI. */
export const AGENT_META: Record<
  string,
  { display: string; icon: string; gradient: string; ring: string }
> = {
  trend: {
    display: "Trend Agent",
    icon: "trending-up",
    gradient: "from-blue-500/15 to-cyan-500/5",
    ring: "ring-blue-500/30",
  },
  seo: {
    display: "SEO Agent",
    icon: "search",
    gradient: "from-emerald-500/15 to-teal-500/5",
    ring: "ring-emerald-500/30",
  },
  content: {
    display: "Content Agent",
    icon: "file-text",
    gradient: "from-amber-500/15 to-orange-500/5",
    ring: "ring-amber-500/30",
  },
  design: {
    display: "Design Agent",
    icon: "palette",
    gradient: "from-pink-500/15 to-rose-500/5",
    ring: "ring-pink-500/30",
  },
  quality: {
    display: "Quality Agent",
    icon: "check-circle",
    gradient: "from-red-500/15 to-rose-500/5",
    ring: "ring-red-500/30",
  },
  scheduler: {
    display: "Scheduler Agent",
    icon: "clock",
    gradient: "from-indigo-500/15 to-blue-500/5",
    ring: "ring-indigo-500/30",
  },
  analytics: {
    display: "Analytics Agent",
    icon: "bar-chart-3",
    gradient: "from-teal-500/15 to-emerald-500/5",
    ring: "ring-teal-500/30",
  },
  strategy: {
    display: "Strategy Agent",
    icon: "lightbulb",
    gradient: "from-violet-500/15 to-purple-500/5",
    ring: "ring-violet-500/30",
  },
  master: {
    display: "Master Agent",
    icon: "cpu",
    gradient: "from-purple-500/15 to-fuchsia-500/5",
    ring: "ring-purple-500/30",
  },
};

export const AGENT_ORDER = [
  "trend",
  "seo",
  "content",
  "design",
  "quality",
  "scheduler",
  "analytics",
  "strategy",
];

/** Run the demo workflow against the backend. Throws ApiError on failure. */
export async function runDemoWorkflow(
  options: WorkflowOptions,
): Promise<DemoWorkflowResponse> {
  return api.post<DemoWorkflowResponse>("/agents/demo-workflow", {
    keyword: options.keyword,
    niche: options.niche || "general",
    audience: options.audience || "",
    tone: options.tone || "professional",
    goal: options.goal || "engagement",
    agents: options.agents || AGENT_ORDER,
  });
}
