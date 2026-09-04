from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details_json: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            ip_address=ip_address,
            user_agent=user_agent,
            details_json=details_json or {}
        )
        self.db.add(entry)
        self.db.commit()
        return entry

    def list_logs(self, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
