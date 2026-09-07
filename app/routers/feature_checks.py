from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.rbac import actor_domain, build_rbac_dependencies
from app.db import get_db
from app.queries.feature.check_feature_query import CheckFeatureQuery
from app.queries.feature.list_enabled_features_query import ListEnabledFeaturesQuery
from app.schemas.feature import EnabledFeaturesResponse, FeatureCheckResponse

router = APIRouter(tags=["feature-checks"])

rbac = build_rbac_dependencies(resource="feature_check", domain_resolver=actor_domain)


@router.get(
    "/feature-checks/{key}",
    response_model=FeatureCheckResponse,
    dependencies=[Depends(rbac["read"])],
)
def check_feature(
    key: str,
    actor_id: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    enabled = CheckFeatureQuery(db, key=key, actor_id=actor_id).execute()
    return FeatureCheckResponse(key=key, enabled=enabled)


@router.get(
    "/enabled-features",
    response_model=EnabledFeaturesResponse,
    dependencies=[Depends(rbac["read"])],
)
def list_enabled_features(
    actor_id: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    features = ListEnabledFeaturesQuery(db, actor_id=actor_id).execute()
    return EnabledFeaturesResponse(features=features)
