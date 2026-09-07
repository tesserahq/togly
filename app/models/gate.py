import enum
import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.mixins import TimestampMixin


class GateType(str, enum.Enum):
    BOOLEAN = "boolean"
    ACTOR = "actor"


class Gate(Base, TimestampMixin):
    """A boolean or actor gate belonging to a feature.

    Only an enabled boolean gate row is stored (disabling removes it), and
    duplicate actor enables are idempotent via a unique constraint enforced
    in the schema migration.
    """

    __tablename__ = "gates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_id = Column(
        UUID(as_uuid=True),
        ForeignKey("features.id", ondelete="CASCADE"),
        nullable=False,
    )
    gate_type = Column(
        Enum(
            GateType,
            name="gate_type",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    value = Column(String, nullable=False)

    feature = relationship("Feature", back_populates="gates")
