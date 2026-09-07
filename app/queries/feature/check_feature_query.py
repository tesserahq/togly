from sqlalchemy.orm import Session

from app.repositories.feature_repository import FeatureRepository
from app.services.feature_checker import is_enabled


class CheckFeatureQuery:
    """Checks whether a single feature is enabled for an optional actor.

    Unknown feature keys are treated as disabled rather than an error, so
    client code can deploy a feature check before the feature is created.
    """

    def __init__(self, db: Session, key: str, actor_id: str | None):
        self.db = db
        self.key = key
        self.actor_id = actor_id
        self.feature_repository = FeatureRepository(db)

    def execute(self) -> bool:
        feature = self.feature_repository.get_feature_by_key(self.key)
        if feature is None:
            return False
        return is_enabled(feature.gates, self.actor_id)
