"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Cpu,
  FileCode,
  FolderGit2,
  Play,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { api, Finding, ScanJob, WorkspaceStats } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<WorkspaceStats | null>(null);
  const [scans, setScans] = useState<ScanJob[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [isTriggering, setIsTriggering] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, scansData, findingsData] = await Promise.all([
        api.getWorkspaceStats(),
        api.getScans(),
        api.getFindings(),
      ]);
      setStats(statsData);
      setScans(scansData);
      setFindings(findingsData);
    } catch (err: any) {
      console.error("Dashboard data fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerQuickScan = async () => {
    setIsTriggering(true);
    try {
      await api.triggerScan({
        repository_id: "default-fixture-repo",
        commit_sha: "9a8b7c6d5e4f3a2b",
        branch_name: "main",
        title: "Scheduled Automated Security Audit",
        ai_triage: true,
        local_path: "./fixtures/vulnerable-repo",
      });
      await loadData();
    } catch (err: any) {
      alert("Error starting scan: " + err.message);
    } finally {
      setIsTriggering(false);
    }
  };

  // Severity metrics calculation
  const severityCounts = {
    CRITICAL: findings.filter((f) => f.severity === "CRITICAL").length,
    HIGH: findings.filter((f) => f.severity === "HIGH").length,
    MEDIUM: findings.filter((f) => f.severity === "MEDIUM").length,
    LOW: findings.filter((f) => f.severity === "LOW").length,
  };

  const filteredFindings = filterSeverity === "ALL" 
    ? findings 
    : findings.filter((f) => f.severity === filterSeverity);

  return (
    <div className="space-y-8">
      {/* Top Banner / Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Security Operations Center
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Real-time status of Pull Request security scans, deterministic findings, and AI triage.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2.5 rounded-lg border border-zinc-800 bg-zinc-900/60 text-zinc-300 hover:bg-zinc-800 transition-colors"
            title="Refresh Dashboard"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>

          <button
            onClick={handleTriggerQuickScan}
            disabled={isTriggering}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold hover:brightness-110 active:scale-95 transition-all shadow-md shadow-orange-500/20 text-sm disabled:opacity-50"
          >
            {isTriggering ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Running Scan...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-slate-950 text-slate-950" />
                <span>Trigger Scan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* KPI Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Scans */}
        <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-1">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-mono">
            <span>TOTAL SCANS</span>
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-white font-mono">
            {stats?.total_scans ?? scans.length}
          </div>
          <div className="text-xs text-emerald-400 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Active Worker Pipeline</span>
          </div>
        </div>

        {/* Critical Vulnerabilities */}
        <div className="p-5 rounded-xl border border-red-900/40 bg-red-950/20 space-y-1">
          <div className="flex items-center justify-between text-xs text-red-400 font-mono">
            <span>CRITICAL SEVERITY</span>
            <AlertTriangle className="w-4 h-4 text-red-500" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-red-400 font-mono">
            {severityCounts.CRITICAL}
          </div>
          <div className="text-xs text-red-300">Requires immediate patch</div>
        </div>

        {/* High Severity */}
        <div className="p-5 rounded-xl border border-orange-900/40 bg-orange-950/20 space-y-1">
          <div className="flex items-center justify-between text-xs text-orange-400 font-mono">
            <span>HIGH SEVERITY</span>
            <ShieldAlert className="w-4 h-4 text-orange-500" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-orange-400 font-mono">
            {severityCounts.HIGH}
          </div>
          <div className="text-xs text-orange-300">Blocks PR merge in review mode</div>
        </div>

        {/* AI Tokens / Budget */}
        <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-1">
          <div className="flex items-center justify-between text-xs text-zinc-400 font-mono">
            <span>AI TRIAGE TOKENS</span>
            <Cpu className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-zinc-200 font-mono">
            {stats?.total_ai_tokens ? stats.total_ai_tokens.toLocaleString() : "370"}
          </div>
          <div className="text-xs text-zinc-500">
            Mode: <span className="text-zinc-300 font-medium">{stats?.review_mode || "ADVISORY"}</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Recent Scans & Top Findings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Scans Table (Col span 2) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <span>Recent Pull Request Scans</span>
            </h2>
            <span className="text-xs text-zinc-500 font-mono">{scans.length} recorded</span>
          </div>

          <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/30">
            {scans.length === 0 ? (
              <div className="p-12 text-center text-zinc-500 text-sm">
                No scans executed yet. Click &quot;Trigger Scan&quot; to run security review against test fixtures.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-zinc-950/60 border-b border-zinc-800 text-xs font-mono text-zinc-400 uppercase">
                    <tr>
                      <th className="px-4 py-3">Scan / Title</th>
                      <th className="px-4 py-3">Branch</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Findings</th>
                      <th className="px-4 py-3">Duration</th>
                      <th className="px-4 py-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60 font-mono text-xs">
                    {scans.slice(0, 8).map((scan) => (
                      <tr key={scan.id} className="hover:bg-zinc-800/30 transition-colors">
                        <td className="px-4 py-3 font-medium text-zinc-200">
                          <div className="font-sans text-sm font-semibold">{scan.title}</div>
                          <div className="text-zinc-500 text-[11px] font-mono">
                            SHA: {scan.commit_sha.substring(0, 8)}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-zinc-400">
                          {scan.branch_name}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold ${
                              scan.status === "SUCCEEDED"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : scan.status === "RUNNING"
                                ? "bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse"
                                : "bg-red-500/10 text-red-400 border border-red-500/20"
                            }`}
                          >
                            {scan.status}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-zinc-200 font-bold">{scan.findings_count ?? 0}</span>
                        </td>
                        <td className="px-4 py-3 text-zinc-400">
                          {scan.duration_seconds ? `${scan.duration_seconds}s` : "—"}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <Link
                            href={`/scans/${scan.id}`}
                            className="text-amber-400 hover:text-amber-300 font-sans text-xs underline"
                          >
                            View Report
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Severity Breakdown & Quick Filters (Col span 1) */}
        <div className="space-y-6">
          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Vulnerabilities by Severity
            </h3>

            <div className="space-y-3">
              {[
                { label: "Critical", count: severityCounts.CRITICAL, color: "bg-red-500", key: "CRITICAL" },
                { label: "High", count: severityCounts.HIGH, color: "bg-orange-500", key: "HIGH" },
                { label: "Medium", count: severityCounts.MEDIUM, color: "bg-yellow-500", key: "MEDIUM" },
                { label: "Low", count: severityCounts.LOW, color: "bg-blue-500", key: "LOW" },
              ].map((item) => (
                <button
                  key={item.key}
                  onClick={() => setFilterSeverity(filterSeverity === item.key ? "ALL" : item.key)}
                  className={`w-full flex items-center justify-between p-2.5 rounded-lg border transition-all text-xs font-mono ${
                    filterSeverity === item.key
                      ? "border-amber-500 bg-amber-500/10"
                      : "border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800/40"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                    <span className="text-zinc-300 font-sans font-medium">{item.label}</span>
                  </div>
                  <span className="text-zinc-100 font-bold">{item.count}</span>
                </button>
              ))}
            </div>

            <div className="pt-2 border-t border-zinc-800">
              <Link
                href="/findings"
                className="w-full block text-center py-2 text-xs font-semibold text-amber-400 hover:text-amber-300"
              >
                Open Full Findings Explorer &rarr;
              </Link>
            </div>
          </div>

          {/* Connected Scanners Widget */}
          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Integrated Security Engines
            </h3>
            <ul className="text-xs space-y-2 text-zinc-300">
              <li className="flex items-center justify-between">
                <span>Bandit Python AST</span>
                <span className="text-emerald-400 font-mono text-[11px]">ACTIVE</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Detect-secrets Engine</span>
                <span className="text-emerald-400 font-mono text-[11px]">ACTIVE</span>
              </li>
              <li className="flex items-center justify-between">
                <span>SARIF 2.1.0 Exporter</span>
                <span className="text-emerald-400 font-mono text-[11px]">ACTIVE</span>
              </li>
              <li className="flex items-center justify-between">
                <span>AI Triage Provider</span>
                <span className="text-amber-400 font-mono text-[11px]">BOUNDED / GROUNDED</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
