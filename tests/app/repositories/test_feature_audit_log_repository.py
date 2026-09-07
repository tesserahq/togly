from uuid import uuid4

from app.repositories.feature_audit_log_repository import FeatureAuditLogRepository


def test_create_and_list_by_feature_id(db, sample_feature, test_user):
    repo = FeatureAuditLogRepository(db)
    repo.create(
        feature_id=sample_feature.id,
        feature_key=sample_feature.key,
        user_id=test_user.id,
        action="created",
    )
    db.commit()

    entries = repo.list_by_feature_id(sample_feature.id)
    assert len(entries) == 1
    assert entries[0].feature_key == sample_feature.key


def test_audit_records_survive_after_feature_deletion(db, sample_feature, test_user):
    from app.repositories.feature_repository import FeatureRepository

    repo = FeatureAuditLogRepository(db)
    feature_id = sample_feature.id
    feature_key = sample_feature.key

    repo.create(
        feature_id=feature_id,
        feature_key=feature_key,
        user_id=test_user.id,
        action="created",
    )
    db.commit()

    FeatureRepository(db).delete_feature(sample_feature)
    db.commit()

    entries = repo.list_by_feature_id(feature_id)
    assert len(entries) == 1
    assert entries[0].feature_key == feature_key


def test_deleted_and_recreated_key_distinguished_by_feature_id(db, faker, test_user):
    from app.repositories.feature_repository import FeatureRepository

    feature_repo = FeatureRepository(db)
    audit_repo = FeatureAuditLogRepository(db)

    key = faker.slug()
    first = feature_repo.create_feature(key=key)
    db.commit()
    first_id = first.id
    audit_repo.create(
        feature_id=first_id, feature_key=key, user_id=test_user.id, action="created"
    )
    db.commit()

    feature_repo.delete_feature(first)
    db.commit()

    second = feature_repo.create_feature(key=key)
    db.commit()
    second_id = second.id
    audit_repo.create(
        feature_id=second_id, feature_key=key, user_id=test_user.id, action="created"
    )
    db.commit()

    assert first_id != second_id
    first_entries = audit_repo.list_by_feature_id(first_id)
    second_entries = audit_repo.list_by_feature_id(second_id)

    assert len(first_entries) == 1
    assert len(second_entries) == 1
    assert first_entries[0].feature_id == first_id
    assert second_entries[0].feature_id == second_id


def test_list_by_feature_id_empty_for_unknown_id(db):
    assert FeatureAuditLogRepository(db).list_by_feature_id(uuid4()) == []
