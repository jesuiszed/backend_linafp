from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.audit_log import AuditLog
from app.models.user import UserRole

router = APIRouter()


@router.get("")
def list_audit_logs(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(UserRole.ADMIN)),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    query = db.query(AuditLog)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [
            {
                "id": item.id,
                "actor_user_id": item.actor_user_id,
                "action": item.action,
                "entity": item.entity,
                "entity_id": item.entity_id,
                "details": item.details,
                "created_at": item.created_at,
            }
            for item in items
        ],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }
