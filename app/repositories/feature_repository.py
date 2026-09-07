from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.feature import Feature


class FeatureRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_feature(self, key: str, description: str | None = None) -> Feature:
        feature = Feature(key=key, description=description)
        self.db.add(feature)
        self.db.flush()
        return feature

    def get_feature(self, feature_id: UUID) -> Feature | None:
        return (
            self.db.query(Feature)
            .options(joinedload(Feature.gates))
            .filter(Feature.id == feature_id)
            .first()
        )

    def get_feature_by_key(self, key: str) -> Feature | None:
        return (
            self.db.query(Feature)
            .options(joinedload(Feature.gates))
            .filter(Feature.key == key)
            .first()
        )

    def list_features(self) -> list[Feature]:
        return self.db.query(Feature).options(joinedload(Feature.gates)).all()

    def delete_feature(self, feature: Feature) -> None:
        self.db.delete(feature)
        self.db.flush()
