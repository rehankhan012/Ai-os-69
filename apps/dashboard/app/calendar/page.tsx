"use client";

import { motion } from "framer-motion";
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function CalendarPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <CalendarIcon className="w-6 h-6" />
            <h1 className="section-title">Content Calendar</h1>
          </div>
          <p className="section-subtitle">Drag-and-drop scheduling — powered by the Scheduler Agent</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon"><ChevronLeft className="w-4 h-4" /></Button>
          <span className="text-sm font-medium px-3">March 2026</span>
          <Button variant="outline" size="icon"><ChevronRight className="w-4 h-4" /></Button>
        </div>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Monthly View</CardTitle>
          <CardDescription>Drag and drop to schedule content</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-1">
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
              <div key={d} className="text-center text-xs text-muted-foreground font-medium py-2">{d}</div>
            ))}
            {Array.from({ length: 31 }, (_, i) => (
              <div key={i} className="min-h-[80px] p-1.5 rounded-lg border border-glass-border hover:bg-glass-hover transition-colors cursor-pointer">
                <span className="text-xs font-medium">{i + 1}</span>
                {i === 14 && <div className="mt-1 p-1 rounded bg-primary/20 text-[8px] text-primary truncate">SEO Guide</div>}
                {i === 15 && <div className="mt-1 p-1 rounded bg-blue-500/20 text-[8px] text-blue-400 truncate">Content Strategy</div>}
                {i === 16 && <div className="mt-1 p-1 rounded bg-emerald-500/20 text-[8px] text-emerald-400 truncate">Pinterest Tips</div>}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}