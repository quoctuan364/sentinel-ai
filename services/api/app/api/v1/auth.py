from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.models import RoleEnum, User, Workspace, WorkspaceMembership
from app.schemas.schemas import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == credentials.email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Get user workspace
    mem_stmt = (
        select(WorkspaceMembership)
        .where(WorkspaceMembership.user_id == user.id)
        .limit(1)
    )
    mem_res = await db.execute(mem_stmt)
    membership = mem_res.scalar_one_or_none()
    workspace_id = membership.workspace_id if membership else ""
    role = membership.role if membership else RoleEnum.DEVELOPER.value

    token = create_access_token(
        subject=user.id,
        workspace_id=workspace_id,
        role=role,
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=role,
        workspace_id=workspace_id,
    )


@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Check if default workspace exists, otherwise create one
    ws_stmt = select(Workspace).limit(1)
    ws_res = await db.execute(ws_stmt)
    workspace = ws_res.scalar_one_or_none()
    if not workspace:
        workspace = Workspace(
            name="Security Engineering",
            slug="sec-eng",
        )
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)

    # Add user to workspace as OWNER or DEVELOPER
    membership = WorkspaceMembership(
        user_id=user.id,
        workspace_id=workspace.id,
        role=RoleEnum.OWNER.value,
    )
    db.add(membership)
    await db.commit()

    return user


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
    return user
