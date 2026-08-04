"""
Audit Logging Service — records every significant action for security and observability.

Every module can call log_action() to write an audit trail entry.
"""

import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.log import Log


class AuditService:
    """Centralized audit logging."""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> Log:
        """Write an audit log entry."""
        entry = Log(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
        )
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def list_logs(
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
        action: str | None = None,
    ) -> list[dict]:
        """Retrieve audit logs for a user."""
        from sqlalchemy import select, desc
        query = select(Log).where(Log.user_id == user_id).order_by(desc(Log.created_at))
        if action:
            query = query.where(Log.action == action)
        query = query.limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()
        return [
            {
                "id": str(log.id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]