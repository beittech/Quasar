from cmath import exp, phase
from math import cos, sin, acos

from typing import List, Tuple

from builtin_gates import BuiltinGate, X_GATE, Y_GATE, Z_GATE, H_GATE, U3_GATE
from quasar_cmd import GateCmd


def invert_gate(gate: BuiltinGate, params: List[float]) -> Tuple[BuiltinGate, List[float]]:
    if gate in {X_GATE, Y_GATE, Z_GATE, H_GATE}:
        assert not params
        return gate, params
    if gate == U3_GATE:
        return U3_GATE, [
            -params[0],  # theta   ->  -theta
            -params[2],  # phi     ->  -lambda
            -params[1],  # lambda  ->  -phi
        ]
    raise NotImplementedError(f'Dont know how to invert {gate} {params}')


def check_commutation(cmd1: GateCmd, cmd2: GateCmd) -> bool:
    """ Returns True if two gates can be swapped with no change to the outcome. """
    # TODO(adsz): In future, it might be also beneficial to check commutation
    #  that alters the gates (with similar gate complexity).

    if cmd1 == cmd2:
        return True
    if not ((cmd1.get_control_qubit_ids() | {cmd1.get_target_qubit_id()}) &
            (cmd2.get_control_qubit_ids() | {cmd2.get_target_qubit_id()})):
        return True
    if cmd1.gate == Z_GATE and cmd2.gate == Z_GATE:
        return True
    if cmd1.gate == X_GATE and cmd2.gate == X_GATE:
        if cmd1.get_target_qubit_id() in cmd2.get_control_qubit_ids():
            return False
        elif cmd2.get_target_qubit_id() in cmd1.get_control_qubit_ids():
            return False
        else:
            return True
    # TODO(adsz): Two simplest rules as a starting point. Add more rules.

    return False


def is_zero(num: complex) -> bool:
    return abs(num) < 1e-9


def reduce_consecutive_u3(a: float, b: float, c: float, x: float, y: float, z: float) \
        -> Tuple[float, float, float, float]:
    """ Returns simplification parameters for two consecutive U3 gates. Given equation of a form:
                U3(a, b, c) * U3(x, y, z) = exp(1j * phi) * U3(alpha, beta, gamma),
        for given a, b, c, x, y, z - real numbers, function returns real phi, alpha, beta and gamma."""

    expcy = exp(1j * (c + y))

    s_sum = sin((a+x) / 2) * (1 + expcy) / 2
    s_sub = sin((a-x) / 2) * (1 - expcy) / 2
    c_sum = cos((a+x) / 2) * (1 + expcy) / 2
    c_sub = cos((a-x) / 2) * (1 - expcy) / 2

    elem1 = c_sum + c_sub
    elem2 = s_sum - s_sub
    elem3 = s_sum + s_sub
    elem4 = c_sum - c_sub

    phi = phase(elem1)
    alpha = 2 * acos(abs(elem1))
    if is_zero(elem2):  # any solution having beta + gamma = phase(elem4) - phi
        beta = 0.
        gamma = phase(elem4) + b + z - phi
    else:
        beta = phase(elem3) + b - phi
        gamma = phase(elem2) + z - phi

    return phi, alpha, beta, gamma
