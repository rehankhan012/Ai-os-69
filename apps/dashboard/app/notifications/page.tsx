"use client";

import { motion } from "framer-motion";
import { Bell, CheckCircle, Clock, AlertTriangle, Sparkles, FileText, Palette, Send, Eye, CheckCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const notifications = [
  { title: "AI Generation Complete", message: "5 pins generated for 'digital marketing'", type: "ai_complete", time: "2 min ago", read: false, icon: Sparkles, color: "text-purple-400", bg: "bg-purple-500/10" },
  { title: "Draft Requires Review", message: "Article '10 AI Tools for Students' is ready for review", type: "draft_review", time: "15 min ago", read: false, icon: Eye, color: "text-amber-400", bg: "bg-amber-500/10" },
  { title: "Publishing Succeeded", message: "Article 'SEO Best Practices Guide' published successfully", type: "publish_success", time: "1 hour ago", read: false, icon: Send, color: "text-emerald-400", bg: "bg-emerald-500/10" },
  { title: "Graphic Rendering Complete", message: "3 variations generated for 'Content Strategy 2026'", type: "ai_complete", time: "3 hours ago", read: true, icon: Palette, color: "text-pink-400", bg: "bg-pink-500/10" },
  { title: "Analytics Alert", message: "Traffic spike detected — 45% increase from Pinterest", type: "analytics_alert", time: "5 hours ago", read: true, icon: AlertTriangle, color: "text-red-400", bg: "bg-red-500/10" },
  { title: "Content Published", message: "Pinterest pin '10 Tips for 2026' is now live", type: "publish_success", time: "1 day ago", read: true, icon: FileText, color: "text-blue-400", bg: "bg-blue-500/10" },
];

export default function NotificationsPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Bell className="w-6 h-6 text-primary" />
            <h1 className="section-title">Notifications</h1>
          </div>
          <p className="section-subtitle">Stay updated on AI generation, publishing, and analytics</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="secondary" className="gap-1"><Bell className="w-3 h-3" /> 3 unread</Badge>
          <Button variant="outline" size="sm" className="gap-1"><CheckCheck className="w-3 h-3" /> Mark All Read</Button>
        </div>
      </div>

      <div className="space-y-2">
        {notifications.map((n, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className={cn(
              "glass-card-hover p-4 flex items-start gap-4",
              !n.read && "border-l-primary"
            )}
          >
            <div className={`p-2 rounded-lg ${n.bg} ${n.color}`}>
              <n.icon className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">{n.title}</h3>
                <div className="flex items-center gap-2">
                  {!n.read && <span className="w-2 h-2 rounded-full bg-primary" />}
                  <span className="text-[10px] text-muted-foreground">{n.time}</span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-1">{n.message}</p>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant="outline" className="text-[9px] capitalize">{n.type.replace(/_/g, " ")}</Badge>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}