from unittest.mock import patch

import pytest

from app.commands.feature.disable_actor_gate_command import DisableActorGateCommand
from app.commands.feature.disable_boolean_gate_command import DisableBooleanGateCommand
from app.commands.feature.enable_actor_gate_command import EnableActorGateCommand
from app.commands.feature.enable_boolean_gate_command import EnableBooleanGateCommand
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository
from app.repositories.gate_repository import GateRepository


def test_enable_boolean_gate_commits_gate_and_audit(db, sample_feature, test_user):
    gate = EnableBooleanGateCommand(
        db, feature_key=sample_feature.key, current_user=test_user
    ).execute()

    assert GateRepository(db).get_boolean_gate(sample_feature.id).id == gate.id
    entries = FeatureAuditLogRepository(db).list_by_feature_id(sample_feature.id)
    assert entries[0].action == "boolean_enabled"


def test_disable_boolean_gate_commits_removal_and_audit(db, sample_feature, test_user):
    EnableBooleanGateCommand(
        db, feature_key=sample_feature.key, current_user=test_user
    ).execute()

    DisableBooleanGateCommand(
        db, feature_key=sample_feature.key, current_user=test_user
    ).execute()

    assert GateRepository(db).get_boolean_gate(sample_feature.id) is None
    entries = FeatureAuditLogRepository(db).list_by_feature_id(sample_feature.id)
    assert entries[0].action == "boolean_disabled"


def test_enable_actor_gate_commits_gate_and_audit(db, sample_feature, test_user):
    gate = EnableActorGateCommand(
        db, feature_key=sample_feature.key, actor_id="actor-1", current_user=test_user
    ).execute()

    assert GateRepository(db).get_actor_gate(sample_feature.id, "actor-1").id == gate.id
    entries = FeatureAuditLogRepository(db).list_by_feature_id(sample_feature.id)
    assert entries[0].action == "actor_enabled"
    assert entries[0].snapshot == {"actor_id": "actor-1"}


def test_disable_actor_gate_commits_removal_and_audit(db, sample_feature, test_user):
    EnableActorGateCommand(
        db, feature_key=sample_feature.key, actor_id="actor-1", current_user=test_user
    ).execute()

    DisableActorGateCommand(
        db, feature_key=sample_feature.key, actor_id="actor-1", current_user=test_user
    ).execute()

    assert GateRepository(db).get_actor_gate(sample_feature.id, "actor-1") is None
    entries = FeatureAuditLogRepository(db).list_by_feature_id(sample_feature.id)
    assert entries[0].action == "actor_disabled"


def test_enable_boolean_gate_unknown_feature_raises_not_found(db, test_user):
    with pytest.raises(ResourceNotFoundError):
        EnableBooleanGateCommand(
            db, feature_key="does-not-exist", current_user=test_user
        ).execute()


def test_forced_audit_write_failure_rolls_back_gate_mutation_too(db, faker, test_user):
    from app.repositories.feature_repository import FeatureRepository

    # Flushed (not committed) so this stays part of the same transaction the
    # forced rollback below reverts -- proving the gate mutation never
    # survives without its audit record, not just that both usually succeed.
    feature = FeatureRepository(db).create_feature(key=faker.slug())
    feature_id = feature.id
    feature_key = feature.key

    with patch(
        "app.repositories.feature_audit_log_repository.FeatureAuditLogRepository.create",
        side_effect=RuntimeError("simulated audit write failure"),
    ):
        with pytest.raises(RuntimeError):
            EnableBooleanGateCommand(
                db, feature_key=feature_key, current_user=test_user
            ).execute()

    assert GateRepository(db).get_boolean_gate(feature_id) is None
    assert FeatureRepository(db).get_feature(feature_id) is None
