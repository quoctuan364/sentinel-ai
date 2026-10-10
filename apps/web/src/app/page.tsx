"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ShieldAlert,
  Terminal,
  Cpu,
  ArrowRight,
  Lock,
  GitPullRequest,
  CheckCircle2,
  FileCode,
  Zap,
  Server,
  Database,
  ExternalLink,
} from "lucide-react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter();
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);

  const handleRunDemoScan = async () => {
    setIsScanning(true);
    try {
      const scan = await api.triggerScan({
        repository_id: "default-fixture-repo",
        commit_sha: "c0ffeebabe123456",
        branch_name: "feature/auth-and-payments",
        title: "Test Pull Request: Security Audit Demo",
        ai_triage: true,
        local_path: "./fixtures/vulnerable-repo",
      });
      setScanResult(scan);
      setTimeout(() => {
        router.push(`/scans/${scan.id}`);
      }, 1200);
    } catch (err: any) {
      alert("Scan failed: " + err.message);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="space-y-24 py-6">
      {/* Hero Section */}
      <section className="relative text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-400 text-xs font-mono font-medium">
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span>PRODUCTION-READY CODE SECURITY PLATFORM</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Deterministic Security Analysis Meets <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-orange-500 to-amber-600">Bounded AI Triage</span>
        </h1>

        <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
          Sentinel AI analyzes GitHub Pull Requests, detects vulnerabilities with deterministic security tools (Bandit, Detect-secrets, Semgrep), and validates findings with evidence-grounded AI reviews.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <button
            onClick={handleRunDemoScan}
            disabled={isScanning}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold hover:brightness-110 active:scale-95 transition-all shadow-lg shadow-orange-500/25 disabled:opacity-50"
          >
            {isScanning ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Scanning Fixtures...</span>
              </>
            ) : (
              <>
                <Terminal className="w-4 h-4 text-slate-950" />
                <span>Launch Interactive Test Scan</span>
              </>
            )}
          </button>

          <Link
            href="/dashboard"
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-zinc-700 bg-zinc-800/70 hover:bg-zinc-800 text-zinc-200 font-semibold transition-colors"
          >
            <span>Open Security Dashboard</span>
            <ArrowRight className="w-4 h-4 text-zinc-400" />
          </Link>
        </div>

        {scanResult && (
          <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-sm flex items-center justify-center gap-2 animate-fade-in font-mono">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Scan #{scanResult.id.substring(0, 8)} completed! Redirecting to report...</span>
          </div>
        )}
      </section>

      {/* Security Architecture & Workflow */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">How Sentinel AI Works</h2>
          <p className="text-sm text-zinc-400">Strict pipeline separating deterministic detection from bounded AI reasoning.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-amber-400">
              <GitPullRequest className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">1. Ingest PR Webhook</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              GitHub App delivers webhook with HMAC SHA-256 signature. Idempotency layer deduplicates deliveries and enqueues scan job.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-orange-400">
              <FileCode className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">2. Deterministic Scanners</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Analyzes Python AST & text patterns (CWE-89, CWE-78, CWE-502, CWE-798) with zero false-fabrication. Exports standardized SARIF 2.1.0.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-yellow-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">3. Bounded AI Triage</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Treats code as untrusted input with prompt-injection boundaries. Triages scanner findings, evaluates false positives, and generates concrete remediation patches.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-emerald-400">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">4. Evidence-Based Report</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Renders interactive findings explorer with code snippets, audit trail, and opt-in GitHub review publication in advisory or review mode.
            </p>
          </div>
        </div>
      </section>

      {/* Defense & Privacy Model */}
      <section className="p-8 rounded-2xl border border-zinc-800 bg-gradient-to-b from-zinc-900/60 to-zinc-950/80 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <Lock className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Secure-by-Default Architecture</h2>
            <p className="text-xs text-zinc-400">Designed under the premise that all reviewed code is potentially hostile.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-zinc-300">
          <div className="space-y-2 border-l-2 border-amber-500/50 pl-4">
            <h4 className="font-semibold text-white">Anti-Prompt Injection</h4>
            <p className="text-xs text-zinc-400">
              Diffs and comments are strictly isolated inside fenced delimiters (<code className="text-amber-400">{"<<<UNTRUSTED_CONTENT>>>"}</code>). Strict Pydantic schemas reject hallucinated or command payloads.
            </p>
          </div>
          <div className="space-y-2 border-l-2 border-amber-500/50 pl-4">
            <h4 className="font-semibold text-white">Zero Arbitrary Execution</h4>
            <p className="text-xs text-zinc-400">
              Scanners run with static AST & pattern parsing. The host environment never executes build scripts or tests from incoming pull requests.
            </p>
          </div>
          <div className="space-y-2 border-l-2 border-amber-500/50 pl-4">
            <h4 className="font-semibold text-white">Multi-Tenant Isolation</h4>
            <p className="text-xs text-zinc-400">
              All scans, findings, tokens, and audit records are bound to workspace boundaries and enforced at both SQL query and service layers.
            </p>
          </div>
        </div>
      </section>

      {/* Self-Hosting & Quickstart */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white">Self-Host in Minutes</h2>
          <p className="text-sm text-zinc-400">Complete Docker Compose stack with PostgreSQL, Redis, Prometheus, and Next.js frontend.</p>
        </div>

        <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-950 font-mono text-sm text-zinc-300 space-y-4">
          <div className="flex items-center justify-between text-xs text-zinc-500 border-b border-zinc-800 pb-2">
            <span>Terminal</span>
            <span>docker compose up</span>
          </div>
          <pre className="text-amber-400 overflow-x-auto text-xs leading-relaxed">
{`# 1. Clone repository
git clone https://github.com/sentinel-ai/sentinel.git
cd sentinel

# 2. Configure environment (works out of the box with safe defaults)
cp .env.example .env

# 3. Spin up full production-grade stack
docker compose up -d

# 4. Open Sentinel AI
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/v1/docs
# Metrics:  http://localhost:8000/api/v1/metrics`}
          </pre>
        </div>
      </section>
    </div>
  );
}
