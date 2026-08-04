"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Settings, User, Palette, Bell, Key, Globe, Image, Cpu,
  Pin, Link2, Unlink, ExternalLink, Loader2, CheckCircle2, AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import api from "@/lib/api";
import { ensureAuth } from "@/lib/auth";

const sections = [
  { icon: User, label: "Profile", desc: "Manage your account details" },
  { icon: Cpu, label: "AI Agents", desc: "Configure agent behavior and providers" },
  { icon: Palette, label: "Brand", desc: "Brand colors, fonts, and templates" },
  { icon: Bell, label: "Notifications", desc: "Email and push notification preferences" },
  { icon: Key, label: "API Keys", desc: "Manage API integrations" },
  { icon: Globe, label: "Localization", desc: "Language, timezone, and region" },
  { icon: Image, label: "Defaults", desc: "Default pin styles and sizes" },
];

interface PinterestStatus {
  connected: boolean;
  /** Whether Pinterest developer credentials are present in the backend .env. */
  configured?: boolean;
  account: {
    username?: string;
    full_name?: string;
    board_count?: number;
    pin_count?: number;
    follower_count?: number;
    profile_image_url?: string;
  };
}

export default function SettingsPage() {
  const [status, setStatus] = useState<PinterestStatus>({ connected: false, account: {} });
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [error, setError] = useState("");
  const [configError, setConfigError] = useState("");

  const loadStatus = async () => {
    await ensureAuth();
    try {
      const res = await api.get<PinterestStatus>("/pinterest/status");
      setStatus(res);
      if (!res.connected && res.configured === false) {
        setConfigError(
          "Pinterest is not configured. Add PINTEREST_CLIENT_ID and PINTEREST_CLIENT_SECRET to .env (create a free app at developers.pinterest.com).",
        );
      } else {
        setConfigError("");
      }
    } catch (e) {
      if (e instanceof Error && e.message.toLowerCase().includes("configured")) {
        setConfigError(e.message);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    // If we just came back from Pinterest OAuth
    if (typeof window !== "undefined" && new URLSearchParams(window.location.search).get("pinterest") === "connected") {
      loadStatus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const connect = async () => {
    setConnecting(true);
    setError("");
    try {
      const res = await api.get<{ authorization_url: string }>("/pinterest/auth-url");
      // Open Pinterest OAuth in a new tab; user approves and Pinterest redirects
      // back to our callback which bounces to /settings?pinterest=connected
      window.open(res.authorization_url, "_blank");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to start connection";
      if (msg.toLowerCase().includes("configured")) {
        // Missing Pinterest developer credentials → show the friendly setup box
        setConfigError(msg);
      } else {
        setError(msg);
      }
    } finally {
      setConnecting(false);
    }
  };

  const disconnect = async () => {
    setDisconnecting(true);
    try {
      await api.post("/pinterest/disconnect");
      setStatus({ connected: false, account: {} });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Disconnect failed");
    } finally {
      setDisconnecting(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div>
        <h1 className="section-title">Settings</h1>
        <p className="section-subtitle">Configure your AI Content OS</p>
      </div>

      {/* Pinterest Connection */}
      <Card className={cn("border", status.connected ? "border-emerald-500/30" : "border-glass-border")}>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className={cn("p-2 rounded-xl", status.connected ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400")}>
              <Pin className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <CardTitle className="text-base flex items-center gap-2">
                Pinterest Account
                {status.connected && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Connected
                  </span>
                )}
              </CardTitle>
              <CardDescription>
                {status.connected
                  ? `Connected as @${status.account.username || "pinterest user"} — publish real pins, manage boards, and pull analytics`
                  : "Connect your real Pinterest account to publish pins directly"}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {configError ? (
            <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-4 flex items-start gap-3">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-medium text-amber-400">Pinterest API not configured yet</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {configError} Create a free app at{" "}
                  <a href="https://developers.pinterest.com" target="_blank" rel="noreferrer" className="text-primary underline">developers.pinterest.com</a>,
                  then set <code className="text-[10px] px-1 py-0.5 rounded bg-muted">PINTEREST_CLIENT_ID</code> and{" "}
                  <code className="text-[10px] px-1 py-0.5 rounded bg-muted">PINTEREST_CLIENT_SECRET</code> in your <code className="text-[10px] px-1 py-0.5 rounded bg-muted">.env</code>.
                </p>
              </div>
            </div>
          ) : loading ? (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Checking connection...
            </div>
          ) : status.connected ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: "Username", value: status.account.username || "—" },
                  { label: "Boards", value: status.account.board_count ?? "—" },
                  { label: "Pins", value: status.account.pin_count ?? "—" },
                  { label: "Followers", value: status.account.follower_count ?? "—" },
                ].map((s, i) => (
                  <div key={i} className="rounded-xl bg-glass border border-glass-border p-3">
                    <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{s.label}</p>
                    <p className="text-sm font-semibold mt-0.5">{String(s.value)}</p>
                  </div>
                ))}
              </div>
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" className="gap-2" onClick={disconnect} disabled={disconnecting}>
                  {disconnecting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Unlink className="w-3.5 h-3.5" />}
                  Disconnect
                </Button>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => window.open("https://www.pinterest.com", "_blank")}>
                  <ExternalLink className="w-3.5 h-3.5" /> Open Pinterest
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-3">
              <Button size="lg" className="gap-2" onClick={connect} disabled={connecting}>
                {connecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link2 className="w-4 h-4" />}
                {connecting ? "Opening Pinterest..." : "Connect Pinterest Account"}
              </Button>
              <p className="text-[11px] text-muted-foreground">
                Authorize in the new tab, then return here — you'll be connected automatically.
              </p>
            </div>
          )}
          {error && <p className="text-xs text-red-400">{error}</p>}
        </CardContent>
      </Card>

      {/* Setting categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sections.map((section, i) => (
          <Card key={i} className="group cursor-pointer hover:shadow-xl transition-all duration-300">
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="p-2 rounded-lg bg-primary/10 text-primary"><section.icon className="w-5 h-5" /></div>
                <div>
                  <CardTitle className="text-base">{section.label}</CardTitle>
                  <CardDescription>{section.desc}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <span className="text-xs px-2 py-1 rounded-full bg-glass border border-glass-border group-hover:bg-primary/10 group-hover:text-primary transition-colors">Configure →</span>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* AI Provider Settings */}
      <Card>
        <CardHeader>
          <CardTitle>AI Provider Settings</CardTitle>
          <CardDescription>Choose your preferred AI models for each agent</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { name: "GPT-4o", provider: "OpenAI", desc: "Best for general content & SEO" },
              { name: "Claude 3.5", provider: "Anthropic", desc: "Best for creative writing & strategy" },
              { name: "Gemini Pro", provider: "Google", desc: "Best for research & analytics" },
            ].map((model, i) => (
              <div key={i} className="p-4 rounded-xl border border-glass-border hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{model.name}</span>
                  <input type="radio" name="ai-provider" className="accent-primary" defaultChecked={i === 0} />
                </div>
                <p className="text-xs text-muted-foreground">{model.provider}</p>
                <p className="text-xs text-muted-foreground mt-1">{model.desc}</p>
              </div>
            ))}
          </div>
          <Button>Save Settings</Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}
