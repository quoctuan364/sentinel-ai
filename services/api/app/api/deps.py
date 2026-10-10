from typing import List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import RoleEnum, User, Workspace, WorkspaceMembership

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Authenticate user via Bearer JWT.
    If no authorization header is provided in local dev mode, return the default admin user.
    """
    if auth and auth.credentials:
        payload = decode_access_token(auth.credentials)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            stmt = select(User).where(User.id == user_id)
            res = await db.execute(stmt)
            user = res.scalar_one_or_none()
            if user:
                return user

    # Only allow fallback to default user if explicitly permitted in development mode
    if settings.ENVIRONMENT == "development" and settings.ALLOW_DEV_FALLBACK_AUTH:
        stmt = select(User).where(User.email == "analyst@sentinel.ai")
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_workspace(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Workspace:
    """
    Retrieve active workspace for user. Enforces strict tenant isolation.
    """
    stmt = (
        select(Workspace)
        .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
        .where(WorkspaceMembership.user_id == user.id)
    )
    res = await db.execute(stmt)
    workspace = res.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to any active workspace",
        )

    return workspace


def require_roles(allowed_roles: List[RoleEnum]):
    async def role_checker(
        user: User = Depends(get_current_user),
        workspace: Workspace = Depends(get_current_workspace),
        db: AsyncSession = Depends(get_db),
    ):
        stmt = select(WorkspaceMembership).where(
            WorkspaceMembership.user_id == user.id,
            WorkspaceMembership.workspace_id == workspace.id,
        )
        res = await db.execute(stmt)
        membership = res.scalar_one_or_none()
        if not membership or membership.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of roles: {[r.value for r in allowed_roles]}",
            )
        return membership

    return role_checker
