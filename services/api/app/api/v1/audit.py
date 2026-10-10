from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_workspace
from app.core.database import get_db
from app.models.models import AuditEvent, WebhookDelivery, Workspace
from app.schemas.schemas import AuditEventRead, WebhookDeliveryRead

router = APIRouter(prefix="/audit", tags=["Audit & Observability"])


@router.get("/events", response_model=List[AuditEventRead])
async def list_audit_events(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditEvent).where(AuditEvent.workspace_id == workspace.id)
    if action:
        query = query.where(AuditEvent.action == action)
    if resource_type:
        query = query.where(AuditEvent.resource_type == resource_type)

    query = query.order_by(desc(AuditEvent.created_at)).offset(offset).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()


@router.get("/deliveries", response_model=List[WebhookDeliveryRead])
async def list_webhook_deliveries(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(WebhookDelivery)
        .order_by(desc(WebhookDelivery.created_at))
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(query)
    return res.scalars().all()
