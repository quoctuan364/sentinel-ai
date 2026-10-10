"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  Filter,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { api, Finding } from "@/lib/api";

export default function FindingsExplorerPage() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("");
  const [selectedStatus, setSelectedStatus] = useState<string>("");

  const loadFindings = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getFindings({
        severity: selectedSeverity || undefined,
        status: selectedStatus || undefined,
        search: search || undefined,
      });
      setFindings(data);
    } catch (err: any) {
      console.error("Failed to load findings:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedSeverity, selectedStatus, search]);

  useEffect(() => {
    loadFindings();
  }, [loadFindings]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadFindings();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Security Findings Explorer
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Browse, filter, and triage normalized static analysis findings across all repositories.
          </p>
        </div>

        <button
          onClick={loadFindings}
          disabled={loading}
          className="p-2.5 rounded-lg border border-zinc-800 bg-zinc-900/60 text-zinc-300 hover:bg-zinc-800 transition-colors self-start sm:self-auto"
          title="Refresh Findings"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row items-center gap-3 bg-zinc-900/40 p-4 rounded-xl border border-zinc-800">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by title, rule, or file path..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-9 pr-4 py-2 text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-amber-500 font-mono"
          />
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Severity filter */}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-300 font-mono focus:outline-none focus:border-amber-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Lifecycle Status filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-300 font-mono focus:outline-none focus:border-amber-500"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="RESOLVED">Resolved</option>
            <option value="WONT_FIX">Won&apos;t Fix</option>
          </select>
        </div>
      </div>

      {/* Findings Table */}
      <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/30">
        {loading ? (
          <div className="p-16 text-center">
            <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <span className="text-zinc-500 font-mono text-xs">Querying security database...</span>
          </div>
        ) : findings.length === 0 ? (
          <div className="p-16 text-center text-zinc-500 text-sm">
            No matching security findings found for the selected filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-950/60 border-b border-zinc-800 text-xs font-mono text-zinc-400 uppercase">
                <tr>
                  <th className="px-4 py-3">Severity</th>
                  <th className="px-4 py-3">Finding Title / CWE</th>
                  <th className="px-4 py-3">File Location</th>
                  <th className="px-4 py-3">Scanner</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-mono text-xs">
                {findings.map((f) => (
                  <tr key={f.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
                          f.severity === "CRITICAL"
                            ? "bg-red-500/20 text-red-400 border border-red-500/40"
                            : f.severity === "HIGH"
                            ? "bg-orange-500/20 text-orange-400 border border-orange-500/40"
                            : f.severity === "MEDIUM"
                            ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/40"
                            : "bg-blue-500/20 text-blue-400 border border-blue-500/40"
                        }`}
                      >
                        {f.severity}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-sans">
                      <div className="font-semibold text-zinc-200">{f.title}</div>
                      <div className="text-zinc-500 text-[11px] font-mono">
                        {f.cwe_id || f.rule_id}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-zinc-400">
                      <span className="text-amber-400">{f.file_path}</span>
                      <span className="text-zinc-500 text-[11px]"> : {f.start_line}</span>
                    </td>
                    <td className="px-4 py-3 text-zinc-300">
                      {f.scanner_name}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                          f.lifecycle_status === "OPEN"
                            ? "text-red-400 bg-red-500/10 border border-red-500/20"
                            : "text-emerald-400 bg-emerald-500/10 border border-emerald-500/20"
                        }`}
                      >
                        {f.lifecycle_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/findings/${f.id}`}
                        className="text-amber-400 hover:text-amber-300 font-sans font-semibold underline"
                      >
                        Details
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
  );
}
