"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  Cpu,
  KeyRound,
  Lock,
  Save,
  ShieldAlert,
  Sliders,
  Users,
} from "lucide-react";
import { api, WorkspaceStats } from "@/lib/api";

export default function SettingsPage() {
  const [stats, setStats] = useState<WorkspaceStats | null>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [reviewMode, setReviewMode] = useState("ADVISORY");
  const [budgetCents, setBudgetCents] = useState(5000);
  const [workspaceName, setWorkspaceName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    api.getWorkspaceStats().then((data) => {
      setStats(data);
      setReviewMode(data.review_mode);
      setBudgetCents(data.ai_monthly_budget_cents);
      setWorkspaceName(data.name);
    });
    api.getWorkspaceMembers().then((data) => setMembers(data));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await api.updateWorkspace({
        name: workspaceName,
        review_mode: reviewMode,
        ai_monthly_budget_cents: budgetCents,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert("Failed to update settings: " + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Cài Đặt & Quản Trị Hệ Thống</h1>
        <p className="text-sm text-zinc-400 mt-1">
          Cấu hình chính sách kiểm duyệt an ninh, hạn mức chi phí AI hàng tháng, chế độ đánh giá và phân quyền thành viên.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* General Settings */}
        <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-6">
          <div className="flex items-center gap-2 pb-4 border-b border-zinc-800">
            <Sliders className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-white">Chế Độ Đánh Giá & Chính Sách</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1">
                Tên Không Gian Làm Việc
              </label>
              <input
                type="text"
                value={workspaceName}
                onChange={(e) => setWorkspaceName(e.target.value)}
                className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 font-sans focus:outline-none focus:border-amber-500"
              />
            </div>

            {/* Review Mode Radio */}
            <div className="space-y-2">
              <label className="block text-xs font-mono text-zinc-400">
                Chế Độ Đánh Giá Pull Request
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <label
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    reviewMode === "ADVISORY"
                      ? "border-amber-500 bg-amber-500/10"
                      : "border-zinc-800 bg-zinc-950 hover:bg-zinc-900"
                  }`}
                >
                  <input
                    type="radio"
                    name="review_mode"
                    value="ADVISORY"
                    checked={reviewMode === "ADVISORY"}
                    onChange={(e) => setReviewMode(e.target.value)}
                    className="sr-only"
                  />
                  <div className="font-bold text-sm text-white">Chế Độ Tư Vấn (Advisory - Mặc định)</div>
                  <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                    Tạo báo cáo kiểm tra an ninh nội bộ trên giao diện, không tự ý bình luận công khai lên PR GitHub.
                  </p>
                </label>

                <label
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    reviewMode === "REVIEW"
                      ? "border-amber-500 bg-amber-500/10"
                      : "border-zinc-800 bg-zinc-950 hover:bg-zinc-900"
                  }`}
                >
                  <input
                    type="radio"
                    name="review_mode"
                    value="REVIEW"
                    checked={reviewMode === "REVIEW"}
                    onChange={(e) => setReviewMode(e.target.value)}
                    className="sr-only"
                  />
                  <div className="font-bold text-sm text-white">Chế Độ Kiểm Duyệt Trực Tiếp (Review Mode)</div>
                  <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
                    Tự động tạo nhận xét, đánh giá và gắn cờ cảnh báo trực tiếp trên GitHub PR khi phát hiện lỗ hổng nghiêm trọng.
                  </p>
                </label>
              </div>
            </div>

            {/* AI Budget */}
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1">
                Hạn Mức Chi Phí Token AI Hàng Tháng (USD)
              </label>
              <div className="flex items-center gap-2 max-w-xs">
                <span className="text-zinc-400 font-mono text-sm">$</span>
                <input
                  type="number"
                  value={budgetCents / 100}
                  onChange={(e) => setBudgetCents(Math.round(parseFloat(e.target.value || "0") * 100))}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 font-mono focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
            {saveSuccess ? (
              <span className="text-xs text-emerald-400 font-mono flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>Đã lưu cài đặt thành công</span>
              </span>
            ) : <span />}

            <button
              type="submit"
              disabled={isSaving}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-colors disabled:opacity-50 cursor-pointer"
            >
              <Save className="w-4 h-4" />
              <span>{isSaving ? "Đang lưu..." : "Lưu Thay Đổi Chính Sách"}</span>
            </button>
          </div>
        </div>
      </form>

      {/* RBAC Team Members Section */}
      <div className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40 space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-white">Danh Sách Thành Viên & Phân Quyền (RBAC)</h2>
          </div>
          <span className="text-xs text-zinc-500 font-mono">{members.length} thành viên</span>
        </div>

        <div className="divide-y divide-zinc-800/60 font-mono text-xs">
          {members.map((m) => (
            <div key={m.id} className="py-3 flex items-center justify-between">
              <div>
                <div className="font-semibold text-zinc-200">{m.user?.full_name || "Chuyên viên phân tích"}</div>
                <div className="text-zinc-500">{m.user?.email || "analyst@sentinel.ai"}</div>
              </div>
              <span className="px-2 py-0.5 rounded font-bold bg-zinc-800 text-amber-400">
                {m.role === "OWNER" ? "QUẢN TRỊ VIÊN (OWNER)" : m.role}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
