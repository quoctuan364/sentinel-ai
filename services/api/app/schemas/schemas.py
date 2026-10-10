from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Auth & User schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    workspace_id: str


class TokenPayload(BaseModel):
    sub: str
    role: Optional[str] = None
    workspace_id: Optional[str] = None
    exp: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = "Security Analyst"


class UserRead(BaseSchema):
    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


# Workspace schemas
class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    review_mode: str = "ADVISORY"


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    review_mode: Optional[str] = None
    ai_monthly_budget_cents: Optional[int] = None


class WorkspaceRead(BaseSchema):
    id: str
    name: str
    slug: str
    review_mode: str
    ai_monthly_budget_cents: int
    ai_used_cents: int
    created_at: datetime


class WorkspaceMemberRead(BaseSchema):
    id: str
    workspace_id: str
    user_id: str
    role: str
    created_at: datetime
    user: Optional[UserRead] = None


class WorkspaceMemberAdd(BaseModel):
    email: EmailStr
    role: str = "DEVELOPER"


# Repository schemas
class RepositoryCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=200, json_schema_extra={"example": "octocat/hello-world"})
    default_branch: str = "main"
    scan_on_pr: bool = True
    min_severity_for_review: str = "HIGH"


class RepositoryRead(BaseSchema):
    id: str
    workspace_id: str
    full_name: str
    default_branch: str
    is_active: bool
    scan_on_pr: bool
    min_severity_for_review: str
    created_at: datetime


# Finding & Audit schemas
class FindingAuditRead(BaseSchema):
    id: str
    finding_id: str
    user_id: Optional[str]
    old_status: str
    new_status: str
    comment: Optional[str]
    created_at: datetime


class FindingRead(BaseSchema):
    id: str
    scan_id: str
    workspace_id: str
    repository_id: str
    fingerprint: str
    scanner_name: str
    rule_id: str
    title: str
    message: str
    severity: str
    confidence: str
    cwe_id: Optional[str] = None
    file_path: str
    start_line: int
    end_line: int
    code_snippet: Optional[str] = None
    remediation_guidance: Optional[str] = None
    validation_status: str
    lifecycle_status: str
    ai_explanation: Optional[str] = None
    ai_suggested_patch: Optional[str] = None
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    audits: Optional[List[FindingAuditRead]] = None


class FindingUpdateStatus(BaseModel):
    lifecycle_status: str = Field(..., pattern="^(OPEN|RESOLVED|WONT_FIX)$")
    validation_status: Optional[str] = Field(None, pattern="^(CONFIRMED|FALSE_POSITIVE|SUPPRESSED)$")
    comment: Optional[str] = Field(None, max_length=1000)


# Scan schemas
class ScanCreate(BaseModel):
    repository_id: str
    commit_sha: str = Field(..., min_length=7, max_length=64)
    branch_name: str = "main"
    base_branch: str = "main"
    pr_number: Optional[int] = None
    title: str = "Manual Security Scan"
    ai_triage: bool = True
    local_path: Optional[str] = None  # Safe path for local fixture scans


class ScanRead(BaseSchema):
    id: str
    workspace_id: str
    repository_id: str
    pr_number: Optional[int]
    commit_sha: str
    branch_name: str
    base_branch: str
    title: str
    trigger: str
    status: str
    retry_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]
    ai_triage_enabled: bool
    ai_summary: Optional[Dict[str, Any]]
    created_at: datetime
    findings_count: Optional[int] = 0
    severity_breakdown: Optional[Dict[str, int]] = None


class ScanDetailRead(ScanRead):
    findings: List[FindingRead] = []
    sarif_report: Optional[Dict[str, Any]] = None


# AI Triage structured output schema
class AITriagedFinding(BaseModel):
    fingerprint: str
    is_likely_false_positive: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    remediation_patch: Optional[str] = None
    security_tradeoffs: Optional[str] = None


class AIPullRequestSummary(BaseModel):
    executive_summary: str
    risk_assessment: str = Field(..., pattern="^(CRITICAL|HIGH|MEDIUM|LOW|CLEAN)$")
    key_vulnerabilities_highlighted: List[str] = []
    triaged_findings: List[AITriagedFinding] = []


# Webhook delivery schema
class WebhookDeliveryRead(BaseSchema):
    id: str
    delivery_id: str
    event_type: str
    status: str
    error_message: Optional[str]
    created_at: datetime


class AuditEventRead(BaseSchema):
    id: str
    workspace_id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    created_at: datetime
