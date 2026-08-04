import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto px-5 sm:px-8 py-28 text-center animate-fade-in-up">
      <p className="text-[11px] uppercase tracking-[0.3em] text-accent font-medium mb-4">404</p>
      <h1 className="font-serif text-4xl sm:text-5xl font-bold tracking-tight">
        This page drifted into the void
      </h1>
      <p className="mt-5 text-muted-foreground max-w-md mx-auto">
        The article you are looking for doesn&apos;t exist or may have been removed.
      </p>
      <Link
        href="/"
        className="inline-flex items-center gap-2 mt-8 px-6 py-3 rounded-2xl bg-accent text-white text-sm font-medium hover:bg-accent/90 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to all articles
      </Link>
    </div>
  );
}
