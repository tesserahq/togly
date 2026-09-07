from app.models.gate import GateType
from app.repositories.gate_repository import GateRepository


def test_enable_boolean_gate_is_idempotent(db, sample_feature):
    repo = GateRepository(db)
    gate1 = repo.enable_boolean_gate(sample_feature.id)
    gate2 = repo.enable_boolean_gate(sample_feature.id)
    db.commit()

    assert gate1.id == gate2.id
    assert (
        db.query(type(gate1))
        .filter_by(feature_id=sample_feature.id, gate_type=GateType.BOOLEAN)
        .count()
        == 1
    )


def test_disable_boolean_gate_removes_row(db, sample_feature):
    repo = GateRepository(db)
    repo.enable_boolean_gate(sample_feature.id)
    db.commit()

    removed = repo.disable_boolean_gate(sample_feature.id)
    db.commit()

    assert removed is True
    assert repo.get_boolean_gate(sample_feature.id) is None


def test_disable_boolean_gate_missing_returns_false(db, sample_feature):
    assert GateRepository(db).disable_boolean_gate(sample_feature.id) is False


def test_enable_actor_gate_is_idempotent(db, sample_feature):
    repo = GateRepository(db)
    gate1 = repo.enable_actor_gate(sample_feature.id, "actor-1")
    gate2 = repo.enable_actor_gate(sample_feature.id, "actor-1")
    db.commit()

    assert gate1.id == gate2.id


def test_actor_gates_are_scoped_per_actor(db, sample_feature):
    repo = GateRepository(db)
    repo.enable_actor_gate(sample_feature.id, "actor-1")
    repo.enable_actor_gate(sample_feature.id, "actor-2")
    db.commit()

    assert repo.get_actor_gate(sample_feature.id, "actor-1") is not None
    assert repo.get_actor_gate(sample_feature.id, "actor-2") is not None

    removed = repo.disable_actor_gate(sample_feature.id, "actor-1")
    db.commit()

    assert removed is True
    assert repo.get_actor_gate(sample_feature.id, "actor-1") is None
    assert repo.get_actor_gate(sample_feature.id, "actor-2") is not None
