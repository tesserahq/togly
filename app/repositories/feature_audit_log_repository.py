from uuid import UUID

from sqlalchemy.orm import Session

from app.models.feature_audit_log import FeatureAuditLog


class FeatureAuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        feature_id: UUID,
        feature_key: str,
        user_id: UUID,
        action: str,
        snapshot: dict | None = None,
    ) -> FeatureAuditLog:
        entry = FeatureAuditLog(
            feature_id=feature_id,
            feature_key=feature_key,
            user_id=user_id,
            action=action,
            snapshot=snapshot,
        )
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_by_feature_id(self, feature_id: UUID) -> list[FeatureAuditLog]:
        return (
            self.db.query(FeatureAuditLog)
            .filter(FeatureAuditLog.feature_id == feature_id)
            .order_by(FeatureAuditLog.created_at.desc())
            .all()
        )
