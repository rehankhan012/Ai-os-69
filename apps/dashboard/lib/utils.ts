import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
  return num.toLocaleString();
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(date));
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "...";
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function getAgentColor(agent: string): string {
  const colors: Record<string, string> = {
    master: "from-purple-500 to-violet-600",
    trend: "from-blue-500 to-cyan-600",
    seo: "from-emerald-500 to-teal-600",
    content: "from-amber-500 to-orange-600",
    design: "from-pink-500 to-rose-600",
    quality: "from-red-500 to-rose-600",
    scheduler: "from-indigo-500 to-blue-600",
    analytics: "from-teal-500 to-emerald-600",
    strategy: "from-violet-500 to-purple-600",
  };
  return colors[agent.toLowerCase()] || "from-gray-500 to-gray-600";
}

export function getAgentStatusColor(status: string): string {
  const colors: Record<string, string> = {
    idle: "bg-muted-foreground",
    running: "bg-blue-400 animate-pulse",
    completed: "bg-emerald-400",
    failed: "bg-red-400",
    queued: "bg-amber-400",
  };
  return colors[status] || "bg-muted-foreground";
}