"use client";

import { motion } from "framer-motion";
import { Lightbulb, TrendingUp, Star, Zap, Target, Rocket } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const recommendations = [
  { title: "Expand into video content", desc: "Pinterest video pins get 4x more engagement than static pins", type: "content_format", priority: "high", icon: TrendingUp, color: "text-blue-400" },
  { title: "Create a pillar page", desc: "Build SEO authority with a comprehensive guide in your niche", type: "seo", priority: "high", icon: Target, color: "text-emerald-400" },
  { title: "Publish 3x/week consistently", desc: "Accounts posting 3+ times see 2x faster follower growth", type: "frequency", priority: "medium", icon: Zap, color: "text-amber-400" },
  { title: "Add story pins to your mix", desc: "Story pins get 35% more saves than standard pins", type: "format", priority: "medium", icon: Star, color: "text-pink-400" },
  { title: "Repurpose top content", desc: "Turn your best-performing content into infographics", type: "repurposing", priority: "low", icon: Rocket, color: "text-violet-400" },
];

export default function InsightsPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Lightbulb className="w-6 h-6 text-violet-400" />
            <h1 className="section-title">AI Insights</h1>
          </div>
          <p className="section-subtitle">Powered by the Strategy Agent — continuous growth recommendations</p>
        </div>
        <Button className="gap-2"><Rocket className="w-4 h-4" />Generate New Insights</Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((rec, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="agent-card border-l-emerald-500"
          >
            <div className="flex items-start gap-4">
              <div className={`p-2 rounded-lg bg-background/50 ${rec.color}`}>
                <rec.icon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm">{rec.title}</h3>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium capitalize ${
                    rec.priority === "high" ? "bg-red-500/10 text-red-400" :
                    rec.priority === "medium" ? "bg-amber-500/10 text-amber-400" :
                    "bg-muted text-muted-foreground"
                  }`}>{rec.priority}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{rec.desc}</p>
                <span className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full bg-glass border border-glass-border text-muted-foreground capitalize">{rec.type}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}