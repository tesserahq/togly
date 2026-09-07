from sqlalchemy.orm import Session

from app.repositories.feature_repository import FeatureRepository
from app.services.feature_checker import is_enabled


class ListEnabledFeaturesQuery:
    """Returns the keys of every feature enabled for an optional actor.

    Disabled features are omitted entirely rather than returned as a
    key-to-boolean map.
    """

    def __init__(self, db: Session, actor_id: str | None):
        self.db = db
        self.actor_id = actor_id
        self.feature_repository = FeatureRepository(db)

    def execute(self) -> list[str]:
        features = self.feature_repository.list_features()
        return [
            feature.key
            for feature in features
            if is_enabled(feature.gates, self.actor_id)
        ]
