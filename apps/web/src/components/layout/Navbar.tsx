"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ShieldAlert,
  Terminal,
  Layers,
  FolderGit2,
  Sliders,
  FileCheck2,
  Activity,
  Github,
  History,
} from "lucide-react";
import { api } from "@/lib/api";

export function Navbar() {
  const pathname = usePathname();
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    api.getHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  const navItems = [
    { href: "/dashboard", label: "Bảng điều khiển", icon: Activity },
    { href: "/findings", label: "Lỗ hổng bảo mật", icon: ShieldAlert },
    { href: "/repositories", label: "Kho mã nguồn", icon: FolderGit2 },
    { href: "/audit", label: "Nhật ký kiểm toán", icon: History },
    { href: "/integrations", label: "Tích hợp GitHub", icon: Github },
    { href: "/settings", label: "Cài đặt", icon: Sliders },
  ];

  return (
    <header className="border-b border-border bg-[#090d16]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5 font-bold tracking-tight text-white hover:opacity-90 transition-opacity">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-amber-600 to-orange-400 flex items-center justify-center shadow-lg shadow-orange-500/20">
              <ShieldAlert className="w-5 h-5 text-slate-950" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg">Sentinel</span>
              <span className="text-xs px-1.5 py-0.5 rounded border border-amber-500/30 bg-amber-500/10 text-amber-400 font-mono font-medium">AI BẢO MẬT</span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-zinc-800/80 text-amber-400 border border-zinc-700/60"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Status & Actions */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full border border-zinc-800 bg-zinc-900/60 text-xs text-zinc-300">
            <span
              className={`w-2 h-2 rounded-full ${
                isHealthy === true
                  ? "bg-emerald-500 shadow-[0_0_8px_#10b981]"
                  : isHealthy === false
                  ? "bg-red-500 shadow-[0_0_8px_#ef4444]"
                  : "bg-zinc-500 animate-pulse"
              }`}
            />
            <span className="font-mono">
              {isHealthy === true ? "API HOẠT ĐỘNG" : isHealthy === false ? "MẤT KẾT NỐI API" : "ĐANG KẾT NỐI..."}
            </span>
          </div>

          <div className="hidden sm:flex items-center gap-2 text-xs text-zinc-400 border-l border-zinc-800 pl-4">
            <span className="font-mono text-zinc-500">Không gian:</span>
            <span className="font-medium text-zinc-200">Sec-Ops</span>
          </div>
        </div>
      </div>
    </header>
  );
}
