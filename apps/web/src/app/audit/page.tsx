"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  Clock,
  History,
  RefreshCw,
  ShieldCheck,
  Webhook,
  XCircle,
} from "lucide-react";
import { api } from "@/lib/api";

export default function AuditLogsPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [deliveries, setDeliveries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"events" | "deliveries">("events");

  const loadData = async () => {
    setLoading(true);
    try {
      const [eventsData, deliveriesData] = await Promise.all([
        api.getAuditEvents(),
        api.getWebhookDeliveries(),
      ]);
      setEvents(eventsData);
      setDeliveries(deliveriesData);
    } catch (err: any) {
      console.error("Failed to load audit records:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Lịch Sử Kiểm Toán & Tích Hợp</h1>
          <p className="text-sm text-zinc-400 mt-1">
            Nhật ký bất biến ghi nhận mọi hành động an ninh, lệnh quét và sự kiện webhook tiếp nhận.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="p-2.5 rounded-lg border border-zinc-800 bg-zinc-900/60 text-zinc-300 hover:bg-zinc-800 transition-colors self-start sm:self-auto cursor-pointer"
          title="Làm mới dữ liệu kiểm toán"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-zinc-800 text-xs font-mono">
        <button
          onClick={() => setActiveTab("events")}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 font-medium transition-colors cursor-pointer ${
            activeTab === "events"
              ? "border-amber-500 text-amber-400 bg-amber-500/5"
              : "border-transparent text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <History className="w-4 h-4" />
          <span>Nhật Ký An Ninh ({events.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("deliveries")}
          className={`flex items-center gap-2 px-4 py-2.5 border-b-2 font-medium transition-colors cursor-pointer ${
            activeTab === "deliveries"
              ? "border-amber-500 text-amber-400 bg-amber-500/5"
              : "border-transparent text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <Webhook className="w-4 h-4" />
          <span>Sự Kiện Webhook ({deliveries.length})</span>
        </button>
      </div>

      {/* Content */}
      <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/30">
        {loading ? (
          <div className="p-16 text-center">
            <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <span className="text-zinc-500 font-mono text-xs">Đang tải dữ liệu kiểm toán...</span>
          </div>
        ) : activeTab === "events" ? (
          events.length === 0 ? (
            <div className="p-16 text-center text-zinc-500 text-sm">
              Chưa có sự kiện kiểm toán nào được ghi lại.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-zinc-950/60 border-b border-zinc-800 text-xs font-mono text-zinc-400 uppercase">
                  <tr>
                    <th className="px-4 py-3">Thời gian</th>
                    <th className="px-4 py-3">Hành động</th>
                    <th className="px-4 py-3">Tài nguyên</th>
                    <th className="px-4 py-3">Chi tiết</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60 font-mono text-xs">
                  {events.map((e) => (
                    <tr key={e.id} className="hover:bg-zinc-800/30 transition-colors">
                      <td className="px-4 py-3 text-zinc-400">
                        {new Date(e.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 font-semibold text-amber-400">
                        {e.action}
                      </td>
                      <td className="px-4 py-3 text-zinc-300">
                        {e.resource_type} {e.resource_id ? `(${e.resource_id.substring(0, 8)})` : ""}
                      </td>
                      <td className="px-4 py-3 text-zinc-400">
                        <pre className="text-[11px] truncate max-w-md">
                          {JSON.stringify(e.details)}
                        </pre>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : deliveries.length === 0 ? (
          <div className="p-16 text-center text-zinc-500 text-sm">
            Chưa có webhook nào được tiếp nhận.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-zinc-950/60 border-b border-zinc-800 text-xs font-mono text-zinc-400 uppercase">
                <tr>
                  <th className="px-4 py-3">Mã Giao Nhận</th>
                  <th className="px-4 py-3">Loại Sự Kiện</th>
                  <th className="px-4 py-3">Trạng thái</th>
                  <th className="px-4 py-3">Thời gian nhận</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60 font-mono text-xs">
                {deliveries.map((d) => (
                  <tr key={d.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-zinc-300">
                      {d.delivery_id}
                    </td>
                    <td className="px-4 py-3 text-zinc-200">
                      {d.event_type}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                          d.status === "PROCESSED"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : d.status === "IGNORED"
                            ? "bg-zinc-800 text-zinc-400"
                            : "bg-red-500/10 text-red-400 border border-red-500/20"
                        }`}
                      >
                        {d.status === "PROCESSED" ? "ĐÃ XỬ LÝ" : d.status === "IGNORED" ? "BỎ QUA" : d.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-zinc-400">
                      {new Date(d.created_at).toLocaleString()}
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
