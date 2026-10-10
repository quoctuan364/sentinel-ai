from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_workspace, require_roles
from app.core.database import get_db
from app.models.models import Finding, Repository, RoleEnum, ScanJob, Workspace
from app.schemas.schemas import ScanCreate, ScanDetailRead, ScanRead
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.get("", response_model=List[ScanRead])
async def list_scans(
    repository_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    query = select(ScanJob).where(ScanJob.workspace_id == workspace.id)
    if repository_id:
        query = query.where(ScanJob.repository_id == repository_id)
    if status:
        query = query.where(ScanJob.status == status)

    query = query.order_by(desc(ScanJob.created_at)).offset(offset).limit(limit)
    res = await db.execute(query)
    scans = res.scalars().all()

    # Enrich with findings count
    results = []
    for s in scans:
        cnt_stmt = select(func.count(Finding.id)).where(Finding.scan_id == s.id)
        cnt_res = await db.execute(cnt_stmt)
        count = cnt_res.scalar() or 0

        scan_dict = ScanRead.model_validate(s)
        scan_dict.findings_count = count
        results.append(scan_dict)

    return results


@router.post("", response_model=ScanRead)
async def trigger_scan(
    scan_in: ScanCreate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.DEVELOPER])),
):
    # Verify repository belongs to workspace
    repo_stmt = select(Repository).where(
        Repository.id == scan_in.repository_id,
        Repository.workspace_id == workspace.id,
    )
    repo_res = await db.execute(repo_stmt)
    repo = repo_res.scalar_one_or_none()
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found in this workspace.",
        )

    # Create scan job
    job = await ScanService.create_scan_job(
        db=db,
        workspace_id=workspace.id,
        repository_id=repo.id,
        commit_sha=scan_in.commit_sha,
        branch_name=scan_in.branch_name,
        base_branch=scan_in.base_branch,
        pr_number=scan_in.pr_number,
        title=scan_in.title,
        trigger="MANUAL",
        ai_triage_enabled=scan_in.ai_triage,
    )

    # Execute scan synchronously or asynchronously (returns completed job)
    completed_job = await ScanService.execute_scan(
        db=db,
        scan_id=job.id,
        target_path=scan_in.local_path,
    )

    cnt_stmt = select(func.count(Finding.id)).where(Finding.scan_id == completed_job.id)
    cnt_res = await db.execute(cnt_stmt)
    count = cnt_res.scalar() or 0

    scan_read = ScanRead.model_validate(completed_job)
    scan_read.findings_count = count
    return scan_read


@router.get("/{scan_id}", response_model=ScanDetailRead)
async def get_scan_detail(
    scan_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(ScanJob)
        .options(selectinload(ScanJob.findings))
        .where(
            ScanJob.id == scan_id,
            ScanJob.workspace_id == workspace.id,
        )
    )
    res = await db.execute(stmt)
    scan = res.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found",
        )

    scan_read = ScanDetailRead.model_validate(scan)
    scan_read.findings_count = len(scan.findings)
    return scan_read


@router.post("/{scan_id}/cancel", response_model=ScanRead)
async def cancel_scan(
    scan_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
):
    scan = await ScanService.cancel_scan(db=db, scan_id=scan_id)
    if not scan or scan.workspace_id != workspace.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


@router.get("/{scan_id}/sarif")
async def get_scan_sarif(
    scan_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ScanJob).where(
        ScanJob.id == scan_id,
        ScanJob.workspace_id == workspace.id,
    )
    res = await db.execute(stmt)
    scan = res.scalar_one_or_none()
    if not scan or not scan.sarif_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SARIF report not found for this scan",
        )
    return scan.sarif_report
