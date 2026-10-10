import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.provider import get_ai_provider
from app.core.config import settings
from app.models.models import (
    AIAnalysisRecord,
    AuditEvent,
    Finding,
    FindingAudit,
    Repository,
    ScanJob,
    ScanStatusEnum,
    UsageRecord,
    Workspace,
)
from app.scanners.runner import scan_directory, scan_diff_content
from app.scanners.sarif import export_to_sarif

logger = logging.getLogger(__name__)


class ScanService:
    @staticmethod
    async def create_scan_job(
        db: AsyncSession,
        workspace_id: str,
        repository_id: str,
        commit_sha: str,
        branch_name: str = "main",
        base_branch: str = "main",
        pr_number: Optional[int] = None,
        title: str = "Manual Security Scan",
        trigger: str = "MANUAL",
        ai_triage_enabled: bool = True,
    ) -> ScanJob:
        scan_job = ScanJob(
            workspace_id=workspace_id,
            repository_id=repository_id,
            commit_sha=commit_sha,
            branch_name=branch_name,
            base_branch=base_branch,
            pr_number=pr_number,
            title=title,
            trigger=trigger,
            status=ScanStatusEnum.PENDING.value,
            ai_triage_enabled=ai_triage_enabled,
        )
        db.add(scan_job)
        await db.flush()

        from app.services.audit_service import AuditService
        await AuditService.log_event(
            db=db,
            workspace_id=workspace_id,
            action="scan.created",
            resource_type="scan_job",
            resource_id=scan_job.id,
            details={"title": title, "commit_sha": commit_sha, "branch": branch_name},
        )
        await db.commit()
        await db.refresh(scan_job)
        return scan_job

    @staticmethod
    async def execute_scan(
        db: AsyncSession,
        scan_id: str,
        target_path: Optional[str] = None,
        diff_text: Optional[str] = None,
    ) -> ScanJob:
        """
        Execute the end-to-end scanner pipeline:
        1. Transition state: QUEUED -> RUNNING
        2. Run deterministic scanners (AST, Secrets, Pattern)
        3. Persist normalized findings with stable fingerprints
        4. Run optional AI triage
        5. Export SARIF
        6. Transition state: RUNNING -> SUCCEEDED or FAILED
        """
        stmt = select(ScanJob).where(ScanJob.id == scan_id)
        result = await db.execute(stmt)
        scan = result.scalar_one_or_none()
        if not scan:
            raise ValueError(f"ScanJob {scan_id} not found")

        # Check if already cancelled
        if scan.status == ScanStatusEnum.CANCELLED.value:
            logger.info(f"Scan {scan_id} was cancelled before execution.")
            return scan

        # Transition to RUNNING
        scan.status = ScanStatusEnum.RUNNING.value
        scan.started_at = datetime.now(timezone.utc)
        await db.commit()

        start_time = time.time()

        try:
            raw_findings: List[Dict[str, Any]] = []

            if diff_text:
                raw_findings = scan_diff_content(diff_text)
            elif target_path:
                raw_findings = scan_directory(target_path)
            else:
                # Default scan path: fixtures directory if none specified
                fixtures_dir = "./fixtures/vulnerable-repo"
                raw_findings = scan_directory(fixtures_dir)

            # Persist findings into database with deduplication
            persisted_findings: List[Finding] = []
            for rf in raw_findings:
                fp = rf["fingerprint"]
                # Check if finding with this fingerprint already exists in repository
                existing_stmt = select(Finding).where(
                    Finding.repository_id == scan.repository_id,
                    Finding.fingerprint == fp,
                )
                existing_res = await db.execute(existing_stmt)
                existing_finding = existing_res.scalar_one_or_none()

                now = datetime.now(timezone.utc)
                if existing_finding:
                    existing_finding.last_seen_at = now
                    # Link to latest scan
                    existing_finding.scan_id = scan.id
                    persisted_findings.append(existing_finding)
                else:
                    new_finding = Finding(
                        scan_id=scan.id,
                        workspace_id=scan.workspace_id,
                        repository_id=scan.repository_id,
                        fingerprint=fp,
                        scanner_name=rf.get("scanner_name", "sentinel-engine"),
                        rule_id=rf.get("rule_id", "UNKNOWN"),
                        title=rf.get("title", "Potential Vulnerability"),
                        message=rf.get("message", ""),
                        severity=rf.get("severity", "MEDIUM"),
                        confidence=rf.get("confidence", "HIGH"),
                        cwe_id=rf.get("cwe_id"),
                        file_path=rf.get("file_path", ""),
                        start_line=rf.get("start_line", 1),
                        end_line=rf.get("end_line", 1),
                        code_snippet=rf.get("code_snippet"),
                        remediation_guidance=rf.get("remediation_guidance"),
                        validation_status="CONFIRMED",
                        lifecycle_status="OPEN",
                        first_seen_at=now,
                        last_seen_at=now,
                    )
                    db.add(new_finding)
                    persisted_findings.append(new_finding)

            await db.commit()

            # Optional AI Triage
            if scan.ai_triage_enabled and settings.AI_ENABLED:
                ai_provider = get_ai_provider()
                ai_result = await ai_provider.triage_scan(
                    pr_title=scan.title,
                    pr_description=f"Branch {scan.branch_name} targeting {scan.base_branch}",
                    findings=raw_findings,
                    diff_text=diff_text,
                )
                scan.ai_summary = ai_result.get("summary")

                # Update findings with AI explanations & patch suggestions
                triaged_findings = ai_result.get("summary", {}).get("triaged_findings", [])
                triage_map = {tf["fingerprint"]: tf for tf in triaged_findings if "fingerprint" in tf}

                for pf in persisted_findings:
                    if pf.fingerprint in triage_map:
                        tdata = triage_map[pf.fingerprint]
                        pf.ai_explanation = tdata.get("reasoning")
                        pf.ai_suggested_patch = tdata.get("remediation_patch")

                # Record AI analysis metadata
                meta = ai_result.get("metadata", {})
                ai_record = AIAnalysisRecord(
                    scan_id=scan.id,
                    workspace_id=scan.workspace_id,
                    provider=meta.get("provider", "mock"),
                    model_name=meta.get("model", "default"),
                    prompt_version=meta.get("prompt_version", "v1.0"),
                    input_tokens=meta.get("input_tokens", 0),
                    output_tokens=meta.get("output_tokens", 0),
                    duration_ms=meta.get("duration_ms", 0),
                    status=meta.get("status", "SUCCEEDED"),
                )
                db.add(ai_record)

            # Generate SARIF report
            sarif_doc = export_to_sarif(raw_findings, run_id=scan.id)
            scan.sarif_report = sarif_doc

            # Record usage
            usage = UsageRecord(
                workspace_id=scan.workspace_id,
                metric="scans_run",
                quantity=1,
            )
            db.add(usage)

            # Complete scan
            scan.status = ScanStatusEnum.SUCCEEDED.value
            scan.completed_at = datetime.now(timezone.utc)
            scan.duration_seconds = round(time.time() - start_time, 2)

            from app.services.audit_service import AuditService
            await AuditService.log_event(
                db=db,
                workspace_id=scan.workspace_id,
                action="scan.completed",
                resource_type="scan_job",
                resource_id=scan.id,
                details={
                    "status": scan.status,
                    "findings_count": len(raw_findings),
                    "duration_seconds": scan.duration_seconds
                },
            )

            await db.commit()
            await db.refresh(scan)
            return scan

        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {str(e)}", exc_info=True)
            scan.status = ScanStatusEnum.FAILED.value
            scan.error_message = str(e)
            scan.completed_at = datetime.now(timezone.utc)
            scan.duration_seconds = round(time.time() - start_time, 2)
            await db.commit()
            return scan

    @staticmethod
    async def cancel_scan(db: AsyncSession, scan_id: str) -> Optional[ScanJob]:
        stmt = select(ScanJob).where(ScanJob.id == scan_id)
        res = await db.execute(stmt)
        scan = res.scalar_one_or_none()
        if scan and scan.status in (ScanStatusEnum.PENDING.value, ScanStatusEnum.QUEUED.value, ScanStatusEnum.RUNNING.value):
            scan.status = ScanStatusEnum.CANCELLED.value
            scan.completed_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(scan)
        return scan
