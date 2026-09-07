from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.rbac import build_rbac_dependencies
from app.db import get_db
from app.queries.feature.get_feature_audit_log_query import GetFeatureAuditLogQuery
from app.schemas.feature import AuditLogEntryResponse

router = APIRouter(prefix="/feature-audit-logs", tags=["feature-audit-logs"])

rbac = build_rbac_dependencies(resource="feature_admin")


@router.get(
    "/{feature_id}",
    response_model=list[AuditLogEntryResponse],
    dependencies=[Depends(rbac["read"])],
)
def get_feature_audit_log(feature_id: UUID, db: Session = Depends(get_db)):
    return GetFeatureAuditLogQuery(db, feature_id).execute()
