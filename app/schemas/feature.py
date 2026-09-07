from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.gate import GateType


class FeatureCreate(BaseModel):
    key: str = Field(min_length=1)
    description: str | None = None


class GateResponse(BaseModel):
    id: UUID
    gate_type: GateType
    value: str

    model_config = {"from_attributes": True}


class FeatureResponse(BaseModel):
    id: UUID
    key: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    gates: list[GateResponse] = []

    model_config = {"from_attributes": True}


class AuditLogEntryResponse(BaseModel):
    id: UUID
    feature_id: UUID
    feature_key: str
    user_id: UUID
    action: str
    snapshot: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeatureCheckResponse(BaseModel):
    key: str
    enabled: bool


class EnabledFeaturesResponse(BaseModel):
    features: list[str]
