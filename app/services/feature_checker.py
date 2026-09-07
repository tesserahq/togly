from collections.abc import Iterable

from app.models.gate import Gate, GateType


def is_enabled(gates: Iterable[Gate], actor_id: str | None) -> bool:
    """Pure evaluation of whether a feature is enabled.

    A feature is enabled when its boolean gate is on, or (if actor_id is
    supplied) it has an actor gate matching the requested actor. Actor gates
    never match without an actor to compare against. A feature with no
    matching gate is disabled.
    """
    has_boolean_gate = False
    for gate in gates:
        if gate.gate_type == GateType.BOOLEAN:
            has_boolean_gate = True
        elif (
            gate.gate_type == GateType.ACTOR
            and actor_id is not None
            and gate.value == actor_id
        ):
            return True

    return has_boolean_gate
