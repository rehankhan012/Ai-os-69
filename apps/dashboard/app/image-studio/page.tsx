"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Palette, Sparkles, Settings2, Download, Maximize2,
  RotateCcw, CheckCircle, AlertTriangle, Eye,
  Layout, Type, Shapes, Image, Layers, Grid3X3,
  ChevronLeft, ChevronRight, Star, Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const TEMPLATES = [
  { id: "minimal", name: "Minimal", vibe: "Clean, whitespace-dominant", icon: Layout },
  { id: "luxury", name: "Luxury", vibe: "Elegant, gold accents", icon: Star },
  { id: "business", name: "Business", vibe: "Professional, structured", icon: Layout },
  { id: "modern", name: "Modern", vibe: "Sleek, contemporary", icon: Zap },
  { id: "magazine", name: "Magazine", vibe: "Editorial, sophisticated", icon: Layers },
  { id: "glassmorphism", name: "Glass", vibe: "Frosted glass, depth", icon: Layers },
  { id: "technology", name: "Tech", vibe: "Digital, innovative", icon: Grid3X3 },
  { id: "education", name: "Education", vibe: "Academic, clear", icon: Image },
  { id: "recipe", name: "Recipe", vibe: "Warm, appetizing", icon: Image },
  { id: "travel", name: "Travel", vibe: "Adventurous, vibrant", icon: Image },
  { id: "fashion", name: "Fashion", vibe: "Chic, stylish", icon: Star },
  { id: "quotes", name: "Quotes", vibe: "Inspirational, typography", icon: Type },
  { id: "infographic", name: "Infographic", vibe: "Data-driven, visual", icon: Shapes },
  { id: "product", name: "Product", vibe: "Product-focused", icon: Layout },
  { id: "comparison", name: "Comparison", vibe: "Comparative, balanced", icon: Grid3X3 },
  { id: "listicle", name: "Listicle", vibe: "Numbered, actionable", icon: ListOrdered },
  { id: "split", name: "Split", vibe: "Balanced, dual-tone", icon: Layout },
  { id: "hero", name: "Hero", vibe: "Bold, dramatic", icon: Maximize2 },
];

const STYLES = ["Minimal", "Luxury", "Business", "Modern", "Glassmorphism", "Technology", "Education", "Recipe", "Travel", "Fashion", "Quotes", "Infographic", "Product", "Comparison", "Listicle", "Split", "Hero"];

type SamplePreview = {
  id?: string;
  variation?: string;
  score?: number;
  quality_score?: number;
  svg?: string;
  colors: string[];
  template: string;
};

const SAMPLE_PREVIEWS: SamplePreview[] = [
  { id: "A", score: 94, colors: ["#2563EB", "#0F172A", "#FFFFFF"], template: "modern" },
  { id: "B", score: 88, colors: ["#8B5CF6", "#1E1B4B", "#FFFFFF"], template: "glassmorphism" },
  { id: "C", score: 82, colors: ["#059669", "#064E3B", "#FFFFFF"], template: "education" },
];

export default function ImageStudioPage() {
  const [topic, setTopic] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("modern");
  const [activeTab, setActiveTab] = useState<"design" | "preview" | "templates">("design");
  const [generating, setGenerating] = useState(false);
  const [previewVar, setPreviewVar] = useState("A");
  const [result, setResult] = useState<{ previews: SamplePreview[]; template: string; rationale: string } | null>(null);
  const [error, setError] = useState("");

  const generateDesign = async () => {
    if (!topic.trim() || generating) return;
    setGenerating(true);
    setError("");
    try {
      const res = await api.post<{ previews: SamplePreview[]; template: string; rationale: string }>("/renderer/preview", {
        topic: topic.trim(),
        audience: "",
        mood: "clean",
        niche: "",
        brand_color: "#2563EB",
        brand_profile: "default",
        variations: 3,
      });
      setResult(res);
      setPreviewVar(res.previews[0]?.variation || res.previews[0]?.id || "A");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Rendering failed — is the API running?");
    } finally {
      setGenerating(false);
    }
  };

  const downloadSvg = (svg: string, name: string) => {
    const blob = new Blob([svg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${name}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="page-container space-y-8"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Palette className="w-6 h-6 text-pink-400" />
            <h1 className="section-title">Graphic Studio</h1>
            <span className="px-2 py-0.5 rounded-full bg-pink-500/10 text-pink-400 text-[10px] font-medium">v3.0</span>
          </div>
          <p className="section-subtitle">AI Graphic Rendering Engine — 18 templates, zero API costs</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2">
            <Settings2 className="w-4 h-4" />
            Brand Profile
          </Button>
          <Button className="gap-2" onClick={generateDesign} disabled={!topic.trim() || generating}>
            {generating ? (
              <><Zap className="w-4 h-4 animate-pulse" /> Generating...</>
            ) : (
              <><Sparkles className="w-4 h-4" /> Generate Design</>
            )}
          </Button>
        </div>
      </motion.div>

      {/* Tabs */}
      <motion.div variants={itemVariants} className="flex gap-1 p-1 rounded-xl bg-glass border border-glass-border w-fit">
        {[
          { id: "design" as const, label: "Design Studio", icon: Palette },
          { id: "preview" as const, label: "Preview", icon: Eye },
          { id: "templates" as const, label: "Template Library", icon: Layout },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
              activeTab === tab.id
                ? "bg-primary/10 text-primary shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </motion.div>

      {/* Design Studio Tab */}
      {activeTab === "design" && (
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Panel */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Design Input</CardTitle>
              <CardDescription>The AI will think like a designer</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Topic / Headline</label>
                <Input
                  placeholder="e.g., 10 AI Tools Every Student Should Know"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Audience</label>
                <Input placeholder="e.g., Students, Professionals, Beginners" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Mood</label>
                <div className="flex flex-wrap gap-2">
                  {["Clean", "Bold", "Elegant", "Playful", "Dark"].map((mood) => (
                    <span key={mood} className="px-3 py-1.5 rounded-lg text-xs border border-glass-border hover:bg-primary/10 hover:text-primary hover:border-primary/30 cursor-pointer transition-all">{mood}</span>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Style / Template</label>
                <div className="flex flex-wrap gap-2">
                  {STYLES.slice(0, 9).map((style) => (
                    <span
                      key={style}
                      onClick={() => setSelectedStyle(style.toLowerCase())}
                      className={cn(
                        "px-3 py-1.5 rounded-lg text-xs border cursor-pointer transition-all",
                        selectedStyle === style.toLowerCase()
                          ? "bg-primary/10 text-primary border-primary/30"
                          : "border-glass-border hover:bg-primary/10 hover:text-primary hover:border-primary/30"
                      )}
                    >{style}</span>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Brand Color</label>
                <div className="flex gap-2">
                  {["#2563EB", "#E94560", "#8B5CF6", "#059669", "#D4AF37", "#F97316"].map((color) => (
                    <div
                      key={color}
                      className="w-8 h-8 rounded-full cursor-pointer border-2 border-transparent hover:border-white/50 transition-all"
                      style={{ backgroundColor: color }}
                      title={color}
                    />
                  ))}
                  <Input type="color" className="w-8 h-8 p-0.5 rounded-full cursor-pointer" defaultValue="#2563EB" />
                </div>
              </div>
              <Button
                className="w-full gap-2"
                size="lg"
                onClick={generateDesign}
                disabled={!topic.trim() || generating}
              >
                {generating ? (
                  <><Zap className="w-4 h-4 animate-pulse" /> AI Designing...</>
                ) : (
                  <><Sparkles className="w-4 h-4" /> Generate Design</>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Preview Area */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Design Preview</CardTitle>
              <CardDescription>AI-generated design specifications</CardDescription>
            </CardHeader>
            <CardContent>
              {!topic ? (
                <div className="text-center py-16 text-muted-foreground">
                  <Palette className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p className="font-medium">Enter a topic to start designing</p>
                  <p className="text-sm mt-1">The AI will select a template, colors, typography, and layout</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Template Selection */}
                  <div className="p-4 rounded-xl bg-glass border border-glass-border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Selected Template</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary capitalize">{selectedStyle}</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {TEMPLATES.find(t => t.id === selectedStyle)?.vibe || "Modern, clean design"}
                    </p>
                  </div>

                  {error && <p className="text-xs text-red-400">{error}</p>}

                  {/* Variations */}
                  <div className="grid grid-cols-3 gap-4">
                    {(result?.previews.length ? result.previews : SAMPLE_PREVIEWS).map((preview) => (
                      <div
                        key={preview.variation || preview.id}
                        onClick={() => setPreviewVar(preview.variation || preview.id || "A")}
                        className={cn(
                          "p-3 rounded-xl border cursor-pointer transition-all",
                          previewVar === (preview.variation || preview.id)
                            ? "border-primary bg-primary/5"
                            : "border-glass-border hover:border-primary/30"
                        )}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-sm font-semibold">Variation {preview.variation || preview.id}</span>
                          <div className="flex items-center gap-1 text-xs text-emerald-400">
                            <CheckCircle className="w-3 h-3" />
                            {preview.quality_score || preview.score}
                          </div>
                        </div>
                        {preview.svg ? (
                          <div
                            className="pin-preview aspect-[2/3] rounded-lg overflow-hidden border border-glass-border"
                            dangerouslySetInnerHTML={{ __html: preview.svg }}
                          />
                        ) : (
                          <>
                            {/* Mini color swatches */}
                            <div className="flex gap-1.5 mb-3">
                              {preview.colors.map((color, i) => (
                                <div key={i} className="w-6 h-6 rounded-md" style={{ backgroundColor: color }} />
                              ))}
                            </div>
                            <div className="aspect-[2/3] rounded-lg bg-gradient-to-br from-muted to-card flex items-center justify-center">
                              <div className="text-center p-2">
                                <p className="text-[8px] font-medium line-clamp-2">{topic}</p>
                                <div className="w-8 h-1.5 rounded-full mx-auto mt-2" style={{ backgroundColor: preview.colors[0] }} />
                              </div>
                            </div>
                          </>
                        )}
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-[10px] text-muted-foreground capitalize">{result?.template || preview.template}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0"
                            onClick={(e) => { e.stopPropagation(); if (preview.svg) downloadSvg(preview.svg, `pin-${preview.variation || preview.id}`); }}
                          >
                            <Download className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Design Details */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-xl bg-glass border border-glass-border">
                      <div className="flex items-center gap-2 mb-2">
                        <Type className="w-4 h-4 text-blue-400" />
                        <span className="text-xs font-medium">Typography</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">Inter 48px Bold · Space Grotesk 18px</p>
                    </div>
                    <div className="p-3 rounded-xl bg-glass border border-glass-border">
                      <div className="flex items-center gap-2 mb-2">
                        <Shapes className="w-4 h-4 text-purple-400" />
                        <span className="text-xs font-medium">Layout</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">Centered · Safe margins 80px · 1000×1500</p>
                    </div>
                    <div className="p-3 rounded-xl bg-glass border border-glass-border">
                      <div className="flex items-center gap-2 mb-2">
                        <Layers className="w-4 h-4 text-emerald-400" />
                        <span className="text-xs font-medium">Background</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">Gradient 135° · Mesh overlay · Glass effect</p>
                    </div>
                    <div className="p-3 rounded-xl bg-glass border border-glass-border">
                      <div className="flex items-center gap-2 mb-2">
                        <Star className="w-4 h-4 text-amber-400" />
                        <span className="text-xs font-medium">Quality Score</span>
                      </div>
                      <p className="text-[10px] text-emerald-400 font-medium">94/100 · Excellent</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Preview Tab */}
      {activeTab === "preview" && (
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Live Preview</CardTitle>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" className="gap-1 text-xs">
                    <Maximize2 className="w-3 h-3" /> Zoom
                  </Button>
                  <Button variant="outline" size="sm" className="gap-1 text-xs">
                    <RotateCcw className="w-3 h-3" /> Reset
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="aspect-[2/3] max-w-[400px] mx-auto bg-gradient-to-br from-primary/5 via-card to-accent/5 rounded-2xl border border-glass-border overflow-hidden relative">
                {/* Faux rendered pin */}
                <div className="absolute inset-0 flex flex-col">
                  <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
                    <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mb-4">
                      <Sparkles className="w-6 h-6 text-primary" />
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">{topic || "Your Headline"}</h3>
                    <p className="text-xs text-muted-foreground mb-4">Perfect for students • Save this pin</p>
                    <div className="px-6 py-2.5 rounded-full bg-primary text-primary-foreground text-xs font-semibold">
                      Save for Later
                    </div>
                  </div>
                  <div className="h-12 border-t border-glass-border flex items-center justify-center">
                    <span className="text-[10px] text-muted-foreground">Follow for more tips</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Export Options</CardTitle>
              <CardDescription>Download your design in multiple formats</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                {[
                  { format: "PNG", desc: "High quality, 1000×1500", size: "~2.5 MB" },
                  { format: "JPG", desc: "Compressed, smaller file", size: "~0.8 MB" },
                  { format: "SVG", desc: "Vector, infinitely scalable", size: "~0.1 MB" },
                  { format: "PDF", desc: "Print-ready document", size: "~3.0 MB" },
                ].map((fmt) => (
                  <div key={fmt.format} className="p-4 rounded-xl border border-glass-border hover:bg-glass-hover transition-colors cursor-pointer group">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-sm">{fmt.format}</span>
                      <Download className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                    </div>
                    <p className="text-[10px] text-muted-foreground">{fmt.desc}</p>
                    <p className="text-[10px] text-muted-foreground">{fmt.size}</p>
                  </div>
                ))}
              </div>
              <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span className="text-xs text-amber-400">Generate a design first to enable exports</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Template Library Tab */}
      {activeTab === "templates" && (
        <motion.div variants={itemVariants}>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {TEMPLATES.map((template) => (
              <div
                key={template.id}
                onClick={() => { setSelectedStyle(template.id); setActiveTab("design"); }}
                className={cn(
                  "p-4 rounded-xl border cursor-pointer transition-all group",
                  selectedStyle === template.id
                    ? "border-primary bg-primary/5"
                    : "border-glass-border hover:border-primary/30 bg-glass"
                )}
              >
                <div className="aspect-[2/3] rounded-lg bg-gradient-to-br from-muted via-card to-muted flex items-center justify-center mb-3">
                  <template.icon className="w-8 h-8 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <h3 className="text-sm font-semibold">{template.name}</h3>
                <p className="text-[10px] text-muted-foreground mt-1">{template.vibe}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

function ListOrdered(props: any) { return <Grid3X3 {...props} />; }