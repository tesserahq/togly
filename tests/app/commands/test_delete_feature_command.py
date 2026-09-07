import pytest

from app.commands.feature.delete_feature_command import DeleteFeatureCommand
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.feature_repository import FeatureRepository
from app.schemas.feature import FeatureKey


def test_delete_feature_commits_deletion_and_audit(db, sample_feature, test_user):
    feature_id = sample_feature.id
    feature_key = sample_feature.key

    DeleteFeatureCommand(db).execute(FeatureKey(key=feature_key), deleted_by=test_user)

    assert FeatureRepository(db).get_feature(feature_id) is None
    entries = FeatureAuditLogRepository(db).list_by_feature_id(feature_id)
    assert len(entries) == 1
    assert entries[0].action == "deleted"
    assert entries[0].feature_key == feature_key


def test_delete_unknown_feature_raises_not_found(db, test_user):
    with pytest.raises(ResourceNotFoundError):
        DeleteFeatureCommand(db).execute(
            FeatureKey(key="does-not-exist"), deleted_by=test_user
        )
