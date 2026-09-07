from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.models.feature import Feature
from app.repositories.feature_repository import FeatureRepository


def get_feature_by_key(key: str, db: Session = Depends(get_db)) -> Feature:
    """
    Dependency to get a feature by its unique key.
    Raises ResourceNotFoundError (mapped to 404) if not found.
    """
    feature = FeatureRepository(db).get_feature_by_key(key)
    if not feature:
        raise ResourceNotFoundError(f"Feature with key {key!r} not found")
    return feature


def get_actor_id_param(
    actor_id: str | None = Query(default=None, min_length=1),
) -> str | None:
    """
    Optional actor_id query parameter shared by Feature Check routes.
    A present-but-empty value is rejected with 422 by FastAPI's own
    validation; a genuinely absent value is a valid global-only check.
    """
    return actor_id
