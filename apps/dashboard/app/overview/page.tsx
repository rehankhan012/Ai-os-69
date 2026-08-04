"use client";

import { motion } from "framer-motion";
import {
  TrendingUp, ArrowUpRight, ArrowDownRight,
  Image, Clock, CheckCircle, Eye, MousePointerClick,
  Heart, Star, Activity, Sparkles, Cpu, Brain,
  BarChart3, LineChart
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const stats = [
  { label: "Pins Created", value: "156", change: "+12%", icon: Image, trend: "up", color: "from-blue-500/20 to-purple-500/20", iconColor: "text-blue-400" },
  { label: "Queued", value: "18", change: "-3%", icon: Clock, trend: "down", color: "from-amber-500/20 to-orange-500/20", iconColor: "text-amber-400" },
  { label: "Published", value: "138", change: "+8%", icon: CheckCircle, trend: "up", color: "from-emerald-500/20 to-teal-500/20", iconColor: "text-emerald-400" },
  { label: "Impressions", value: "89.2K", change: "+15%", icon: Eye, trend: "up", color: "from-violet-500/20 to-purple-500/20", iconColor: "text-violet-400" },
  { label: "Saves", value: "3.4K", change: "+5.7%", icon: Heart, trend: "up", color: "from-red-500/20 to-pink-500/20", iconColor: "text-red-400" },
  { label: "CTR", value: "4.8%", change: "+0.6%", icon: MousePointerClick, trend: "up", color: "from-primary/20 to-primary/5", iconColor: "text-primary" },
];

const recentActivity = [
  { action: "Workflow completed", detail: "5 pins generated for 'digital marketing'", time: "2 min ago", agent: "Master" },
  { action: "Trend scan finished", detail: "3 new opportunities in SEO niche", time: "15 min ago", agent: "Trend" },
  { action: "Content generated", detail: "Titles, descriptions, and hashtags ready", time: "1 hour ago", agent: "Content" },
  { action: "Quality review passed", detail: "All checks passed — score: 92/100", time: "3 hours ago", agent: "Quality" },
  { action: "Strategy update", detail: "New recommendations for Q2 growth", time: "5 hours ago", agent: "Strategy" },
];

const agentQuickStatus = [
  { name: "Master", status: "running", color: "bg-purple-500", desc: "Workflow in progress" },
  { name: "Trend", status: "idle", color: "bg-blue-500", desc: "Ready for scan" },
  { name: "SEO", status: "idle", color: "bg-emerald-500", desc: "Awaiting keyword" },
  { name: "Content", status: "idle", color: "bg-amber-500", desc: "Ready to generate" },
  { name: "Design", status: "idle", color: "bg-pink-500", desc: "Idle" },
  { name: "Quality", status: "completed", color: "bg-red-500", desc: "Last review passed" },
  { name: "Scheduler", status: "idle", color: "bg-indigo-500", desc: "No pending items" },
  { name: "Analytics", status: "completed", color: "bg-teal-500", desc: "Report ready" },
  { name: "Strategy", status: "idle", color: "bg-violet-500", desc: "Generating insights" },
];

export default function OverviewPage() {
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
            <h1 className="section-title">Pinterest AI Studio</h1>
            <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-medium">v2.0</span>
          </div>
          <p className="section-subtitle">Your AI marketing team — 24/7 content production</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-glass border border-glass-border">
            <Activity className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-medium text-emerald-400">All Systems Active</span>
          </div>
          <Button className="gap-2">
            <Sparkles className="w-4 h-4" />
            New Workflow
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="stats-card relative overflow-hidden group">
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-40 group-hover:opacity-60 transition-opacity duration-300`} />
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-2">
                <div className={`p-1.5 rounded-lg bg-background/50 backdrop-blur-sm ${stat.iconColor}`}>
                  <stat.icon className="w-4 h-4" />
                </div>
                <div className={`flex items-center gap-0.5 text-[10px] font-medium ${stat.trend === "up" ? "text-emerald-400" : "text-red-400"}`}>
                  {stat.trend === "up" ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                  {stat.change}
                </div>
              </div>
              <p className="text-xl font-bold">{stat.value}</p>
              <p className="text-[11px] text-muted-foreground">{stat.label}</p>
            </div>
          </div>
        ))}
      </motion.div>

      {/* Main Grid: Agent Status + Growth + Activity */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Status Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-primary" />
                <CardTitle>AI Agent Status</CardTitle>
              </div>
              <span className="text-[10px] text-muted-foreground">9 agents</span>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {agentQuickStatus.map((agent) => (
              <div key={agent.name} className="flex items-center justify-between p-2.5 rounded-xl hover:bg-glass-hover transition-colors">
                <div className="flex items-center gap-3">
                  <div className={cn("w-2 h-2 rounded-full", agent.color, agent.status === "running" && "animate-pulse")} />
                  <div>
                    <p className="text-sm font-medium">{agent.name}</p>
                    <p className="text-[10px] text-muted-foreground">{agent.desc}</p>
                  </div>
                </div>
                <span className={cn(
                  "text-[10px] px-2 py-0.5 rounded-full font-medium",
                  agent.status === "running" ? "bg-blue-500/10 text-blue-400" :
                  agent.status === "completed" ? "bg-emerald-500/10 text-emerald-400" :
                  "bg-muted text-muted-foreground"
                )}>
                  {agent.status}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Growth Chart Area */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Growth</CardTitle>
              <span className="text-[10px] text-muted-foreground">Last 30 days</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[280px] flex items-end justify-between gap-1.5">
              {[30, 45, 38, 52, 48, 65, 58, 72, 68, 85, 78, 92, 88, 105, 98, 110, 95, 115, 108, 120, 112, 130, 125, 140, 135, 145, 138, 150, 142, 155].map((height, i) => (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  animate={{ height: `${height / 1.55}%` }}
                  transition={{ delay: i * 0.02, duration: 0.4, ease: "easeOut" }}
                  className="flex-1 bg-gradient-to-t from-primary/40 to-primary/20 rounded-t hover:from-primary/60 hover:to-primary/40 transition-colors cursor-pointer relative group"
                >
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-card border border-glass-border rounded-lg px-2 py-1 text-[10px] whitespace-nowrap z-10">
                    {height} clicks
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Activity</CardTitle>
              <Activity className="w-4 h-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent className="space-y-1">
            {recentActivity.map((activity, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="p-2.5 rounded-xl hover:bg-glass-hover transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary font-medium">{activity.agent}</span>
                  <span className="text-[10px] text-muted-foreground">{activity.time}</span>
                </div>
                <p className="text-sm mt-1">{activity.action}</p>
                <p className="text-[10px] text-muted-foreground">{activity.detail}</p>
              </motion.div>
            ))}
          </CardContent>
        </Card>
      </motion.div>

      {/* AI Insights Panel */}
      <motion.div variants={itemVariants}>
        <Card className="gradient-card border-primary/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              <CardTitle>AI Strategy Insights</CardTitle>
              <CardDescription>Powered by the Strategy Agent</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { icon: TrendingUp, title: "Expand into Video", desc: "Pinterest video pins get 4x more engagement", priority: "high", color: "text-blue-400" },
                { icon: Star, title: "Best Posting Time", desc: "2:00 PM EST (Tue-Thu) — 2.4x higher CTR", priority: "high", color: "text-amber-400" },
                { icon: BarChart3, title: "Top Performing Style", desc: "Infographic style — 2.3x higher CTR than average", priority: "medium", color: "text-emerald-400" },
              ].map((insight, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 rounded-xl glass border border-glass-border"
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg bg-background/50 ${insight.color}`}>
                      <insight.icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{insight.title}</p>
                      <p className="text-[10px] text-muted-foreground mt-1">{insight.desc}</p>
                      <span className="inline-block mt-2 text-[10px] px-1.5 py-0.5 rounded-full bg-primary/10 text-primary capitalize">{insight.priority} priority</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}