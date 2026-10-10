from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_workspace, require_roles
from app.core.database import get_db
from app.models.models import Repository, RoleEnum, Workspace
from app.schemas.schemas import RepositoryCreate, RepositoryRead

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.get("", response_model=List[RepositoryRead])
async def list_repositories(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Repository).where(Repository.workspace_id == workspace.id)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("", response_model=RepositoryRead)
async def create_repository(
    repo_in: RepositoryCreate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _membership=Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.DEVELOPER])),
):
    # Check if already registered in workspace
    stmt = select(Repository).where(
        Repository.workspace_id == workspace.id,
        Repository.full_name == repo_in.full_name,
    )
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Repository '{repo_in.full_name}' is already registered in this workspace.",
        )

    repo = Repository(
        workspace_id=workspace.id,
        full_name=repo_in.full_name,
        default_branch=repo_in.default_branch,
        scan_on_pr=repo_in.scan_on_pr,
        min_severity_for_review=repo_in.min_severity_for_review,
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)
    return repo


@router.get("/{repo_id}", response_model=RepositoryRead)
async def get_repository(
    repo_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Repository).where(
        Repository.id == repo_id,
        Repository.workspace_id == workspace.id,
    )
    res = await db.execute(stmt)
    repo = res.scalar_one_or_none()
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )
    return repo
