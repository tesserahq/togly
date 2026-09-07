from sqlalchemy.orm import Session

from app.constants import feature_audit_actions
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.models.user import User
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.feature_repository import FeatureRepository
from app.repositories.gate_repository import GateRepository


class DisableActorGateCommand:
    def __init__(
        self, db: Session, feature_key: str, actor_id: str, current_user: User
    ):
        self.db = db
        self.feature_key = feature_key
        self.actor_id = actor_id
        self.current_user = current_user
        self.feature_repository = FeatureRepository(db)
        self.gate_repository = GateRepository(db)
        self.audit_log_repository = FeatureAuditLogRepository(db)

    def execute(self) -> None:
        feature = self.feature_repository.get_feature_by_key(self.feature_key)
        if feature is None:
            raise ResourceNotFoundError(
                f"Feature with key {self.feature_key!r} not found"
            )

        try:
            self.gate_repository.disable_actor_gate(feature.id, self.actor_id)
            self.audit_log_repository.create(
                feature_id=feature.id,
                feature_key=feature.key,
                user_id=self.current_user.id,
                action=feature_audit_actions.ACTOR_DISABLED,
                snapshot={"actor_id": self.actor_id},
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
