from uuid import UUID

from sqlalchemy.orm import Session

from app.models.gate import Gate, GateType


class GateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_boolean_gate(self, feature_id: UUID) -> Gate | None:
        return (
            self.db.query(Gate)
            .filter(Gate.feature_id == feature_id, Gate.gate_type == GateType.BOOLEAN)
            .first()
        )

    def get_actor_gate(self, feature_id: UUID, actor_id: str) -> Gate | None:
        return (
            self.db.query(Gate)
            .filter(
                Gate.feature_id == feature_id,
                Gate.gate_type == GateType.ACTOR,
                Gate.value == actor_id,
            )
            .first()
        )

    def enable_boolean_gate(self, feature_id: UUID) -> Gate:
        existing = self.get_boolean_gate(feature_id)
        if existing:
            return existing
        gate = Gate(feature_id=feature_id, gate_type=GateType.BOOLEAN, value="true")
        self.db.add(gate)
        self.db.flush()
        return gate

    def disable_boolean_gate(self, feature_id: UUID) -> bool:
        gate = self.get_boolean_gate(feature_id)
        if not gate:
            return False
        self.db.delete(gate)
        self.db.flush()
        return True

    def enable_actor_gate(self, feature_id: UUID, actor_id: str) -> Gate:
        existing = self.get_actor_gate(feature_id, actor_id)
        if existing:
            return existing
        gate = Gate(feature_id=feature_id, gate_type=GateType.ACTOR, value=actor_id)
        self.db.add(gate)
        self.db.flush()
        return gate

    def disable_actor_gate(self, feature_id: UUID, actor_id: str) -> bool:
        gate = self.get_actor_gate(feature_id, actor_id)
        if not gate:
            return False
        self.db.delete(gate)
        self.db.flush()
        return True
