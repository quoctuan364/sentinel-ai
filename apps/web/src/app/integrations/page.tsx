"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Copy,
  ExternalLink,
  Github,
  KeyRound,
  Lock,
  RefreshCw,
  ShieldCheck,
  Webhook,
} from "lucide-react";

export default function IntegrationsPage() {
  const [copiedWebhook, setCopiedWebhook] = useState(false);
  const webhookUrl = "http://localhost:8000/api/v1/webhooks/github";

  const copyToClipboard = () => {
    navigator.clipboard.writeText(webhookUrl);
    setCopiedWebhook(true);
    setTimeout(() => setCopiedWebhook(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">GitHub App & Integrations</h1>
        <p className="text-sm text-zinc-400 mt-1">
          Configure GitHub webhook subscriptions, App permissions, and secret verification.
        </p>
      </div>

      {/* GitHub App Connection Card */}
      <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-zinc-800 flex items-center justify-center text-white">
              <Github className="w-7 h-7" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">GitHub App Integration</h2>
              <p className="text-xs text-zinc-400">Least-privilege integration for pull request security reviews</p>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            HEALTHY
          </span>
        </div>

        {/* Webhook Configuration Section */}
        <div className="space-y-3 pt-4 border-t border-zinc-800">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
              <Webhook className="w-4 h-4 text-amber-400" />
              <span>Webhook Payload URL</span>
            </h3>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={webhookUrl}
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs font-mono text-zinc-300 select-all"
            />
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-800 text-xs font-semibold text-zinc-200 hover:bg-zinc-700 transition-colors"
            >
              {copiedWebhook ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedWebhook ? "Copied" : "Copy"}</span>
            </button>
          </div>
        </div>

        {/* Required Events Table */}
        <div className="space-y-3 pt-4 border-t border-zinc-800">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-400">
            Subscribed Webhook Events
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono text-zinc-300">
            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between">
              <span>Pull request (opened, synchronize)</span>
              <span className="text-emerald-400">Active</span>
            </div>
            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between">
              <span>Push (default branch commits)</span>
              <span className="text-emerald-400">Active</span>
            </div>
          </div>
        </div>

        {/* Security & Verification Box */}
        <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800/80 text-xs space-y-2">
          <div className="flex items-center gap-2 text-amber-400 font-bold font-mono">
            <Lock className="w-3.5 h-3.5" />
            <span>Cryptographic Verification Guarantee</span>
          </div>
          <p className="text-zinc-400 leading-relaxed">
            All incoming webhooks are validated using HMAC-SHA256 constant-time comparison (<code className="text-amber-400">X-Hub-Signature-256</code>). Deliveries are tracked by <code className="text-amber-400">X-GitHub-Delivery</code> for replay-attack prevention and idempotency.
          </p>
        </div>
      </div>
    </div>
  );
}
