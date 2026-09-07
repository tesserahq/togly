from uuid import UUID

from sqlalchemy.orm import Session

from app.models.feature_audit_log import FeatureAuditLog
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository


class GetFeatureAuditLogQuery:
    def __init__(self, db: Session, feature_id: UUID):
        self.db = db
        self.feature_id = feature_id
        self.audit_log_repository = FeatureAuditLogRepository(db)

    def execute(self) -> list[FeatureAuditLog]:
        return self.audit_log_repository.list_by_feature_id(self.feature_id)
