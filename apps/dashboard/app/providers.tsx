"use client";

import { useEffect } from "react";
import { Toaster } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { ensureAuth } from "@/lib/auth";

export function Providers({ children }: { children: React.ReactNode }) {
  // Auto-provision a local demo account so every API call is authenticated.
  useEffect(() => {
    ensureAuth();
  }, []);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            color: "hsl(var(--foreground))",
          },
        }}
      />
    </AnimatePresence>
  );
}
