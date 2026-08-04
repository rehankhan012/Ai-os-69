"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Activity, CheckCircle, ThumbsUp, ListOrdered, Clock, Settings2,
  Zap, Sparkles, ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import WorkflowRunner from "@/components/agents/workflow-runner";
import { AGENT_ORDER } from "@/lib/agents";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const workflowSteps = [
  { name: "Trend", color: "text-blue-400", bg: "bg-blue-500/10" },
  { name: "SEO", color: "text-emerald-400", bg: "bg-emerald-500/10" },
  { name: "Content", color: "text-amber-400", bg: "bg-amber-500/10" },
  { name: "Design", color: "text-pink-400", bg: "bg-pink-500/10" },
  { name: "Quality", color: "text-red-400", bg: "bg-red-500/10" },
  { name: "Schedule", color: "text-indigo-400", bg: "bg-indigo-500/10" },
  { name: "Analytics", color: "text-teal-400", bg: "bg-teal-500/10" },
  { name: "Strategy", color: "text-violet-400", bg: "bg-violet-500/10" },
];

export default function AICommandCenterPage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="page-container space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Cpu className="w-6 h-6 text-primary" />
            <h1 className="section-title">AI Command Center</h1>
          </div>
          <p className="section-subtitle">Orchestrate your AI marketing team — Master Agent + 8 specialists working together</p>
        </div>
        <Button variant="outline" className="gap-2">
          <Settings2 className="w-4 h-4" />
          Agent Settings
        </Button>
      </motion.div>

      {/* Real Workflow Runner */}
      <motion.div variants={itemVariants}>
        <WorkflowRunner
          agents={AGENT_ORDER}
          placeholder="Enter a topic or keyword to launch the full AI workflow..."
          buttonLabel="Launch Workflow"
          runningLabel="Running..."
          subtitle="Trend → SEO → Content → Design → Quality → Schedule → Analytics → Strategy — every agent runs against the live API and returns real, structured output."
        />
      </motion.div>

      {/* Operations Overview */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Running AI Tasks */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2"><Activity className="w-4 h-4 text-blue-400" /> Running Tasks</CardTitle>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400">live</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="p-3 rounded-xl bg-glass border border-glass-border">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium">Full workflow · {AGENT_ORDER.length} agents</span>
                <span className="text-[10px] text-blue-400 animate-pulse">ready</span>
              </div>
              <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                <div className="h-full w-full bg-gradient-to-r from-blue-500 to-purple-500" />
              </div>
              <span className="text-[10px] text-muted-foreground mt-1 inline-block">
                Launch a workflow above — the live agent grid updates in real time
              </span>
            </div>
            <div className="p-3 rounded-xl bg-muted/30 border border-glass-border">
              <p className="text-[10px] text-muted-foreground">Enter a topic above to see every agent execute with per-agent timing.</p>
            </div>
          </CardContent>
        </Card>

        {/* Completed Tasks */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-400" /> Agent Proof</CardTitle>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400">{AGENT_ORDER.length} agents</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {AGENT_ORDER.map((name) => (
              <div key={name} className="flex items-center justify-between p-2.5 rounded-xl hover:bg-glass-hover transition-colors">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                  <p className="text-xs font-medium capitalize">{name}</p>
                </div>
                <span className="text-[10px] text-muted-foreground">runs on launch</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Pending Approvals + Queue Status */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2"><ThumbsUp className="w-4 h-4 text-amber-400" /> Publishing Queue</CardTitle>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400">approval-based</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="p-3 rounded-xl bg-glass border border-glass-border">
              <p className="text-xs font-medium">Review → Approve → Publish</p>
              <p className="text-[10px] text-muted-foreground mt-1">
                No content publishes without your explicit approval. Generated content lands in the publishing queue as a draft.
              </p>
            </div>
            <div className="pt-2 border-t border-glass-border">
              <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                <span>Queue status</span>
                <span className="flex items-center gap-1"><ListOrdered className="w-3 h-3" /> See Publishing Queue page</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Workflow Pipeline Visualization */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Workflow Pipeline</CardTitle>
            <CardDescription>Trend Discovery → Keyword Research → Content Generation → Design → Quality → Queue → Analytics → Strategy</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap items-center gap-2">
              {workflowSteps.map((step, i) => (
                <div key={step.name} className="flex items-center gap-2">
                  <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${step.bg} border border-glass-border`}>
                    <Sparkles className={`w-4 h-4 ${step.color}`} />
                    <span className="text-sm font-medium">{step.name}</span>
                  </div>
                  {i < workflowSteps.length - 1 && <ArrowRight className="w-4 h-4 text-muted-foreground" />}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
