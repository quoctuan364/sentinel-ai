import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_and_readiness():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Liveness probe
        res = await client.get("/api/v1/healthz")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"

        # Readiness probe
        res = await client.get("/api/v1/ready")
        assert res.status_code == 200
        assert res.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_metrics_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/metrics")
        assert res.status_code == 200
        assert "sentinel_scans_total" in res.text


@pytest.mark.asyncio
async def test_end_to_end_scan_and_findings():
    from app.core.database import AsyncSessionLocal
    from app.models.models import User, Workspace
    from app.core.security import create_access_token
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.email == "analyst@sentinel.ai"))
        analyst = res.scalar_one()
        res_ws = await db.execute(select(Workspace).where(Workspace.slug == "sec-ops"))
        ws = res_ws.scalar_one()

    token = create_access_token(subject=analyst.id, workspace_id=ws.id, role="OWNER")
    auth_headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Trigger scan on vulnerable fixture
        scan_payload = {
            "repository_id": "default-fixture-repo",
            "commit_sha": "a1b2c3d4e5f67890",
            "branch_name": "feature/payment",
            "base_branch": "main",
            "pr_number": 42,
            "title": "Add payment gateway",
            "ai_triage": True,
            "local_path": "./fixtures/vulnerable-repo"
        }
        res = await client.post("/api/v1/scans", headers=auth_headers, json=scan_payload)
        assert res.status_code == 200
        scan_data = res.json()
        assert scan_data["status"] == "SUCCEEDED"
        assert scan_data["findings_count"] > 0
        scan_id = scan_data["id"]

        # Fetch scan detail
        detail_res = await client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert len(detail["findings"]) > 0
        assert detail["sarif_report"] is not None

        # Fetch findings explorer
        findings_res = await client.get("/api/v1/findings", headers=auth_headers)
        assert findings_res.status_code == 200
        findings = findings_res.json()
        assert len(findings) > 0

        # Update finding lifecycle status
        first_finding = findings[0]
        finding_id = first_finding["id"]
        update_res = await client.patch(
            f"/api/v1/findings/{finding_id}/status",
            headers=auth_headers,
            json={
                "lifecycle_status": "RESOLVED",
                "comment": "Verified parameterized query fix in PR #42."
            }
        )
        assert update_res.status_code == 200
        updated = update_res.json()
        assert updated["lifecycle_status"] == "RESOLVED"
        assert len(updated["audits"]) >= 1


@pytest.mark.asyncio
async def test_webhook_idempotency_and_signature():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        import hashlib
        import hmac
        from app.core.config import settings

        delivery_id = "test-delivery-guid-001"
        body = b'{"action":"ping"}'
        mac = hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"), msg=body, digestmod=hashlib.sha256)
        sig = f"sha256={mac.hexdigest()}"

        headers = {
            "X-GitHub-Delivery": delivery_id,
            "X-GitHub-Event": "ping",
            "X-Hub-Signature-256": sig,
            "Content-Type": "application/json"
        }

        # First delivery: processed/ignored cleanly
        res1 = await client.post("/api/v1/webhooks/github", content=body, headers=headers)
        assert res1.status_code == 200

        # Second delivery with same delivery_id: idempotently ignored
        res2 = await client.post("/api/v1/webhooks/github", content=body, headers=headers)
        assert res2.status_code == 200
        assert res2.json()["status"] == "ignored"
        assert res2.json()["reason"] == "duplicate_delivery"
