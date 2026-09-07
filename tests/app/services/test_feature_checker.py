from uuid import uuid4

from app.models.gate import Gate, GateType
from app.services.feature_checker import is_enabled


def _gate(gate_type: GateType, value: str) -> Gate:
    return Gate(feature_id=uuid4(), gate_type=gate_type, value=value)


def test_no_gates_is_disabled():
    assert is_enabled([], actor_id=None) is False
    assert is_enabled([], actor_id="actor-1") is False


def test_boolean_gate_enabled_regardless_of_actor():
    gates = [_gate(GateType.BOOLEAN, "true")]
    assert is_enabled(gates, actor_id=None) is True
    assert is_enabled(gates, actor_id="actor-1") is True


def test_no_boolean_gate_and_no_actor_supplied_is_disabled():
    gates = [_gate(GateType.ACTOR, "actor-1")]
    assert is_enabled(gates, actor_id=None) is False


def test_matching_actor_gate_enables_without_boolean_gate():
    gates = [_gate(GateType.ACTOR, "actor-1")]
    assert is_enabled(gates, actor_id="actor-1") is True


def test_nonmatching_actor_gate_stays_disabled():
    gates = [_gate(GateType.ACTOR, "actor-1")]
    assert is_enabled(gates, actor_id="actor-2") is False


def test_boolean_and_actor_gates_combined():
    gates = [_gate(GateType.BOOLEAN, "true"), _gate(GateType.ACTOR, "actor-1")]
    assert is_enabled(gates, actor_id="actor-2") is True
    assert is_enabled(gates, actor_id=None) is True
