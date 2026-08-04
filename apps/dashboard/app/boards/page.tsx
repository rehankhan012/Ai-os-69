"use client";

import { motion } from "framer-motion";
import { ClipboardList, Plus, Search } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function BoardsPage() {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="page-container space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <ClipboardList className="w-6 h-6" />
            <h1 className="section-title">Boards</h1>
          </div>
          <p className="section-subtitle">Organize your pins into boards</p>
        </div>
        <Button className="gap-2"><Plus className="w-4 h-4" />Create Board</Button>
      </div>
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input placeholder="Search boards..." className="pl-10" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { name: "SEO Strategies", pins: 24, color: "from-blue-500/20 to-purple-500/20" },
          { name: "Content Marketing", pins: 18, color: "from-emerald-500/20 to-teal-500/20" },
          { name: "Social Media Tips", pins: 32, color: "from-red-500/20 to-pink-500/20" },
          { name: "Design Inspiration", pins: 15, color: "from-amber-500/20 to-orange-500/20" },
          { name: "Business Growth", pins: 21, color: "from-violet-500/20 to-purple-500/20" },
          { name: "Tech Trends", pins: 12, color: "from-cyan-500/20 to-blue-500/20" },
        ].map((board, i) => (
          <Card key={i} className="group overflow-hidden cursor-pointer hover:shadow-xl transition-all">
            <div className={`h-32 bg-gradient-to-br ${board.color} flex items-center justify-center`}>
              <ClipboardList className="w-10 h-10 text-foreground/60" />
            </div>
            <CardContent className="p-4">
              <h3 className="font-semibold">{board.name}</h3>
              <p className="text-sm text-muted-foreground mt-1">{board.pins} pins</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
}