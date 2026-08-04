import type { Metadata } from "next";
import { Inter, Lora } from "next/font/google";
import Link from "next/link";
import { Twitter, Instagram, Linkedin, Youtube } from "lucide-react";
import { getSiteInfo } from "@/lib/api";
import "@/styles/globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const lora = Lora({ subsets: ["latin"], variable: "--font-serif" });

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  let title = "Darkverse";
  let description = "A blog about ideas, technology, and the stories shaping the world.";
  try {
    const info = await getSiteInfo();
    title = info.name;
    if (info.description) description = info.description;
  } catch {
    // fall back to defaults
  }
  return {
    title: { default: title, template: `%s — ${title}` },
    description,
    openGraph: {
      title,
      description,
      type: "website",
    },
  };
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let tagline = "";
  try {
    const info = await getSiteInfo();
    tagline = info.tagline;
  } catch {
    // fall back to empty
  }

  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${lora.variable} font-sans bg-background text-foreground min-h-screen flex flex-col`}
      >
        <header className="sticky top-0 z-40 backdrop-blur-xl bg-background/80 border-b border-border">
          <div className="max-w-5xl mx-auto px-5 sm:px-8 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2.5 group">
              <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent via-purple-600 to-blue-600 flex items-center justify-center text-white text-sm font-bold shadow-lg shadow-accent/20 group-hover:shadow-accent/40 transition-shadow">
                D
              </span>
              <span className="font-serif text-lg font-semibold tracking-tight">
                Darkverse
              </span>
            </Link>
            <nav className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link href="/" className="hover:text-foreground transition-colors">
                Home
              </Link>
              <Link
                href="/#categories"
                className="hover:text-foreground transition-colors hidden sm:block"
              >
                Categories
              </Link>
              {tagline && (
                <span className="hidden md:block text-xs text-muted-foreground/70 max-w-[220px] truncate">
                  {tagline}
                </span>
              )}
            </nav>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-border mt-24">
          <div className="max-w-5xl mx-auto px-5 sm:px-8 py-12 flex flex-col sm:flex-row items-center justify-between gap-8">
            <div className="flex flex-col items-center sm:items-start gap-2">
              <div className="flex items-center gap-2.5">
                <span className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent via-purple-600 to-blue-600 flex items-center justify-center text-white text-xs font-bold shadow-lg shadow-accent/20">
                  D
                </span>
                <span className="font-serif text-base font-semibold tracking-tight">
                  Darkverse
                </span>
              </div>
              <p className="text-xs text-muted-foreground/70">
                Stories, ideas, and deep dives.
              </p>
            </div>

            <nav className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link href="/" className="hover:text-foreground transition-colors">
                Home
              </Link>
              <Link
                href="/#categories"
                className="hover:text-foreground transition-colors"
              >
                Categories
              </Link>
            </nav>

            <div className="flex items-center gap-2">
              {[
                { label: "X (Twitter)", icon: Twitter },
                { label: "Instagram", icon: Instagram },
                { label: "LinkedIn", icon: Linkedin },
                { label: "YouTube", icon: Youtube },
              ].map((s) => (
                <a
                  key={s.label}
                  href="#"
                  aria-label={s.label}
                  title={s.label}
                  className="w-9 h-9 rounded-xl border border-border bg-card text-muted-foreground flex items-center justify-center hover:text-accent hover:border-accent/50 hover:-translate-y-0.5 transition-all duration-200"
                >
                  <s.icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>
          <div className="border-t border-border">
            <p className="max-w-5xl mx-auto px-5 sm:px-8 py-5 text-xs text-muted-foreground/60 text-center sm:text-left">
              © {new Date().getFullYear()} Darkverse. All rights reserved.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
