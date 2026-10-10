import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "Sentinel AI | Production Code Security Review Platform",
  description:
    "Production-grade, open-source AI-powered code security review platform that analyzes GitHub Pull Requests, detects potential vulnerabilities with deterministic security tools, and generates evidence-based review reports.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className="dark">
      <body className="min-h-screen bg-[#07090e] text-zinc-100 flex flex-col selection:bg-amber-500/20 selection:text-amber-300">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-zinc-900 bg-[#05060a] py-6 text-center text-xs text-zinc-500 font-mono">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between px-4 gap-2">
            <span>NỀN TẢNG BẢO MẬT SENTINEL AI &bull; KIỂM ĐỊNH AN NINH MÃ NGUỒN TỰ ĐỘNG</span>
            <div className="flex gap-4 text-zinc-400">
              <a href="http://127.0.0.1:8000/api/v1/metrics" target="_blank" rel="noreferrer" className="hover:text-amber-400 transition-colors">CHỈ SỐ METRICS</a>
              <a href="http://127.0.0.1:8000/api/v1/docs" target="_blank" rel="noreferrer" className="hover:text-amber-400 transition-colors">TÀI LIỆU API (SWAGGER)</a>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
