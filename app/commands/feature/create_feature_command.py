from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.constants import feature_audit_actions
from app.exceptions.duplicate_resource_error import DuplicateResourceError
from app.models.feature import Feature
from app.models.user import User
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.feature_repository import FeatureRepository
from app.schemas.feature import FeatureCreate


class CreateFeatureCommand:
    def __init__(self, db: Session):
        self.db = db
        self.feature_repository = FeatureRepository(db)
        self.audit_log_repository = FeatureAuditLogRepository(db)

    def execute(self, feature_data: FeatureCreate, created_by: User) -> Feature:
        if self.feature_repository.get_feature_by_key(feature_data.key) is not None:
            raise DuplicateResourceError(
                f"Feature with key {feature_data.key!r} already exists"
            )

        try:
            feature = self.feature_repository.create_feature(
                key=feature_data.key, description=feature_data.description
            )
            self.audit_log_repository.create(
                feature_id=feature.id,
                feature_key=feature.key,
                user_id=created_by.id,
                action=feature_audit_actions.CREATED,
                snapshot={"key": feature.key, "description": feature.description},
            )
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicateResourceError(
                f"Feature with key {feature_data.key!r} already exists"
            )
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(feature)
        return feature
