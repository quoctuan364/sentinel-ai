from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_current_workspace, require_roles
from app.core.database import get_db
from app.models.models import (
    Finding,
    FindingAudit,
    RoleEnum,
    User,
    Workspace,
)
from app.schemas.schemas import FindingRead, FindingUpdateStatus

router = APIRouter(prefix="/findings", tags=["Findings"])


@router.get("", response_model=List[FindingRead])
async def list_findings(
    severity: Optional[str] = Query(None),
    scanner_name: Optional[str] = Query(None),
    lifecycle_status: Optional[str] = Query(None),
    repository_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Finding)
        .options(selectinload(Finding.audits))
        .where(Finding.workspace_id == workspace.id)
    )

    if severity:
        query = query.where(Finding.severity == severity.upper())
    if scanner_name:
        query = query.where(Finding.scanner_name == scanner_name)
    if lifecycle_status:
        query = query.where(Finding.lifecycle_status == lifecycle_status.upper())
    if repository_id:
        query = query.where(Finding.repository_id == repository_id)
    if search:
        query = query.where(
            Finding.title.ilike(f"%{search}%") | Finding.file_path.ilike(f"%{search}%")
        )

    query = query.order_by(desc(Finding.created_at)).offset(offset).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()


@router.get("/{finding_id}", response_model=FindingRead)
async def get_finding(
    finding_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Finding)
        .options(selectinload(Finding.audits))
        .where(
            Finding.id == finding_id,
            Finding.workspace_id == workspace.id,
        )
    )
    res = await db.execute(stmt)
    finding = res.scalar_one_or_none()
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )
    return finding


@router.patch("/{finding_id}/status", response_model=FindingRead)
async def update_finding_status(
    finding_id: str,
    update_in: FindingUpdateStatus,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.DEVELOPER])),
):
    stmt = (
        select(Finding)
        .options(selectinload(Finding.audits))
        .where(
            Finding.id == finding_id,
            Finding.workspace_id == workspace.id,
        )
    )
    res = await db.execute(stmt)
    finding = res.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")

    old_status = finding.lifecycle_status
    finding.lifecycle_status = update_in.lifecycle_status
    if update_in.validation_status:
        finding.validation_status = update_in.validation_status

    # Record audit event
    audit = FindingAudit(
        finding_id=finding.id,
        user_id=user.id,
        old_status=old_status,
        new_status=update_in.lifecycle_status,
        comment=update_in.comment,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(finding)
    return finding
