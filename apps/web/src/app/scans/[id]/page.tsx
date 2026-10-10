"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Cpu,
  Download,
  FileCode,
  GitCommit,
  GitPullRequest,
  ShieldAlert,
  Terminal,
} from "lucide-react";
import { api, Finding, ScanJob } from "@/lib/api";

export default function ScanDetailPage() {
  const params = useParams();
  const scanId = params.id as string;
  const [scan, setScan] = useState<ScanJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (scanId) {
      api.getScanDetail(scanId)
        .then((data) => setScan(data))
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [scanId]);

  const handleDownloadSarif = async () => {
    try {
      const sarif = await api.getScanSarif(scanId);
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(sarif, null, 2));
      const downloadAnchor = document.createElement("a");
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `sentinel-sarif-${scanId.substring(0, 8)}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch (err: any) {
      alert("Failed to download SARIF: " + err.message);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <div className="text-zinc-400 font-mono text-sm">Loading security review results...</div>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div className="py-12 space-y-4 text-center">
        <div className="text-red-400 font-bold">Failed to load scan details</div>
        <div className="text-zinc-500 text-sm font-mono">{error}</div>
        <Link href="/dashboard" className="inline-block text-amber-400 underline text-sm">
          Return to dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header & Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-800">
        <div className="space-y-2">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition-colors font-mono"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>BACK TO SCANS</span>
          </Link>
          <h1 className="text-2xl font-bold text-white tracking-tight">{scan.title}</h1>
          <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-zinc-400">
            <span className="flex items-center gap-1">
              <GitPullRequest className="w-3.5 h-3.5 text-zinc-500" />
              <span>{scan.branch_name} &rarr; {scan.base_branch}</span>
            </span>
            <span>&bull;</span>
            <span className="flex items-center gap-1">
              <GitCommit className="w-3.5 h-3.5 text-zinc-500" />
              <span>{scan.commit_sha.substring(0, 8)}</span>
            </span>
            <span>&bull;</span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-zinc-500" />
              <span>{scan.duration_seconds ?? 0}s execution</span>
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadSarif}
            className="flex items-center gap-2 px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-800/80 hover:bg-zinc-800 text-xs text-zinc-200 font-semibold transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-zinc-400" />
            <span>Export SARIF 2.1.0</span>
          </button>

          <span
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold ${
              scan.status === "SUCCEEDED"
                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
            }`}
          >
            {scan.status}
          </span>
        </div>
      </div>

      {/* AI Executive Summary Card */}
      {scan.ai_summary && (
        <div className="p-6 rounded-xl border border-amber-500/30 bg-gradient-to-r from-amber-950/20 via-zinc-900/60 to-zinc-950/80 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-amber-400" />
              <h2 className="text-base font-bold text-white">AI Security Triage & Executive Assessment</h2>
            </div>
            <span
              className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                scan.ai_summary.risk_assessment === "CRITICAL"
                  ? "bg-red-500/20 text-red-400 border border-red-500/40"
                  : scan.ai_summary.risk_assessment === "HIGH"
                  ? "bg-orange-500/20 text-orange-400 border border-orange-500/40"
                  : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
              }`}
            >
              RISK: {scan.ai_summary.risk_assessment}
            </span>
          </div>

          <p className="text-sm text-zinc-300 leading-relaxed">
            {scan.ai_summary.executive_summary}
          </p>

          {scan.ai_summary.key_vulnerabilities_highlighted && scan.ai_summary.key_vulnerabilities_highlighted.length > 0 && (
            <div className="space-y-1.5 pt-2 border-t border-zinc-800">
              <div className="text-xs font-mono text-zinc-400 uppercase">Key Identified Risk Vectors:</div>
              <ul className="text-xs text-zinc-300 list-disc list-inside space-y-1">
                {scan.ai_summary.key_vulnerabilities_highlighted.map((vuln, idx) => (
                  <li key={idx} className="text-amber-300">{vuln}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Findings List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Deterministic Security Findings ({scan.findings?.length ?? 0})</span>
          </h2>
          <span className="text-xs text-zinc-500 font-mono">Deduplicated by cryptographic fingerprint</span>
        </div>

        {(!scan.findings || scan.findings.length === 0) ? (
          <div className="p-12 text-center text-zinc-500 text-sm border border-zinc-800 rounded-xl bg-zinc-900/30">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            No vulnerabilities detected across scanned files. Clean security posture.
          </div>
        ) : (
          <div className="space-y-4">
            {scan.findings.map((f) => (
              <div
                key={f.id}
                className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:border-zinc-700 transition-colors space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
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
                    <h3 className="font-bold text-white text-base">{f.title}</h3>
                    {f.cwe_id && (
                      <span className="text-xs font-mono text-zinc-400 border border-zinc-800 px-1.5 py-0.5 rounded">
                        {f.cwe_id}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
                    <span className="px-2 py-0.5 bg-zinc-800 rounded">{f.scanner_name}</span>
                    <span>&bull;</span>
                    <span>Rule: {f.rule_id}</span>
                  </div>
                </div>

                <p className="text-xs text-zinc-300 leading-relaxed">{f.message}</p>

                {/* File & Code snippet */}
                <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 font-mono text-xs space-y-2">
                  <div className="text-zinc-500 flex items-center justify-between border-b border-zinc-800/60 pb-1.5">
                    <span className="text-amber-400">{f.file_path}</span>
                    <span>Line {f.start_line}</span>
                  </div>
                  {f.code_snippet && (
                    <pre className="text-zinc-300 overflow-x-auto py-1">
                      {f.code_snippet}
                    </pre>
                  )}
                </div>

                {/* AI Explanation & Patch */}
                {f.ai_explanation && (
                  <div className="p-4 rounded-lg bg-zinc-950/70 border border-amber-500/20 space-y-3">
                    <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
                      <Cpu className="w-3.5 h-3.5" />
                      <span>AI Triage Analysis & Remediation</span>
                    </div>
                    <p className="text-xs text-zinc-300 leading-relaxed">{f.ai_explanation}</p>
                    {f.ai_suggested_patch && (
                      <div className="space-y-1">
                        <div className="text-[11px] font-mono text-zinc-500">Recommended Code Patch:</div>
                        <pre className="p-3 rounded bg-zinc-900 border border-zinc-800 text-emerald-400 font-mono text-xs overflow-x-auto">
                          {f.ai_suggested_patch}
                        </pre>
                      </div>
                    )}
                  </div>
                )}

                <div className="flex items-center justify-between text-xs text-zinc-500 font-mono pt-2 border-t border-zinc-800/60">
                  <span>Lifecycle: <strong className="text-zinc-300">{f.lifecycle_status}</strong></span>
                  <Link
                    href={`/findings/${f.id}`}
                    className="text-amber-400 hover:text-amber-300 font-sans font-semibold underline"
                  >
                    Manage Finding Lifecycle &rarr;
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
