"use client";

import { motion } from "framer-motion";
import { ListOrdered, Calendar, Clock, CheckCircle, XCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const queueItems = [
  { title: "10 Pinterest Tips for 2026", status: "queued", scheduled: "Today, 2:00 PM", id: 1 },
  { title: "Ultimate SEO Guide", status: "publishing", scheduled: "Today, 4:00 PM", id: 2 },
  { title: "Content Strategy Secrets", status: "queued", scheduled: "Tomorrow, 10:00 AM", id: 3 },
  { title: "Best Time to Post on Pinterest", status: "queued", scheduled: "Tomorrow, 2:00 PM", id: 4 },
  { title: "Pinterest Algorithm Changes 2026", status: "draft", scheduled: "Not scheduled", id: 5 },
];

export default function QueuePage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <ListOrdered className="w-6 h-6" />
            <h1 className="section-title">Publishing Queue</h1>
          </div>
          <p className="section-subtitle">Powered by the Scheduler Agent</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2"><Calendar className="w-4 h-4" />Calendar View</Button>
          <Button variant="outline">Export Queue</Button>
        </div>
      </div>
      <div className="space-y-3">
        {queueItems.map((item) => (
          <div key={item.id} className="glass-card-hover p-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-2 rounded-lg ${item.status === "queued" ? "bg-amber-500/10 text-amber-400" : item.status === "publishing" ? "bg-blue-500/10 text-blue-400" : "bg-muted text-muted-foreground"}`}>
                {item.status === "queued" ? <Clock className="w-5 h-5" /> : item.status === "publishing" ? <ListOrdered className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
              </div>
              <div>
                <p className="text-sm font-medium">{item.title}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{item.scheduled}</p>
              </div>
            </div>
            <span className={`text-[10px] px-2 py-1 rounded-full font-medium ${item.status === "queued" ? "bg-amber-500/10 text-amber-400" : item.status === "publishing" ? "bg-blue-500/10 text-blue-400" : "bg-muted text-muted-foreground"}`}>{item.status}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}