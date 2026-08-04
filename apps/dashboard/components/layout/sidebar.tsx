"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn, getAgentStatusColor } from "@/lib/utils";
import {
  LayoutDashboard,
  Cpu,
  TrendingUp,
  Search,
  FileText,
  Palette,
  ClipboardList,
  ListOrdered,
  Calendar,
  BarChart3,
  Lightbulb,
  Settings,
  ChevronLeft,
  ChevronRight,
  Brain,
  Activity,
  Globe,
  DollarSign,
  Bell,
  Image,
  Layers,
  GitBranch,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";

const navItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/overview" },
  { icon: Cpu, label: "AI Command Center", href: "/ai-command-center", badge: "9 agents" },
  { icon: GitBranch, label: "Content Pipeline", href: "/content-pipeline" },
  { icon: Globe, label: "Website CMS", href: "/cms" },
  { icon: Palette, label: "Pinterest Studio", href: "/image-studio" },
  { icon: Layers, label: "Graphic Studio", href: "/graphic-studio" },
  { icon: Image, label: "Media Library", href: "/media" },
  { icon: TrendingUp, label: "Trend Discovery", href: "/trends" },
  { icon: Search, label: "Keyword Research", href: "/keywords" },
  { icon: FileText, label: "Content Generator", href: "/content" },
  { icon: ClipboardList, label: "Boards", href: "/boards" },
  { icon: ListOrdered, label: "Publishing Queue", href: "/queue" },
  { icon: Calendar, label: "Calendar", href: "/calendar" },
  { icon: BarChart3, label: "Analytics", href: "/analytics" },
  { icon: DollarSign, label: "Revenue", href: "/revenue" },
  { icon: Bell, label: "Notifications", href: "/notifications" },
  { icon: Lightbulb, label: "AI Insights", href: "/insights" },
  { icon: Settings, label: "Settings", href: "/settings" },
];

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

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <motion.aside
      animate={{ width: collapsed ? 80 : 260 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="fixed left-0 top-0 z-40 h-screen glass border-r border-glass-border flex flex-col"
    >
      {/* Logo */}
      <div className={cn("flex items-center h-16 px-4 border-b border-glass-border", collapsed && "justify-center")}>
        <AnimatePresence mode="wait">
          {collapsed ? (
            <motion.div
              key="icon"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center"
            >
              <span className="text-white font-bold text-sm">O</span>
            </motion.div>
          ) : (
            <motion.div
              key="full"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
                <span className="text-white font-bold text-sm">O</span>
              </div>
              <div>
                <h1 className="text-sm font-semibold">AI Content</h1>
                <p className="text-[10px] text-muted-foreground">Operating System</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground hover:bg-glass-hover",
              )}
            >
              <item.icon className={cn("w-5 h-5 shrink-0", isActive && "text-primary")} />
              <AnimatePresence mode="wait">
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    transition={{ duration: 0.15 }}
                    className="text-sm font-medium whitespace-nowrap flex-1"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
              {!collapsed && item.badge && (
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                  {item.badge}
                </span>
              )}
              {isActive && (
                <motion.div
                  layoutId="active-nav"
                  className="absolute inset-0 rounded-xl bg-primary/10"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Agent Status (collapsed only) */}
      {collapsed && (
        <div className="p-3 border-t border-glass-border">
          <div className="flex justify-center gap-1">
            {agentStatuses.slice(0, 5).map((a) => (
              <div
                key={a.name}
                className={cn("w-2 h-2 rounded-full", a.color)}
                title={`${a.name}: ${a.status}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Collapse toggle */}
      <div className="p-3 border-t border-glass-border">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-full p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-glass-hover transition-all duration-200"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </motion.aside>
  );
}