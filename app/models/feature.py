import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base
from app.models.mixins import TimestampMixin


class Feature(Base, TimestampMixin):
    """A uniquely named feature flag with a global boolean gate and zero or
    more actor gates."""

    __tablename__ = "features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)

    gates = relationship("Gate", back_populates="feature", cascade="all, delete-orphan")
