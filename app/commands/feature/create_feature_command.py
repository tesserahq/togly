from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.constants import feature_audit_actions
from app.exceptions.duplicate_resource_error import DuplicateResourceError
from app.models.feature import Feature
from app.models.user import User
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.feature_repository import FeatureRepository


class CreateFeatureCommand:
    def __init__(
        self, db: Session, key: str, description: str | None, current_user: User
    ):
        self.db = db
        self.key = key
        self.description = description
        self.current_user = current_user
        self.feature_repository = FeatureRepository(db)
        self.audit_log_repository = FeatureAuditLogRepository(db)

    def execute(self) -> Feature:
        if self.feature_repository.get_feature_by_key(self.key) is not None:
            raise DuplicateResourceError(
                f"Feature with key {self.key!r} already exists"
            )

        try:
            feature = self.feature_repository.create_feature(
                key=self.key, description=self.description
            )
            self.audit_log_repository.create(
                feature_id=feature.id,
                feature_key=feature.key,
                user_id=self.current_user.id,
                action=feature_audit_actions.CREATED,
                snapshot={"key": feature.key, "description": feature.description},
            )
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicateResourceError(
                f"Feature with key {self.key!r} already exists"
            )
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(feature)
        return feature
