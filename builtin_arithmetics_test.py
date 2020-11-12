import unittest
from cmath import exp, cos, sin, pi
from itertools import product

import numpy as np
from numpy.testing import assert_allclose
from random import random, seed

from builtin_arithmetics import invert_gate, reduce_consecutive_u3
from builtin_gates import X_GATE, Y_GATE, Z_GATE, H_GATE, U3_GATE


def _u3(a: float, b: float, c: float) -> np.array:
    return np.array([
        [cos(a / 2), -exp(c * 1j) * sin(a / 2)],
        [exp(b * 1j) * sin(a / 2), exp((b + c) * 1j) * cos(a / 2)],
    ])


def _rand_ang() -> float:
    return random() * 4 * pi


class BuiltinArithmeticsTest(unittest.TestCase):

    def test_inverse_x(self) -> None:
        self.assertEqual(
            invert_gate(X_GATE, []),
            (X_GATE, []))

    def test_inverse_y(self) -> None:
        self.assertEqual(
            invert_gate(Y_GATE, []),
            (Y_GATE, []))

    def test_inverse_z(self) -> None:
        self.assertEqual(
            invert_gate(Z_GATE, []),
            (Z_GATE, []))

    def test_inverse_h(self) -> None:
        self.assertEqual(
            invert_gate(H_GATE, []),
            (H_GATE, []))

    def test_inverse_u3(self) -> None:
        self.assertEqual(
            invert_gate(U3_GATE, [0, 0, 0]),
            (U3_GATE, [0, 0, 0]))
        self.assertEqual(
            invert_gate(U3_GATE, [2.2, 3.3, 4.4]),
            (U3_GATE, [-2.2, -4.4, -3.3]))

    def test_conversion_random_angles(self) -> None:
        seed(7777)
        for test_id in range(20):
            a = _rand_ang()
            b = _rand_ang()
            c = _rand_ang()
            x = _rand_ang()
            y = _rand_ang()
            z = _rand_ang()
            self._test_conversion(a, b, c, x, y, z)

    def test_conversion_fixed_angles(self) -> None:
        angles_first = [0, pi / 4, pi / 2]
        angles_second = [0, pi / 2]
        for a, b, c in product(angles_first, repeat=3):
            for x, y, z in product(angles_second, repeat=3):
                self._test_conversion(a, b, c, x, y, z)

    def _test_conversion(self, a: float, b: float, c: float, x: float, y: float, z: float) -> None:
        u3_1 = _u3(a, b, c)
        u3_2 = _u3(x, y, z)
        expected = u3_1 @ u3_2
        conv_args = reduce_consecutive_u3(a, b, c, x, y, z)

        conv_matrix = exp(1j * conv_args[0]) * _u3(conv_args[1], conv_args[2], conv_args[3])
        assert_allclose(abs(conv_matrix - expected), 0, atol=1e-7)


if __name__ == '__main__':
    unittest.main()
