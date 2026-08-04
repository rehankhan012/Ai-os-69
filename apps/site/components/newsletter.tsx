"use client";

import { useState } from "react";
import { ArrowRight, Check, Sparkles } from "lucide-react";

export default function Newsletter() {
  const [email, setEmail] = useState("");
  const [done, setDone] = useState(false);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes("@")) return;
    setDone(true);
  };

  return (
    <section className="mt-24 rounded-3xl border border-border overflow-hidden relative animate-fade-in-up">
      <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-accent/10 blur-3xl" />
      <div className="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-blue-500/10 blur-3xl" />
      <div className="relative px-8 sm:px-14 py-14 sm:py-16 text-center">
        <span className="inline-flex items-center gap-1.5 text-[11px] uppercase tracking-[0.3em] text-accent font-medium mb-5">
          <Sparkles className="w-3.5 h-3.5" /> The Sunday Dispatch
        </span>
        <h2 className="font-serif text-3xl sm:text-4xl font-bold tracking-tight">
          Stories worth stopping for, in your inbox
        </h2>
        <p className="mt-4 text-muted-foreground max-w-lg mx-auto">
          One thoughtful email a week — the best essays, ideas, and deep dives
          from the archive. No noise, ever.
        </p>

        {done ? (
          <div className="mt-8 inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-medium animate-fade-in-up">
            <Check className="w-4 h-4" /> You&apos;re on the list — see you Sunday.
          </div>
        ) : (
          <form
            onSubmit={submit}
            className="mt-8 flex flex-col sm:flex-row gap-2.5 max-w-md mx-auto"
          >
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="flex-1 h-12 rounded-2xl bg-card border border-border pl-5 pr-4 text-sm outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent/50 transition-all placeholder:text-muted-foreground"
            />
            <button
              type="submit"
              className="h-12 px-6 rounded-2xl bg-accent text-white text-sm font-medium inline-flex items-center justify-center gap-2 hover:bg-accent/90 hover:gap-3 transition-all shadow-lg shadow-accent/20"
            >
              Subscribe <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
