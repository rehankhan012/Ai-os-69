"use client";

import { motion } from "framer-motion";
import { DollarSign, TrendingUp, ArrowUpRight, ArrowDownRight, ShoppingCart, MousePointerClick, Target, BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const revenueStats = [
  { label: "Total Revenue", value: "$12,450", change: "+18.5%", icon: DollarSign, trend: "up", color: "text-emerald-400" },
  { label: "Affiliate Earnings", value: "$8,230", change: "+12.3%", icon: ShoppingCart, trend: "up", color: "text-blue-400" },
  { label: "Affiliate Clicks", value: "2,876", change: "+8.7%", icon: MousePointerClick, trend: "up", color: "text-purple-400" },
  { label: "Conversion Rate", value: "3.2%", change: "+0.4%", icon: Target, trend: "up", color: "text-amber-400" },
  { label: "Active Links", value: "24", change: "+4", icon: BarChart3, trend: "up", color: "text-pink-400" },
  { label: "Monthly Growth", value: "18.5%", change: "+2.1%", icon: TrendingUp, trend: "up", color: "text-primary" },
];

const topArticles = [
  { title: "10 AI Tools Every Student Should Know", revenue: "$1,240", clicks: 890, conversion: "4.2%" },
  { title: "Ultimate Guide to Pinterest Marketing", revenue: "$980", clicks: 670, conversion: "3.8%" },
  { title: "Content Strategy for 2026", revenue: "$756", clicks: 540, conversion: "3.1%" },
  { title: "SEO Best Practices Guide", revenue: "$543", clicks: 410, conversion: "2.9%" },
  { title: "Social Media Growth Hacks", revenue: "$421", clicks: 320, conversion: "2.5%" },
];

export default function RevenuePage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <DollarSign className="w-6 h-6 text-emerald-400" />
            <h1 className="section-title">Revenue Dashboard</h1>
          </div>
          <p className="section-subtitle">Track earnings, affiliate performance, and growth trends</p>
        </div>
        <Badge variant="outline" className="gap-1"><BarChart3 className="w-3 h-3" /> Last 30 days</Badge>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {revenueStats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center justify-between">
                <stat.icon className={`w-4 h-4 ${stat.color}`} />
                <div className={`flex items-center gap-0.5 text-[10px] font-medium ${stat.trend === "up" ? "text-emerald-400" : "text-red-400"}`}>
                  {stat.trend === "up" ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                  {stat.change}
                </div>
              </div>
              <p className="text-xl font-bold">{stat.value}</p>
              <p className="text-[10px] text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trends</CardTitle>
            <CardDescription>Monthly earnings over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[200px] flex items-end justify-between gap-2">
              {[1200, 1800, 1500, 2200, 1900, 2600, 2300, 2800, 2500, 3100, 2900, 3400].map((height, i) => (
                <motion.div
                  key={i}
                  initial={{ height: 0 }}
                  animate={{ height: `${height / 34}%` }}
                  transition={{ delay: i * 0.03, duration: 0.4 }}
                  className="flex-1 bg-gradient-to-t from-emerald-500/40 to-emerald-500/20 rounded-t hover:from-emerald-500/60 transition-colors cursor-pointer relative group"
                >
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-card border border-glass-border rounded px-2 py-1 text-[10px] whitespace-nowrap">${height}</div>
                </motion.div>
              ))}
            </div>
            <div className="flex justify-between mt-2 text-[10px] text-muted-foreground">
              <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span>
              <span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Converting Articles</CardTitle>
            <CardDescription>Revenue by content</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {topArticles.map((article, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-glass hover:bg-glass-hover transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-lg bg-primary/10 text-primary flex items-center justify-center text-[10px] font-bold">#{i + 1}</div>
                  <div>
                    <p className="text-sm font-medium truncate max-w-[200px]">{article.title}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] text-muted-foreground">{article.clicks} clicks</span>
                      <span className="text-[10px] text-emerald-400">{article.conversion} conv.</span>
                    </div>
                  </div>
                </div>
                <span className="text-sm font-bold text-emerald-400">{article.revenue}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}