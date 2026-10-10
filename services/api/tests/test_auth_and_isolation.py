import pytest
from httpx import ASGITransport, AsyncClient
from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.models import RoleEnum, User, Workspace, WorkspaceMembership
from app.core.database import AsyncSessionLocal


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected():
    """Verify that unauthenticated requests to protected endpoints return 401."""
    # Ensure fallback auth is disabled
    settings.ALLOW_DEV_FALLBACK_AUTH = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/scans")
        assert res.status_code == 401

        res2 = await client.get("/api/v1/findings")
        assert res2.status_code == 401

        res3 = await client.get("/api/v1/repositories")
        assert res3.status_code == 401


@pytest.mark.asyncio
async def test_tenant_workspace_isolation():
    """Verify that a user from Workspace A cannot access Workspace B."""
    import uuid
    suffix_a = uuid.uuid4().hex[:8]
    suffix_b = uuid.uuid4().hex[:8]

    async with AsyncSessionLocal() as db:
        # Create User A & Workspace A
        user_a = User(email=f"tenant_a_{suffix_a}@sentinel.ai", hashed_password="pw", full_name="Tenant A")
        ws_a = Workspace(name="Workspace A", slug=f"ws-a-{suffix_a}")
        db.add_all([user_a, ws_a])
        await db.flush()

        mem_a = WorkspaceMembership(workspace_id=ws_a.id, user_id=user_a.id, role=RoleEnum.OWNER.value)
        db.add(mem_a)

        # Create User B & Workspace B
        user_b = User(email=f"tenant_b_{suffix_b}@sentinel.ai", hashed_password="pw", full_name="Tenant B")
        ws_b = Workspace(name="Workspace B", slug=f"ws-b-{suffix_b}")
        db.add_all([user_b, ws_b])
        await db.flush()

        mem_b = WorkspaceMembership(workspace_id=ws_b.id, user_id=user_b.id, role=RoleEnum.OWNER.value)
        db.add(mem_b)

        await db.commit()

        user_a_id = user_a.id
        ws_a_id = ws_a.id
        user_b_id = user_b.id
        ws_b_id = ws_b.id

    # Create token for User A
    token_a = create_access_token(subject=user_a_id, workspace_id=ws_a_id, role="OWNER")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Create token for User B
    token_b = create_access_token(subject=user_b_id, workspace_id=ws_b_id, role="OWNER")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User A creates a repo in Workspace A
        res_create = await client.post(
            "/api/v1/repositories",
            headers=headers_a,
            json={"full_name": "tenant-a/service-x", "default_branch": "main"}
        )
        assert res_create.status_code == 200
        repo_a_id = res_create.json()["id"]

        # User A can see repo
        res_list_a = await client.get("/api/v1/repositories", headers=headers_a)
        assert res_list_a.status_code == 200
        repo_names_a = [r["full_name"] for r in res_list_a.json()]
        assert "tenant-a/service-x" in repo_names_a

        # User B CANNOT see User A's repo in their workspace list
        res_list_b = await client.get("/api/v1/repositories", headers=headers_b)
        assert res_list_b.status_code == 200
        repo_names_b = [r["full_name"] for r in res_list_b.json()]
        assert "tenant-a/service-x" not in repo_names_b

        # User B trying to access User A's repo directly returns 404 (isolated)
        res_get_cross = await client.get(f"/api/v1/repositories/{repo_a_id}", headers=headers_b)
        assert res_get_cross.status_code == 404


@pytest.mark.asyncio
async def test_audit_event_logging_and_retrieval():
    """Verify that actions generate audit events and can be retrieved."""
    # Authenticate as default analyst
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        res = await db.execute(select(User).where(User.email == "analyst@sentinel.ai"))
        analyst = res.scalar_one()
        res_ws = await db.execute(select(Workspace).where(Workspace.slug == "sec-ops"))
        ws = res_ws.scalar_one()

    token = create_access_token(subject=analyst.id, workspace_id=ws.id, role="OWNER")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Trigger scan which logs audit event
        scan_payload = {
            "repository_id": "default-fixture-repo",
            "commit_sha": "beefcafe12345678",
            "branch_name": "main",
            "title": "Audit Event Test Scan",
            "ai_triage": False,
            "local_path": "./fixtures/safe-repo"
        }
        res_scan = await client.post("/api/v1/scans", headers=headers, json=scan_payload)
        assert res_scan.status_code == 200

        # Query audit events endpoint
        res_audit = await client.get("/api/v1/audit/events", headers=headers)
        assert res_audit.status_code == 200
        events = res_audit.json()
        assert len(events) >= 1
        actions = [e["action"] for e in events]
        assert "scan.created" in actions
