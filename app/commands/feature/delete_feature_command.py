from sqlalchemy.orm import Session

from app.constants import feature_audit_actions
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.models.user import User
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.feature_repository import FeatureRepository


class DeleteFeatureCommand:
    def __init__(self, db: Session, feature_key: str, current_user: User):
        self.db = db
        self.feature_key = feature_key
        self.current_user = current_user
        self.feature_repository = FeatureRepository(db)
        self.audit_log_repository = FeatureAuditLogRepository(db)

    def execute(self) -> None:
        feature = self.feature_repository.get_feature_by_key(self.feature_key)
        if feature is None:
            raise ResourceNotFoundError(
                f"Feature with key {self.feature_key!r} not found"
            )

        feature_id = feature.id
        feature_key = feature.key

        try:
            self.feature_repository.delete_feature(feature)
            self.audit_log_repository.create(
                feature_id=feature_id,
                feature_key=feature_key,
                user_id=self.current_user.id,
                action=feature_audit_actions.DELETED,
                snapshot=None,
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
