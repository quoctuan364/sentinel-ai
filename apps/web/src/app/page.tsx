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
          <span>NỀN TẢNG BẢO MẬT MÃ NGUỒN CHUẨN DOANH NGHIỆP</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Phân Tích Bảo Mật Tất Định Kết Hợp <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-orange-500 to-amber-600">AI Triage Kiểm Chứng</span>
        </h1>

        <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
          Sentinel AI tự động phân tích GitHub Pull Request, phát hiện lỗ hổng bằng công cụ bảo mật tất định và xác thực bằng chứng qua mô hình AI an toàn, chống ảo giác.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <button
            onClick={handleRunDemoScan}
            disabled={isScanning}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-slate-950 font-bold hover:brightness-110 active:scale-95 transition-all shadow-lg shadow-orange-500/25 disabled:opacity-50 cursor-pointer"
          >
            {isScanning ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Đang Quét Mã Nguồn...</span>
              </>
            ) : (
              <>
                <Terminal className="w-4 h-4 text-slate-950" />
                <span>Chạy Thử Nghiệm Quét Lỗ Hổng</span>
              </>
            )}
          </button>

          <Link
            href="/dashboard"
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-zinc-700 bg-zinc-800/70 hover:bg-zinc-800 text-zinc-200 font-semibold transition-colors"
          >
            <span>Mở Bảng Điều Khiển</span>
            <ArrowRight className="w-4 h-4 text-zinc-400" />
          </Link>
        </div>

        {scanResult && (
          <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-sm flex items-center justify-center gap-2 animate-fade-in font-mono">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Quét hoàn tất lượt #{scanResult.id.substring(0, 8)}! Đang chuyển đến báo cáo...</span>
          </div>
        )}
      </section>

      {/* Security Architecture & Workflow */}
      <section className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">Quy Trình Hoạt Động Của Sentinel AI</h2>
          <p className="text-sm text-zinc-400">Quy trình nghiêm ngặt phân tách rõ ràng giữa phát hiện tất định và thẩm định AI có kiểm soát.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-amber-400">
              <GitPullRequest className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">1. Tiếp Nhận Webhook PR</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              GitHub App gửi webhook kèm chữ ký HMAC SHA-256. Lớp Idempotency chống trùng lặp và đưa lệnh quét vào hàng đợi an toàn.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-orange-400">
              <FileCode className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">2. Bộ Quét Tĩnh Tất Định</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Phân tích AST mã nguồn và chuỗi mẫu (CWE-89, CWE-78, CWE-502, CWE-798) không phán đoán bừa bãi. Xuất định dạng chuẩn SARIF 2.1.0.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-yellow-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">3. Bounded AI Triage</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Xử lý mã nguồn như dữ liệu không tin cậy với ranh giới chống Prompt Injection. Đánh giá dương tính giả và tạo bản vá đề xuất.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-emerald-400">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white">4. Báo Cáo & Nhật Ký Kiểm Toán</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Hiển thị danh sách lỗ hổng kèm đoạn code vi phạm, lịch sử kiểm toán và xuất báo cáo GitHub Check Run theo chế độ cấu hình.
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
            <h2 className="text-xl font-bold text-white">Kiến Trúc An Ninh Mặc Định (Secure-by-Default)</h2>
            <p className="text-xs text-zinc-400">Được thiết kế dựa trên nguyên tắc mọi đoạn mã đầu vào đều có thể là mã độc.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-zinc-300">
          <div className="space-y-2 border-l-2 border-amber-500/50 pl-4">
            <h4 className="font-semibold text-white">Chống Tấn Công Prompt Injection</h4>
            <p className="text-xs text-zinc-400">
              Nội dung PR được bọc kín trong thẻ phân tách (<code className="text-amber-400">{"<<<UNTRUSTED_CONTENT>>>"}</code>). Lược đồ Pydantic nghiêm ngặt từ chối lệnh can thiệp.
            </p>
          </div>
          <div className="space-y-2 border-l-2 border-amber-500/50 pl-4">
            <h4 className="font-semibold text-white">Không Thực Thi Mã Độc Tùy Tiện</h4>
            <p className="text-xs text-zinc-400">
              Các bộ quét chạy phân tích cú pháp AST tĩnh và biểu thức chính quy. Hệ thống không bao giờ chạy file thực thi hoặc script từ PR.
            </p>
          </div>
          <div className="space-y-2 border-l-2 border-amber-500/50 pl-4">
            <h4 className="font-semibold text-white">Cô Lập Không Gian Làm Việc (Multi-Tenant)</h4>
            <p className="text-xs text-zinc-400">
              Mọi lượt quét, phát hiện, token và nhật ký kiểm toán đều được phân tách nghiêm ngặt theo ID không gian làm việc (Workspace) ở cả tầng SQL lẫn Service.
            </p>
          </div>
        </div>
      </section>

      {/* Self-Hosting & Quickstart */}
      <section className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white">Triển Khai Cục Bộ & Máy Chủ</h2>
          <p className="text-sm text-zinc-400">Ngăn xếp hoàn chỉnh với Docker Compose: PostgreSQL, Redis, Prometheus, FastAPI và Next.js.</p>
        </div>

        <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-950 font-mono text-sm text-zinc-300 space-y-4">
          <div className="flex items-center justify-between text-xs text-zinc-500 border-b border-zinc-800 pb-2">
            <span>Terminal</span>
            <span>docker compose up</span>
          </div>
          <pre className="text-amber-400 overflow-x-auto text-xs leading-relaxed">
{`# 1. Clone mã nguồn
git clone https://github.com/quoctuan364/sentinel-ai.git
cd sentinel-ai

# 2. Cấu hình biến môi trường
cp .env.example .env

# 3. Khởi chạy toàn bộ hệ thống
docker compose up -d

# 4. Truy cập Sentinel AI
# Frontend: http://localhost:3001
# API Docs: http://localhost:8000/api/v1/docs
# Metrics:  http://localhost:8000/api/v1/metrics`}
          </pre>
        </div>
      </section>
    </div>
  );
}
