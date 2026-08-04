"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Layers, Sparkles, Download, Layout, Loader2, CheckCircle, Wand2,
  Pin, ExternalLink, ChevronDown, AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

const TEMPLATES = [
  { id: "minimal", name: "Minimal", vibe: "Clean, whitespace-dominant" },
  { id: "luxury", name: "Luxury", vibe: "Elegant, gold accents" },
  { id: "business", name: "Business", vibe: "Professional, structured" },
  { id: "modern", name: "Modern", vibe: "Sleek, contemporary" },
  { id: "glassmorphism", name: "Glass", vibe: "Frosted glass, depth" },
  { id: "technology", name: "Tech", vibe: "Digital, innovative" },
  { id: "education", name: "Education", vibe: "Academic, clear" },
  { id: "recipe", name: "Recipe", vibe: "Warm, appetizing" },
  { id: "travel", name: "Travel", vibe: "Adventurous, vibrant" },
  { id: "fashion", name: "Fashion", vibe: "Chic, stylish" },
  { id: "quotes", name: "Quotes", vibe: "Inspirational, typography" },
  { id: "infographic", name: "Infographic", vibe: "Data-driven, visual" },
  { id: "product", name: "Product", vibe: "Product-focused" },
  { id: "comparison", name: "Comparison", vibe: "Comparative, balanced" },
  { id: "listicle", name: "Listicle", vibe: "Numbered, actionable" },
  { id: "split", name: "Split", vibe: "Balanced, dual-tone" },
  { id: "hero", name: "Hero", vibe: "Bold, dramatic" },
];

interface PreviewResult {
  success: boolean;
  topic: string;
  template: string;
  rationale: string;
  previews: Array<{ variation: string; quality_score: number; svg: string }>;
}

interface PinterestBoard {
  id: string;
  name: string;
  description?: string;
  privacy?: string;
  pin_count?: number;
}

interface PinterestStatus {
  connected: boolean;
  account: { username?: string };
}

export default function GraphicStudioPage() {
  const [topic, setTopic] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<PreviewResult | null>(null);
  const [error, setError] = useState("");
  const [selectedVar, setSelectedVar] = useState("A");

  // Pinterest publish state
  const [pinterestStatus, setPinterestStatus] = useState<PinterestStatus | null>(null);
  const [boards, setBoards] = useState<PinterestBoard[]>([]);
  const [selectedBoard, setSelectedBoard] = useState("");
  const [boardMenuOpen, setBoardMenuOpen] = useState(false);
  const [pinTitle, setPinTitle] = useState("");
  const [pinDesc, setPinDesc] = useState("");
  const [publishing, setPublishing] = useState(false);
  const [publishedPin, setPublishedPin] = useState<{ id: string; link?: string } | null>(null);
  const [publishError, setPublishError] = useState("");

  const generate = async () => {
    if (!topic.trim() || generating) return;
    setGenerating(true);
    setError("");
    setPublishedPin(null);
    try {
      const res = await api.post<PreviewResult>("/renderer/preview", {
        topic: topic.trim(),
        audience: "",
        mood: "clean",
        niche: "",
        brand_color: "#2563EB",
        brand_profile: "default",
        variations: 3,
      });
      setResult(res);
      setSelectedVar(res.previews[0]?.variation || "A");
      setPinTitle(res.topic);
      // Load Pinterest connection + boards so publish is one click away
      loadPinterest();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Rendering failed — is the API running?");
    } finally {
      setGenerating(false);
    }
  };

  const loadPinterest = async () => {
    try {
      const status = await api.get<PinterestStatus>("/pinterest/status");
      setPinterestStatus(status);
      if (status.connected) {
        const boardsRes = await api.get<{ boards: PinterestBoard[] }>("/pinterest/boards");
        setBoards(boardsRes.boards || []);
        if (boardsRes.boards?.length) setSelectedBoard(boardsRes.boards[0].id);
      }
    } catch {
      setPinterestStatus(null);
    }
  };

  const selectedPreview = result?.previews.find((p) => p.variation === selectedVar) || result?.previews[0];

  const downloadSvg = (svg: string, name: string) => {
    const blob = new Blob([svg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${name}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  /** Rasterize the SVG to a PNG data URL using an in-memory canvas. */
  const svgToPngBase64 = async (svg: string, width = 1000, height = 1500): Promise<string> => {
    const blob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    try {
      const img = new Image();
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = url;
      });
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d")!;
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      return canvas.toDataURL("image/png");
    } finally {
      URL.revokeObjectURL(url);
    }
  };

  const publishToPinterest = async () => {
    if (!selectedPreview || !selectedBoard || publishing) return;
    setPublishing(true);
    setPublishError("");
    setPublishedPin(null);
    try {
      const pngBase64 = await svgToPngBase64(selectedPreview.svg);
      const res = await api.post<{ success: boolean; pin: { id: string; link?: string } }>("/pinterest/pins", {
        board_id: selectedBoard,
        title: pinTitle.trim() || result?.topic || topic,
        description: pinDesc.trim(),
        image_base64: pngBase64,
        image_content_type: "image/png",
        alt_text: (result?.topic || topic).slice(0, 500),
      });
      setPublishedPin(res.pin);
      // Refresh board pin counts
      loadPinterest();
    } catch (e) {
      setPublishError(e instanceof Error ? e.message : "Publishing failed");
    } finally {
      setPublishing(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Layers className="w-6 h-6 text-purple-400" />
            <h1 className="section-title">Graphic Studio</h1>
            <span className="px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 text-[10px] font-medium">Rendering Engine</span>
          </div>
          <p className="section-subtitle">AI Graphic Rendering Engine — 17 templates, zero API costs, publish straight to Pinterest</p>
        </div>
        <Button className="gap-2" onClick={generate} disabled={!topic.trim() || generating}>
          {generating ? <><Loader2 className="w-4 h-4 animate-spin" /> Rendering...</> : <><Sparkles className="w-4 h-4" />Generate Graphic</>}
        </Button>
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Design Input */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Design Input</CardTitle>
            <CardDescription>AI renders code-based graphics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Topic / Headline</label>
              <Input
                placeholder="e.g., 10 AI Tools Every Student Should Know"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && generate()}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Template Library</label>
              <div className="grid grid-cols-3 gap-1.5 max-h-[200px] overflow-y-auto">
                {TEMPLATES.map((t) => (
                  <div key={t.id} className="p-2 rounded-lg border border-glass-border hover:border-primary/30 cursor-pointer transition-all text-center">
                    <div className="aspect-[2/3] rounded bg-gradient-to-br from-muted to-card mb-1 flex items-center justify-center">
                      <Layout className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <p className="text-[9px] font-medium truncate">{t.name}</p>
                  </div>
                ))}
              </div>
            </div>
            <Button className="w-full gap-2" size="lg" onClick={generate} disabled={!topic.trim() || generating}>
              {generating ? <><Loader2 className="w-4 h-4 animate-spin" /> Rendering...</> : <><Wand2 className="w-4 h-4" />Generate 3 Variations</>}
            </Button>

            {/* Pinterest publish panel */}
            {result && (
              <div className="pt-2 border-t border-glass-border space-y-3">
                <div className="flex items-center gap-2">
                  <Pin className="w-4 h-4 text-red-400" />
                  <p className="text-sm font-semibold">Publish to Pinterest</p>
                  {pinterestStatus?.connected ? (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> @{pinterestStatus.account.username}
                    </span>
                  ) : (
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400">not connected</span>
                  )}
                </div>

                {!pinterestStatus?.connected ? (
                  <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-3 text-[11px] text-muted-foreground">
                    Connect your Pinterest account in <span className="text-primary">Settings → Pinterest Account</span> to publish pins directly from here.
                  </div>
                ) : (
                  <>
                    <div className="space-y-1.5">
                      <label className="text-[11px] font-medium text-muted-foreground">Board</label>
                      <div className="relative">
                        <button
                          onClick={() => setBoardMenuOpen(!boardMenuOpen)}
                          className="w-full h-10 px-3 rounded-lg border border-glass-border bg-glass text-xs flex items-center justify-between hover:border-primary/40 transition-colors"
                        >
                          <span className="truncate">{boards.find((b) => b.id === selectedBoard)?.name || "Select a board..."}</span>
                          <ChevronDown className={cn("w-3.5 h-3.5 text-muted-foreground transition-transform", boardMenuOpen && "rotate-180")} />
                        </button>
                        {boardMenuOpen && (
                          <div className="absolute z-20 mt-1 w-full rounded-lg border border-glass-border bg-card shadow-xl max-h-48 overflow-y-auto">
                            {boards.length === 0 && (
                              <div className="p-3 text-[11px] text-muted-foreground">No boards found — create one on Pinterest.</div>
                            )}
                            {boards.map((b) => (
                              <button
                                key={b.id}
                                onClick={() => { setSelectedBoard(b.id); setBoardMenuOpen(false); }}
                                className="w-full text-left px-3 py-2 text-xs hover:bg-primary/10 transition-colors"
                              >
                                {b.name}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[11px] font-medium text-muted-foreground">Pin title</label>
                      <Input value={pinTitle} onChange={(e) => setPinTitle(e.target.value)} className="h-9 text-xs" />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[11px] font-medium text-muted-foreground">Description</label>
                      <textarea
                        value={pinDesc}
                        onChange={(e) => setPinDesc(e.target.value)}
                        rows={3}
                        className="w-full rounded-lg border border-glass-border bg-glass px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                        placeholder="SEO description + hashtags..."
                      />
                    </div>
                    <Button
                      className="w-full gap-2"
                      disabled={publishing || !selectedBoard}
                      onClick={publishToPinterest}
                    >
                      {publishing ? <><Loader2 className="w-4 h-4 animate-spin" /> Publishing...</> : <><Pin className="w-4 h-4" />Publish Pin Live</>}
                    </Button>
                    {publishError && <p className="text-[11px] text-red-400">{publishError}</p>}
                    {publishedPin && (
                      <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-3">
                        <p className="text-[11px] text-emerald-400 flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5" /> Pin published successfully!
                        </p>
                        <a
                          href={`https://www.pinterest.com/pin/${publishedPin.id}/`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] text-primary underline flex items-center gap-1 mt-1"
                        >
                          View on Pinterest <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Preview */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Live Preview</CardTitle>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" className="gap-1 text-xs" onClick={() => selectedPreview && downloadSvg(selectedPreview.svg, `${(result?.topic || topic).replace(/\s+/g, "-").toLowerCase()}-${selectedPreview.variation}`)}>
                  <Download className="w-3 h-3" /> Export SVG
                </Button>
              </div>
            </div>
            <CardDescription>
              {result
                ? `Template: ${result.template} — ${result.rationale}`
                : "The AI selects a template, colors, typography, and layout automatically"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!result ? (
              <div className="text-center py-16 text-muted-foreground">
                <Layers className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="font-medium">Enter a topic to generate graphics</p>
                <p className="text-sm mt-1">The AI will select a template, colors, typography, and layout</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Variation thumbnails */}
                <div className="flex gap-3">
                  {result.previews.map((p) => (
                    <button
                      key={p.variation}
                      onClick={() => setSelectedVar(p.variation)}
                      className={cn(
                        "rounded-lg border transition-all p-2",
                        selectedVar === p.variation
                          ? "border-primary/60 bg-primary/10"
                          : "border-glass-border hover:border-primary/30",
                      )}
                    >
                      <span className="text-[10px] font-semibold block text-center mb-1">Var {p.variation}</span>
                      <span className={cn("text-[10px] px-1.5 py-0.5 rounded-full block text-center", p.quality_score >= 85 ? "bg-emerald-500/15 text-emerald-400" : "bg-amber-500/15 text-amber-400")}>
                        {p.quality_score}/100
                      </span>
                    </button>
                  ))}
                </div>

                {/* Main preview */}
                {selectedPreview && (
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={selectedPreview.variation}
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      transition={{ duration: 0.25 }}
                      className="flex justify-center"
                    >
                      <div
                        className="pin-preview rounded-xl overflow-hidden border border-glass-border shadow-2xl"
                        style={{ width: 300, height: 450 }}
                        dangerouslySetInnerHTML={{ __html: selectedPreview.svg }}
                      />
                    </motion.div>
                  </AnimatePresence>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Gallery of generated variations */}
      {result && result.previews.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" /> All Variations
            </CardTitle>
            <CardDescription>Three AI-designed variations — different layout, colors, typography, and hierarchy</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.previews.map((p) => (
                <div key={p.variation} className="flex flex-col items-center gap-2">
                  <div
                    className="pin-preview rounded-xl overflow-hidden border border-glass-border w-full max-w-[260px]"
                    style={{ aspectRatio: "2/3" }}
                    dangerouslySetInnerHTML={{ __html: p.svg }}
                  />
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold">Variation {p.variation}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400">{p.quality_score}/100</span>
                    <button onClick={() => downloadSvg(p.svg, `pin-${p.variation}`)} className="text-[10px] text-muted-foreground hover:text-primary flex items-center gap-1">
                      <Download className="w-3 h-3" /> SVG
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  );
}
