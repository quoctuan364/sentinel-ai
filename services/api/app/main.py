import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.findings import router as findings_router
from app.api.v1.health import router as health_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.repositories import router as repos_router
from app.api.v1.scans import router as scans_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.workspaces import router as workspaces_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.models import Repository, RoleEnum, User, Workspace, WorkspaceMembership
from app.services.queue_service import task_queue

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s", "level":"%(levelname)s", "logger":"%(name)s", "message":"%(message)s"}'
)
logger = logging.getLogger("sentinel")


async def seed_initial_data():
    """Seed initial workspace, demo user, and demo repository for instant local operation."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        res = await db.execute(select(User).where(User.email == "analyst@sentinel.ai"))
        if not res.scalar_one_or_none():
            logger.info("Bootstrapping default workspace and user for Sentinel AI...")
            user = User(
                email="analyst@sentinel.ai",
                hashed_password=get_password_hash("SentinelSec2026!"),
                full_name="Principal Security Analyst",
            )
            db.add(user)
            await db.flush()

            workspace = Workspace(
                name="Security Operations",
                slug="sec-ops",
                review_mode="ADVISORY",
                ai_monthly_budget_cents=10000,
            )
            db.add(workspace)
            await db.flush()

            membership = WorkspaceMembership(
                workspace_id=workspace.id,
                user_id=user.id,
                role=RoleEnum.OWNER.value,
            )
            db.add(membership)

            repo = Repository(
                id="default-fixture-repo",
                workspace_id=workspace.id,
                full_name="sentinel-ai/vulnerable-test-suite",
                default_branch="main",
                scan_on_pr=True,
                min_severity_for_review="HIGH",
            )
            db.add(repo)

            await db.commit()
            logger.info("Bootstrap complete: user analyst@sentinel.ai and repository ready.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")

    # Production security validation
    if settings.ENVIRONMENT == "production":
        if "change-in-prod" in settings.SECRET_KEY:
            logger.critical("SECURITY ALERT: Using default dev SECRET_KEY in production! Please set SECRET_KEY in environment.")
        if settings.ALLOW_DEV_FALLBACK_AUTH:
            logger.critical("SECURITY ALERT: ALLOW_DEV_FALLBACK_AUTH is enabled in production! Forcing to False.")
            settings.ALLOW_DEV_FALLBACK_AUTH = False

    # Initialize DB schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed demo data in development mode
    if settings.ENVIRONMENT == "development":
        await seed_initial_data()

    # Initialize task queue
    await task_queue.initialize()

    yield

    logger.info("Shutting down Sentinel AI services...")
    await task_queue.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Grade AI Code Security Review Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS: Restricted to configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Correlation ID Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = correlation_id
    return response


# Include Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(metrics_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(workspaces_router, prefix=settings.API_V1_STR)
app.include_router(repos_router, prefix=settings.API_V1_STR)
app.include_router(scans_router, prefix=settings.API_V1_STR)
app.include_router(findings_router, prefix=settings.API_V1_STR)
app.include_router(webhooks_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
