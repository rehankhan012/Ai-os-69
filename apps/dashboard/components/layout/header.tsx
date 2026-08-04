"use client";

import { Bell, Search, ChevronDown, Cpu } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const agentStatuses = [
  { name: "Master", status: "running", color: "bg-purple-400" },
  { name: "Trend", status: "idle", color: "bg-blue-400" },
  { name: "SEO", status: "idle", color: "bg-emerald-400" },
  { name: "Content", status: "idle", color: "bg-amber-400" },
  { name: "Design", status: "idle", color: "bg-pink-400" },
  { name: "Quality", status: "idle", color: "bg-red-400" },
  { name: "Scheduler", status: "idle", color: "bg-indigo-400" },
  { name: "Analytics", status: "completed", color: "bg-teal-400" },
  { name: "Strategy", status: "idle", color: "bg-violet-400" },
];

export function Header() {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="fixed top-0 right-0 left-[260px] z-30 h-14 glass border-b border-glass-border flex items-center justify-between px-6"
    >
      {/* Search */}
      <div className="relative w-96">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search agents, content, keywords..."
          className="pl-10 h-8 bg-background/50 border-glass-border rounded-lg text-sm"
        />
      </div>

      {/* Agent Status Bar */}
      <div className="hidden md:flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-glass border border-glass-border">
          <Cpu className="w-3.5 h-3.5 text-muted-foreground" />
          <div className="flex items-center gap-1.5">
            {agentStatuses.map((agent) => (
              <div
                key={agent.name}
                className={cn(
                  "w-2 h-2 rounded-full",
                  agent.color,
                  agent.status === "running" && "animate-pulse",
                )}
                title={`${agent.name}: ${agent.status}`}
              />
            ))}
          </div>
          <span className="text-[10px] text-muted-foreground font-medium ml-1">
            {agentStatuses.filter((a) => a.status === "running").length > 0 ? "1 active" : "All idle"}
          </span>
        </div>

        <Button variant="ghost" size="icon" className="relative w-8 h-8">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-primary rounded-full" />
        </Button>

        <div className="flex items-center gap-2 pl-3 border-l border-glass-border">
          <Avatar className="w-7 h-7">
            <AvatarFallback className="text-[10px] bg-primary/10 text-primary">JD</AvatarFallback>
          </Avatar>
          <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
        </div>
      </div>
    </motion.header>
  );
}