import type { Metadata } from "next";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { Providers } from "./providers";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "AI Content OS",
  description: "Unified AI-powered content operating system — Website CMS, Pinterest Studio, Graphic Engine, and Revenue Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="dark">
        <Providers>
          <Sidebar />
          <Header />
          <main className="ml-[260px] mt-14 min-h-screen bg-background">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}