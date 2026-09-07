from sqlalchemy.orm import Session

from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.models.feature import Feature
from app.repositories.feature_repository import FeatureRepository


class GetFeatureQuery:
    def __init__(self, db: Session, key: str):
        self.db = db
        self.key = key
        self.feature_repository = FeatureRepository(db)

    def execute(self) -> Feature:
        feature = self.feature_repository.get_feature_by_key(self.key)
        if feature is None:
            raise ResourceNotFoundError(f"Feature with key {self.key!r} not found")
        return feature
