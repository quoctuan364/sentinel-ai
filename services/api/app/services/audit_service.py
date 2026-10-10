import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import AuditEvent

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    async def log_event(
        db: AsyncSession,
        workspace_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditEvent:
        event = AuditEvent(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
        )
        db.add(event)
        # We don't commit immediately to allow enclosing transactions to commit
        return event
