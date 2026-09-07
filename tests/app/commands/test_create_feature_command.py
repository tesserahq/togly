from unittest.mock import patch

import pytest

from app.commands.feature.create_feature_command import CreateFeatureCommand
from app.exceptions.duplicate_resource_error import DuplicateResourceError
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.feature_repository import FeatureRepository
from app.schemas.feature import FeatureCreate


def test_create_feature_commits_mutation_and_audit_together(db, faker, test_user):
    key = faker.slug()
    feature = CreateFeatureCommand(db).execute(
        FeatureCreate(key=key, description="desc"), created_by=test_user
    )

    assert feature.key == key

    entries = FeatureAuditLogRepository(db).list_by_feature_id(feature.id)
    assert len(entries) == 1
    assert entries[0].action == "created"
    assert entries[0].feature_key == key


def test_duplicate_key_raises(db, sample_feature, test_user):
    with pytest.raises(DuplicateResourceError):
        CreateFeatureCommand(db).execute(
            FeatureCreate(key=sample_feature.key, description=None),
            created_by=test_user,
        )


def test_forced_audit_write_failure_rolls_back_the_mutation_too(db, faker, test_user):
    key = faker.slug()

    with patch(
        "app.repositories.feature_audit_log_repository.FeatureAuditLogRepository.create",
        side_effect=RuntimeError("simulated audit write failure"),
    ):
        with pytest.raises(RuntimeError):
            CreateFeatureCommand(db).execute(
                FeatureCreate(key=key, description="desc"), created_by=test_user
            )

    # The mutation must not exist either -- it was never committed independently.
    assert FeatureRepository(db).get_feature_by_key(key) is None
