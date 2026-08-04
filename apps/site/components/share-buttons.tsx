"use client";

import { useState } from "react";
import { Check, Copy, Facebook, Linkedin, Twitter } from "lucide-react";

export default function ShareButtons({ title }: { title: string }) {
  const [copied, setCopied] = useState(false);
  const url = typeof window !== "undefined" ? window.location.href : "";

  const openShare = (href: string) => {
    window.open(href, "_blank", "noopener,noreferrer,width=600,height=500");
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard unavailable */
    }
  };

  const encodedUrl = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);

  const buttons = [
    {
      label: "Share on X",
      icon: Twitter,
      onClick: () =>
        openShare(
          `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}`,
        ),
    },
    {
      label: "Share on Facebook",
      icon: Facebook,
      onClick: () =>
        openShare(`https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`),
    },
    {
      label: "Share on LinkedIn",
      icon: Linkedin,
      onClick: () =>
        openShare(
          `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
        ),
    },
  ];

  return (
    <div className="flex items-center gap-2">
      <span className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground mr-1">
        Share
      </span>
      {buttons.map((b) => (
        <button
          key={b.label}
          type="button"
          onClick={b.onClick}
          aria-label={b.label}
          title={b.label}
          className="w-9 h-9 rounded-xl border border-border bg-card text-muted-foreground flex items-center justify-center hover:text-accent hover:border-accent/50 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200"
        >
          <b.icon className="w-4 h-4" />
        </button>
      ))}
      <button
        type="button"
        onClick={copyLink}
        aria-label="Copy link"
        title="Copy link"
        className="w-9 h-9 rounded-xl border border-border bg-card text-muted-foreground flex items-center justify-center hover:text-accent hover:border-accent/50 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200"
      >
        {copied ? (
          <Check className="w-4 h-4 text-emerald-400" />
        ) : (
          <Copy className="w-4 h-4" />
        )}
      </button>
      {copied && (
        <span className="text-xs text-emerald-400 animate-fade-in-up">
          Link copied
        </span>
      )}
    </div>
  );
}
