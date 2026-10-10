export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ScanJob {
  id: string;
  workspace_id: string;
  repository_id: string;
  pr_number: number | null;
  commit_sha: string;
  branch_name: string;
  base_branch: string;
  title: string;
  trigger: string;
  status: "PENDING" | "QUEUED" | "RUNNING" | "SUCCEEDED" | "PARTIAL" | "FAILED" | "CANCELLED";
  retry_count: number;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  error_message: string | null;
  ai_triage_enabled: boolean;
  ai_summary: {
    executive_summary?: string;
    risk_assessment?: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "CLEAN";
    key_vulnerabilities_highlighted?: string[];
  } | null;
  created_at: string;
  findings_count?: number;
  findings?: Finding[];
  sarif_report?: any;
}

export interface Finding {
  id: string;
  scan_id: string;
  workspace_id: string;
  repository_id: string;
  fingerprint: string;
  scanner_name: string;
  rule_id: string;
  title: string;
  message: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFORMATIONAL";
  confidence: "HIGH" | "MEDIUM" | "LOW";
  cwe_id: string | null;
  file_path: string;
  start_line: number;
  end_line: number;
  code_snippet: string | null;
  remediation_guidance: string | null;
  validation_status: "CONFIRMED" | "FALSE_POSITIVE" | "SUPPRESSED";
  lifecycle_status: "OPEN" | "RESOLVED" | "WONT_FIX";
  ai_explanation: string | null;
  ai_suggested_patch: string | null;
  first_seen_at: string;
  last_seen_at: string;
  created_at: string;
  audits?: Array<{
    id: string;
    old_status: string;
    new_status: string;
    comment: string | null;
    created_at: string;
  }>;
}

export interface Repository {
  id: string;
  workspace_id: string;
  full_name: string;
  default_branch: string;
  is_active: boolean;
  scan_on_pr: boolean;
  min_severity_for_review: string;
  created_at: string;
}

export interface WorkspaceStats {
  workspace_id: string;
  name: string;
  total_scans: number;
  total_ai_tokens: number;
  ai_monthly_budget_cents: number;
  ai_used_cents: number;
  review_mode: string;
}

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  let token: string | null = null;
  if (typeof window !== "undefined") {
    token = localStorage.getItem("sentinel_token");
  }

  const authHeaders: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...options?.headers,
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let errorMsg = `Lỗi API [${res.status}]`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || JSON.stringify(errJson);
    } catch {
      const errorText = await res.text();
      if (errorText) errorMsg = errorText;
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  getHealth: () => fetchJson<{ status: string; service: string }>("/healthz"),
  getReadiness: () => fetchJson<{ status: string; database: string }>("/ready"),
  
  // Workspaces
  getWorkspaceStats: () => fetchJson<WorkspaceStats>("/workspaces/current/stats"),
  getWorkspaceMembers: () => fetchJson<any[]>("/workspaces/current/members"),
  updateWorkspace: (data: any) =>
    fetchJson<any>("/workspaces/current", { method: "PATCH", body: JSON.stringify(data) }),

  // Repositories
  getRepositories: () => fetchJson<Repository[]>("/repositories"),
  createRepository: (data: { full_name: string; default_branch?: string }) =>
    fetchJson<Repository>("/repositories", { method: "POST", body: JSON.stringify(data) }),
  getRepository: (id: string) => fetchJson<Repository>(`/repositories/${id}`),

  // Scans
  getScans: (repoId?: string) =>
    fetchJson<ScanJob[]>(repoId ? `/scans?repository_id=${repoId}` : "/scans"),
  getScanDetail: (id: string) => fetchJson<ScanJob>(`/scans/${id}`),
  triggerScan: (data: {
    repository_id: string;
    commit_sha: string;
    branch_name?: string;
    title?: string;
    pr_number?: number;
    ai_triage?: boolean;
    local_path?: string;
  }) => fetchJson<ScanJob>("/scans", { method: "POST", body: JSON.stringify(data) }),
  cancelScan: (id: string) =>
    fetchJson<ScanJob>(`/scans/${id}/cancel`, { method: "POST" }),
  getScanSarif: (id: string) => fetchJson<any>(`/scans/${id}/sarif`),

  // Findings
  getFindings: (params?: { severity?: string; status?: string; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.severity) query.append("severity", params.severity);
    if (params?.status) query.append("lifecycle_status", params.status);
    if (params?.search) query.append("search", params.search);
    const qs = query.toString() ? `?${query.toString()}` : "";
    return fetchJson<Finding[]>(`/findings${qs}`);
  },
  getFindingDetail: (id: string) => fetchJson<Finding>(`/findings/${id}`),
  updateFindingStatus: (id: string, lifecycle_status: string, comment?: string) =>
    fetchJson<Finding>(`/findings/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ lifecycle_status, comment }),
    }),

  // Audit & Deliveries
  getAuditEvents: () => fetchJson<any[]>("/audit/events"),
  getWebhookDeliveries: () => fetchJson<any[]>("/audit/deliveries"),
};
