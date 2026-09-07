from sqlalchemy.orm import Session

from app.constants import feature_audit_actions
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.models.gate import Gate
from app.models.user import User
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.feature_repository import FeatureRepository
from app.repositories.gate_repository import GateRepository
from app.schemas.feature import ActorGateRequest


class EnableActorGateCommand:
    def __init__(self, db: Session):
        self.db = db
        self.feature_repository = FeatureRepository(db)
        self.gate_repository = GateRepository(db)
        self.audit_log_repository = FeatureAuditLogRepository(db)

    def execute(self, gate_data: ActorGateRequest, modified_by: User) -> Gate:
        feature = self.feature_repository.get_feature_by_key(gate_data.key)
        if feature is None:
            raise ResourceNotFoundError(f"Feature with key {gate_data.key!r} not found")

        try:
            gate = self.gate_repository.enable_actor_gate(
                feature.id, gate_data.actor_id
            )
            self.audit_log_repository.create(
                feature_id=feature.id,
                feature_key=feature.key,
                user_id=modified_by.id,
                action=feature_audit_actions.ACTOR_ENABLED,
                snapshot={"actor_id": gate_data.actor_id},
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(gate)
        return gate
