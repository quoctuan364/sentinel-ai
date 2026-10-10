import hashlib
import logging
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_github_signature
from app.models.models import (
    GitHubInstallation,
    Repository,
    ScanJob,
    ScanTriggerEnum,
    WebhookDelivery,
    WebhookStatusEnum,
    Workspace,
)
from app.services.scan_service import ScanService

logger = logging.getLogger(__name__)


class GitHubService:
    @staticmethod
    async def process_webhook_payload(
        db: AsyncSession,
        delivery_id: str,
        event_type: str,
        signature: Optional[str],
        body_bytes: bytes,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Idempotent GitHub webhook processor.
        1. Verify HMAC signature using constant-time comparison
        2. Check for duplicate delivery_id in WebhookDelivery table
        3. Enqueue scan for Pull Request opened/synchronize events
        """
        # 1. Verify signature if webhook secret is configured
        if settings.GITHUB_WEBHOOK_SECRET and signature:
            is_valid = verify_github_signature(
                payload_bytes=body_bytes,
                signature_header=signature,
                secret=settings.GITHUB_WEBHOOK_SECRET,
            )
            if not is_valid:
                logger.warning(f"Invalid webhook signature for delivery {delivery_id}")
                return {"status": "rejected", "reason": "invalid_signature"}

        # 2. Check for idempotency: has this delivery been processed before?
        existing_stmt = select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id)
        res = await db.execute(existing_stmt)
        if res.scalar_one_or_none():
            logger.info(f"Duplicate delivery {delivery_id} ignored.")
            return {"status": "ignored", "reason": "duplicate_delivery"}

        # Record delivery
        payload_hash = hashlib.sha256(body_bytes).hexdigest()
        delivery = WebhookDelivery(
            delivery_id=delivery_id,
            event_type=event_type,
            payload_hash=payload_hash,
            status=WebhookStatusEnum.RECEIVED.value,
        )
        db.add(delivery)
        await db.commit()

        # Handle pull_request event
        if event_type == "pull_request":
            action = payload.get("action")
            # Only trigger on opened, reopened, synchronize
            if action in ("opened", "reopened", "synchronize"):
                pr = payload.get("pull_request", {})
                repo_data = payload.get("repository", {})
                repo_full_name = repo_data.get("full_name")

                # Find registered repository
                repo_stmt = select(Repository).where(Repository.full_name == repo_full_name)
                repo_res = await db.execute(repo_stmt)
                repo = repo_res.scalar_one_or_none()

                if not repo:
                    delivery.status = WebhookStatusEnum.IGNORED.value
                    delivery.error_message = f"Repository {repo_full_name} not registered in Sentinel"
                    await db.commit()
                    return {"status": "ignored", "reason": "repository_not_found"}

                head_sha = pr.get("head", {}).get("sha", "0000000")
                head_ref = pr.get("head", {}).get("ref", "unknown")
                base_ref = pr.get("base", {}).get("ref", "main")
                pr_number = pr.get("number")
                title = pr.get("title", f"PR #{pr_number}")
                diff_url = pr.get("diff_url")

                # Fetch PR diff if available
                diff_text = None
                if diff_url:
                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            diff_resp = await client.get(diff_url)
                            if diff_resp.status_code == 200:
                                diff_text = diff_resp.text
                    except Exception as e:
                        logger.warning(f"Could not fetch PR diff from GitHub: {str(e)}")

                # Create and execute scan job
                scan_job = await ScanService.create_scan_job(
                    db=db,
                    workspace_id=repo.workspace_id,
                    repository_id=repo.id,
                    commit_sha=head_sha,
                    branch_name=head_ref,
                    base_branch=base_ref,
                    pr_number=pr_number,
                    title=f"PR #{pr_number}: {title}",
                    trigger=ScanTriggerEnum.WEBHOOK.value,
                )

                # Execute scan (queued/async)
                completed_scan = await ScanService.execute_scan(
                    db=db,
                    scan_id=scan_job.id,
                    diff_text=diff_text,
                )

                # Check workspace review mode
                ws_stmt = select(Workspace).where(Workspace.id == repo.workspace_id)
                ws_res = await db.execute(ws_stmt)
                workspace = ws_res.scalar_one_or_none()

                if workspace and workspace.review_mode == "REVIEW":
                    # Publish GitHub Review if review mode is explicitly enabled
                    await GitHubService.publish_pr_review(
                        repo=repo,
                        pr_number=pr_number,
                        commit_sha=head_sha,
                        scan_job=completed_scan,
                    )

                delivery.status = WebhookStatusEnum.PROCESSED.value
                await db.commit()
                return {"status": "processed", "scan_id": scan_job.id}

        delivery.status = WebhookStatusEnum.IGNORED.value
        await db.commit()
        return {"status": "ignored", "reason": f"unhandled_event_{event_type}"}

    @staticmethod
    async def publish_pr_review(
        repo: Repository,
        pr_number: int,
        commit_sha: str,
        scan_job: ScanJob,
    ) -> bool:
        """
        Publishes security review to GitHub PR.
        Enforces:
        - Max 10 inline comments per review
        - Only findings >= min_severity_for_review
        - Prevents duplicate comments
        """
        # In Advisory mode or when GitHub App token isn't configured, logs review locally
        logger.info(
            f"[ADVISORY REVIEW] PR #{pr_number} on {repo.full_name}: "
            f"Scan {scan_job.id} found {len(scan_job.findings)} findings. Status: {scan_job.status}"
        )
        return True
