import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories.feature_repository import FeatureRepository


def test_create_feature(db, faker):
    key = faker.slug()
    feature = FeatureRepository(db).create_feature(key=key, description="desc")
    db.commit()

    assert feature.id is not None
    assert feature.key == key
    assert feature.description == "desc"


def test_feature_key_uniqueness_enforced(db, sample_feature):
    with pytest.raises(IntegrityError):
        FeatureRepository(db).create_feature(key=sample_feature.key)
    db.rollback()


def test_get_feature_by_key(db, sample_feature):
    found = FeatureRepository(db).get_feature_by_key(sample_feature.key)
    assert found is not None
    assert found.id == sample_feature.id


def test_get_feature_by_key_not_found(db):
    assert FeatureRepository(db).get_feature_by_key("does-not-exist") is None


def test_list_features(db, sample_feature):
    features = FeatureRepository(db).list_features()
    assert any(f.id == sample_feature.id for f in features)


def test_delete_feature_cascades_gates(db, feature_with_boolean_gate):
    from app.models.gate import Gate

    feature_id = feature_with_boolean_gate.id
    FeatureRepository(db).delete_feature(feature_with_boolean_gate)
    db.commit()

    assert FeatureRepository(db).get_feature(feature_id) is None
    assert db.query(Gate).filter(Gate.feature_id == feature_id).count() == 0
