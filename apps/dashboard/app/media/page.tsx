"use client";

import { motion } from "framer-motion";
import { Image, Upload, Search, FolderOpen, Trash2, Download, FileImage, FileType } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

const mediaItems = [
  { name: "hero-banner.png", type: "image", size: "2.4 MB", dimensions: "1200×630", date: "Today" },
  { name: "pinterest-pin-1.svg", type: "svg", size: "0.1 MB", dimensions: "1000×1500", date: "Yesterday" },
  { name: "logo-dark.svg", type: "svg", size: "0.02 MB", dimensions: "200×200", date: "2 days ago" },
  { name: "featured-article.jpg", type: "image", size: "1.8 MB", dimensions: "1200×800", date: "3 days ago" },
  { name: "icon-set.svg", type: "svg", size: "0.3 MB", dimensions: "512×512", date: "1 week ago" },
  { name: "brand-colors.png", type: "image", size: "0.5 MB", dimensions: "800×600", date: "2 weeks ago" },
];

export default function MediaPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Image className="w-6 h-6 text-blue-400" />
            <h1 className="section-title">Media Library</h1>
          </div>
          <p className="section-subtitle">Unified assets for website and Pinterest content</p>
        </div>
        <Button className="gap-2"><Upload className="w-4 h-4" /> Upload Media</Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search media..." className="pl-10" />
        </div>
        <div className="flex gap-2">
          <Badge variant="secondary" className="px-3 py-1.5 cursor-pointer">All</Badge>
          <Badge variant="outline" className="px-3 py-1.5 cursor-pointer hover:bg-primary/10">Images</Badge>
          <Badge variant="outline" className="px-3 py-1.5 cursor-pointer hover:bg-primary/10">SVG</Badge>
          <Badge variant="outline" className="px-3 py-1.5 cursor-pointer hover:bg-primary/10">Graphics</Badge>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {mediaItems.map((item, i) => (
          <Card key={i} className="group overflow-hidden">
            <div className="aspect-square bg-gradient-to-br from-muted via-card to-muted flex items-center justify-center relative">
              {item.type === "svg" ? (
                <FileType className="w-10 h-10 text-muted-foreground group-hover:scale-110 transition-transform" />
              ) : (
                <FileImage className="w-10 h-10 text-muted-foreground group-hover:scale-110 transition-transform" />
              )}
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <Button variant="ghost" size="icon" className="text-white"><Download className="w-4 h-4" /></Button>
                <Button variant="ghost" size="icon" className="text-red-400"><Trash2 className="w-4 h-4" /></Button>
              </div>
            </div>
            <CardContent className="p-3">
              <p className="text-xs font-medium truncate">{item.name}</p>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className="text-[8px]">{item.type.toUpperCase()}</Badge>
                <span className="text-[9px] text-muted-foreground">{item.size}</span>
              </div>
              <p className="text-[9px] text-muted-foreground mt-0.5">{item.dimensions} · {item.date}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
}