"use client";

import { useEffect, useState } from "react";
import { List } from "lucide-react";

export interface TocHeading {
  id: string;
  text: string;
  level: number;
}

export default function TableOfContents({ headings }: { headings: TocHeading[] }) {
  const [activeId, setActiveId] = useState<string>("");

  useEffect(() => {
    if (headings.length === 0) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setActiveId(entry.target.id);
        }
      },
      { rootMargin: "-80px 0px -70% 0px", threshold: 0 },
    );
    for (const h of headings) {
      const el = document.getElementById(h.id);
      if (el) observer.observe(el);
    }
    return () => observer.disconnect();
  }, [headings]);

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      const top = el.getBoundingClientRect().top + window.scrollY - 90;
      window.scrollTo({ top, behavior: "smooth" });
      setActiveId(id);
    }
  };

  if (headings.length < 2) return null;

  return (
    <nav className="hidden lg:block w-56 shrink-0">
      <div className="sticky top-24">
        <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.2em] text-muted-foreground mb-4">
          <List className="w-3.5 h-3.5" /> On this page
        </div>
        <ul className="space-y-1 border-l border-border">
          {headings.map((h) => (
            <li key={h.id}>
              <button
                type="button"
                onClick={() => scrollTo(h.id)}
                className={`block text-left text-[13px] leading-snug py-1 -ml-px border-l-2 transition-all duration-200 ${
                  h.level === 3 ? "pl-6" : "pl-3"
                } ${
                  activeId === h.id
                    ? "border-accent text-accent font-medium"
                    : "border-border text-muted-foreground hover:text-foreground hover:border-muted-foreground/40"
                }`}
              >
                {h.text}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
