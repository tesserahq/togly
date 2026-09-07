import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db import Base


class FeatureAuditLog(Base):
    """Append-only audit trail for feature and gate mutations.

    feature_id is retained as the stable correlation identity after a
    feature is deleted (no cascading FK to features); feature_key is a
    denormalized display value for readability.
    """

    __tablename__ = "feature_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    feature_key = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)
    snapshot = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
