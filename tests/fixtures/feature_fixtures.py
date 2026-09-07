import pytest

from app.models.feature import Feature
from app.models.gate import Gate, GateType


@pytest.fixture
def sample_feature(db, faker):
    feature = Feature(key=faker.slug(), description="A test feature")
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature


@pytest.fixture
def feature_with_boolean_gate(db, sample_feature):
    gate = Gate(feature_id=sample_feature.id, gate_type=GateType.BOOLEAN, value="true")
    db.add(gate)
    db.commit()
    db.refresh(sample_feature)
    return sample_feature
