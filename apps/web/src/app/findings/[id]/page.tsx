"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Cpu,
  FileCode,
  History,
  ShieldAlert,
  Terminal,
} from "lucide-react";
import { api, Finding } from "@/lib/api";

export default function FindingDetailPage() {
  const params = useParams();
  const findingId = params.id as string;
  const [finding, setFinding] = useState<Finding | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusComment, setStatusComment] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  const loadFinding = useCallback(() => {
    setLoading(true);
    api.getFindingDetail(findingId)
      .then((data) => setFinding(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [findingId]);

  useEffect(() => {
    if (findingId) {
      loadFinding();
    }
  }, [findingId, loadFinding]);

  const handleUpdateStatus = async (newStatus: "OPEN" | "RESOLVED" | "WONT_FIX") => {
    setIsUpdating(true);
    try {
      await api.updateFindingStatus(findingId, newStatus, statusComment);
      setStatusComment("");
      loadFinding();
    } catch (err: any) {
      alert("Failed to update status: " + err.message);
    } finally {
      setIsUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-4">
        <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <div className="text-zinc-400 font-mono text-sm">Loading finding record...</div>
      </div>
    );
  }

  if (!finding) {
    return (
      <div className="py-12 space-y-4 text-center">
        <div className="text-red-400 font-bold">Finding not found</div>
        <Link href="/findings" className="inline-block text-amber-400 underline text-sm">
          Return to findings
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Top breadcrumb */}
      <div>
        <Link
          href="/findings"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition-colors font-mono"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>BACK TO FINDINGS</span>
        </Link>
      </div>

      {/* Main card */}
      <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-6">
        {/* Title & Metadata */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-6 border-b border-zinc-800">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span
                className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                  finding.severity === "CRITICAL"
                    ? "bg-red-500/20 text-red-400 border border-red-500/40"
                    : finding.severity === "HIGH"
                    ? "bg-orange-500/20 text-orange-400 border border-orange-500/40"
                    : "bg-yellow-500/20 text-yellow-400 border border-yellow-500/40"
                }`}
              >
                {finding.severity}
              </span>
              {finding.cwe_id && (
                <span className="text-xs font-mono text-zinc-400 border border-zinc-800 px-1.5 py-0.5 rounded">
                  {finding.cwe_id}
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{finding.title}</h1>
            <p className="text-xs font-mono text-zinc-500">Fingerprint: {finding.fingerprint}</p>
          </div>

          <div className="flex flex-col items-end gap-1.5 text-xs font-mono text-zinc-400">
            <div>Scanner: <strong className="text-zinc-200">{finding.scanner_name}</strong></div>
            <div>Rule: <strong className="text-zinc-200">{finding.rule_id}</strong></div>
            <div>Confidence: <strong className="text-zinc-200">{finding.confidence}</strong></div>
          </div>
        </div>

        {/* Explanation */}
        <div className="space-y-2">
          <h2 className="text-xs font-bold text-zinc-400 uppercase tracking-wider font-mono">
            Vulnerability Details & Impact
          </h2>
          <p className="text-sm text-zinc-300 leading-relaxed">{finding.message}</p>
        </div>

        {/* Code Excerpt */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-zinc-400 uppercase tracking-wider font-bold">Affected Source Location</span>
            <span className="text-amber-400">{finding.file_path} : Line {finding.start_line}</span>
          </div>
          <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 font-mono text-xs overflow-x-auto text-zinc-300">
            {finding.code_snippet || "No source preview available."}
          </div>
        </div>

        {/* AI Triage & Patch */}
        {finding.ai_explanation && (
          <div className="p-5 rounded-xl border border-amber-500/30 bg-gradient-to-r from-amber-950/20 to-zinc-950 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-amber-400 font-mono uppercase tracking-wider">
              <Cpu className="w-4 h-4" />
              <span>AI Triage Analysis & Remediation</span>
            </div>
            <p className="text-xs text-zinc-300 leading-relaxed">{finding.ai_explanation}</p>
            {finding.ai_suggested_patch && (
              <div className="space-y-1.5">
                <div className="text-[11px] font-mono text-zinc-400">Recommended Code Patch:</div>
                <pre className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-emerald-400 font-mono text-xs overflow-x-auto">
                  {finding.ai_suggested_patch}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Lifecycle Management Controls */}
        <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-950 space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Analyst Lifecycle Management
          </h3>

          <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
            <span>Current State:</span>
            <span className="px-2 py-0.5 rounded font-bold text-white bg-zinc-800">
              {finding.lifecycle_status}
            </span>
          </div>

          <textarea
            placeholder="Add analyst note or rationale for status change..."
            value={statusComment}
            onChange={(e) => setStatusComment(e.target.value)}
            rows={2}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-xs text-zinc-200 placeholder-zinc-500 font-mono focus:outline-none focus:border-amber-500"
          />

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => handleUpdateStatus("RESOLVED")}
              disabled={isUpdating || finding.lifecycle_status === "RESOLVED"}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors disabled:opacity-40"
            >
              Mark as Resolved
            </button>

            <button
              onClick={() => handleUpdateStatus("WONT_FIX")}
              disabled={isUpdating || finding.lifecycle_status === "WONT_FIX"}
              className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-bold transition-colors disabled:opacity-40"
            >
              Mark as Won&apos;t Fix (Risk Accepted)
            </button>

            <button
              onClick={() => handleUpdateStatus("OPEN")}
              disabled={isUpdating || finding.lifecycle_status === "OPEN"}
              className="px-4 py-2 rounded-lg bg-red-900/60 hover:bg-red-800 text-red-200 text-xs font-bold transition-colors disabled:opacity-40"
            >
              Reopen Finding
            </button>
          </div>
        </div>

        {/* Audit History */}
        {finding.audits && finding.audits.length > 0 && (
          <div className="space-y-3 pt-4 border-t border-zinc-800">
            <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider font-mono flex items-center gap-1.5">
              <History className="w-3.5 h-3.5 text-zinc-400" />
              <span>Analyst Audit Log</span>
            </h3>
            <div className="space-y-2">
              {finding.audits.map((a) => (
                <div key={a.id} className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs space-y-1 font-mono">
                  <div className="flex items-center justify-between text-zinc-500">
                    <span>Transition: {a.old_status} &rarr; <strong className="text-zinc-200">{a.new_status}</strong></span>
                    <span>{new Date(a.created_at).toLocaleString()}</span>
                  </div>
                  {a.comment && <p className="text-zinc-300 font-sans text-xs">{a.comment}</p>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
