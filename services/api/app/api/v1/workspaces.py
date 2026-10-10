from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_current_workspace, require_roles
from app.core.database import get_db
from app.models.models import (
    AIAnalysisRecord,
    RoleEnum,
    ScanJob,
    UsageRecord,
    User,
    Workspace,
    WorkspaceMembership,
)
from app.schemas.schemas import (
    WorkspaceMemberAdd,
    WorkspaceMemberRead,
    WorkspaceRead,
    WorkspaceUpdate,
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("/current", response_model=WorkspaceRead)
async def get_active_workspace(workspace: Workspace = Depends(get_current_workspace)):
    return workspace


@router.patch("/current", response_model=WorkspaceRead)
async def update_active_workspace(
    update_data: WorkspaceUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
):
    if update_data.name is not None:
        workspace.name = update_data.name
    if update_data.review_mode is not None:
        workspace.review_mode = update_data.review_mode
    if update_data.ai_monthly_budget_cents is not None:
        workspace.ai_monthly_budget_cents = update_data.ai_monthly_budget_cents

    await db.commit()
    await db.refresh(workspace)
    return workspace


@router.get("/current/members", response_model=List[WorkspaceMemberRead])
async def list_workspace_members(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(WorkspaceMembership)
        .options(selectinload(WorkspaceMembership.user))
        .where(WorkspaceMembership.workspace_id == workspace.id)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/current/members", response_model=WorkspaceMemberRead)
async def add_workspace_member(
    member_in: WorkspaceMemberAdd,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
):
    # Check if user exists by email
    stmt = select(User).where(User.email == member_in.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{member_in.email}' not found.",
        )

    # Check if already a member
    exist_stmt = select(WorkspaceMembership).where(
        WorkspaceMembership.workspace_id == workspace.id,
        WorkspaceMembership.user_id == user.id,
    )
    exist_res = await db.execute(exist_stmt)
    if exist_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace.",
        )

    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=user.id,
        role=member_in.role,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


@router.get("/current/stats")
async def get_workspace_stats(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    # Total scans
    scans_stmt = select(func.count(ScanJob.id)).where(ScanJob.workspace_id == workspace.id)
    scans_res = await db.execute(scans_stmt)
    total_scans = scans_res.scalar() or 0

    # Total tokens used
    tokens_stmt = select(
        func.sum(AIAnalysisRecord.input_tokens + AIAnalysisRecord.output_tokens)
    ).where(AIAnalysisRecord.workspace_id == workspace.id)
    tokens_res = await db.execute(tokens_stmt)
    total_tokens = tokens_res.scalar() or 0

    return {
        "workspace_id": workspace.id,
        "name": workspace.name,
        "total_scans": total_scans,
        "total_ai_tokens": total_tokens,
        "ai_monthly_budget_cents": workspace.ai_monthly_budget_cents,
        "ai_used_cents": workspace.ai_used_cents,
        "review_mode": workspace.review_mode,
    }
