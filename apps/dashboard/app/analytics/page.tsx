"use client";

import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Eye, Heart, MousePointerClick, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const stats = [
  { label: "Total Pins", value: "156", icon: BarChart3, change: "+12", color: "text-blue-400" },
  { label: "Total Clicks", value: "12,450", icon: MousePointerClick, change: "+8.3%", color: "text-emerald-400" },
  { label: "Impressions", value: "89,230", icon: Eye, change: "+15.2%", color: "text-purple-400" },
  { label: "Saves", value: "3,421", icon: Heart, change: "+5.7%", color: "text-red-400" },
  { label: "Outbound Clicks", value: "2,876", icon: ExternalLink, change: "+11.4%", color: "text-amber-400" },
  { label: "CTR", value: "4.8%", icon: TrendingUp, change: "+0.6%", color: "text-primary" },
];

export default function AnalyticsPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-teal-400" />
            <h1 className="section-title">Analytics</h1>
          </div>
          <p className="section-subtitle">Powered by the Analytics Agent — Last 30 days</p>
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center justify-between">
                <stat.icon className={`w-4 h-4 ${stat.color}`} />
                <span className="text-xs text-emerald-400">{stat.change}</span>
              </div>
              <p className="text-2xl font-bold">{stat.value}</p>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle>Traffic Overview</CardTitle></CardHeader>
          <CardContent className="h-[300px] flex items-center justify-center text-muted-foreground">
            <BarChart3 className="w-8 h-8 mr-2" />Chart coming soon
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Top Boards</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {[
              { board: "SEO Strategies", impressions: 12000, clicks: 450 },
              { board: "Content Marketing", impressions: 8900, clicks: 320 },
              { board: "Social Media Tips", impressions: 7600, clicks: 280 },
              { board: "Design Inspiration", impressions: 5400, clicks: 210 },
            ].map((b) => (
              <div key={b.board} className="flex items-center justify-between p-3 rounded-xl bg-glass">
                <div>
                  <p className="text-sm font-medium">{b.board}</p>
                  <p className="text-xs text-muted-foreground">{b.impressions.toLocaleString()} impressions</p>
                </div>
                <span className="text-xs px-2 py-1 rounded-full bg-glass border border-glass-border">{b.clicks} clicks</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}