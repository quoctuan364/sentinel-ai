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
        <h1 className="text-2xl font-bold text-white tracking-tight">Tích Hợp GitHub App</h1>
        <p className="text-sm text-zinc-400 mt-1">
          Cấu hình liên kết webhook GitHub, phân quyền ứng dụng và xác thực chữ ký bảo mật.
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
              <h2 className="text-lg font-bold text-white">Tích Hợp Ứng Dụng GitHub App</h2>
              <p className="text-xs text-zinc-400">Liên kết phân quyền tối thiểu để đánh giá an ninh các Pull Request</p>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            SẴN SÀNG
          </span>
        </div>

        {/* Webhook Configuration Section */}
        <div className="space-y-3 pt-4 border-t border-zinc-800">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
              <Webhook className="w-4 h-4 text-amber-400" />
              <span>Đường Dẫn Tiếp Nhận Webhook Payload</span>
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
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-zinc-700 bg-zinc-800 text-xs font-semibold text-zinc-200 hover:bg-zinc-700 transition-colors cursor-pointer"
            >
              {copiedWebhook ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedWebhook ? "Đã sao chép" : "Sao chép"}</span>
            </button>
          </div>
        </div>

        {/* Required Events Table */}
        <div className="space-y-3 pt-4 border-t border-zinc-800">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-zinc-400">
            Sự Kiện Webhook Cần Đăng Ký
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono text-zinc-300">
            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between">
              <span>Pull request (opened, synchronize)</span>
              <span className="text-emerald-400">Đang bật</span>
            </div>
            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between">
              <span>Push (commit nhánh chính)</span>
              <span className="text-emerald-400">Đang bật</span>
            </div>
          </div>
        </div>

        {/* Security & Verification Box */}
        <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800/80 text-xs space-y-2">
          <div className="flex items-center gap-2 text-amber-400 font-bold font-mono">
            <Lock className="w-3.5 h-3.5" />
            <span>Cơ Chế Xác Thực Mật Mã Chống Tấn Công Phát Lại</span>
          </div>
          <p className="text-zinc-400 leading-relaxed">
            Mọi webhook gửi đến đều được kiểm tra chữ ký HMAC-SHA256 theo thuật toán so sánh thời gian hằng số (<code className="text-amber-400">X-Hub-Signature-256</code>). Lịch sử tiếp nhận được lưu lại qua <code className="text-amber-400">X-GitHub-Delivery</code> để ngăn chặn tấn công phát lại (Replay Attack) và chống trùng lặp dữ liệu.
          </p>
        </div>
      </div>
    </div>
  );
}
