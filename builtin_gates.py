""" This file defines the only gates that are supported by
the QCompiler natively. This list should be kept minimal, as adding new gate
would require implementing its behavior and interaction with others.
In fact, sole U3 should be enough, however others like X, Z are added for easier use.
Whenever handling the builtin gate, prefer referring to the `BuiltinGate` object
instead of its name -- to emphasize its builtinness.
All control gates (by any number of qubits) are builtins implicitly."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BuiltinGate:
    name: str
    num_params: int


X_GATE = BuiltinGate('X', 0)
Y_GATE = BuiltinGate('Y', 0)
Z_GATE = BuiltinGate('Z', 0)
H_GATE = BuiltinGate('H', 0)
U3_GATE = BuiltinGate('U3', 3)

def builtin_repr(gate: BuiltinGate) -> str:
    return f'{gate.name}_GATE'
