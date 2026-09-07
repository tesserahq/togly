from sqlalchemy.orm import Session

from app.models.feature import Feature
from app.repositories.feature_repository import FeatureRepository


class ListFeaturesQuery:
    def __init__(self, db: Session):
        self.db = db
        self.feature_repository = FeatureRepository(db)

    def execute(self) -> list[Feature]:
        return self.feature_repository.list_features()
