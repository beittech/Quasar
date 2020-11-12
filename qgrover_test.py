#
# Copyright (c) 2019- Beit, Beit.Tech, Beit.Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from typing import Dict, List, Tuple

import unittest

from quasar import Quasar, Match, Program
from qgrover import Grover

#
##
#

class GroverTest(unittest.TestCase):

    def test_grover(self) -> None:
        input_mask = (1, 0, 1)
        prgm = Program()
        qubits = prgm.Qubits([0, 0, 0])
        prgm += Grover(qubits, predicate=Match(qubits, mask=input_mask))

        actual = Quasar().to_qasm_str(prgm)
        expected = (
            'OPENQASM 2.0;' + '\n'
            'include "qelib1.inc";' + '\n'
            ' ' + '\n'
            'qreg q[4];' + '\n'
            'creg c[0];' + '\n'
            ' ' + '\n'
            'h q[0];' + '\n'
            'h q[1];' + '\n'
            'h q[2];' + '\n'
            'x q[1];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'cz q[2], q[3];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'x q[1];' + '\n'
            'h q[0];' + '\n'
            'h q[1];' + '\n'
            'h q[2];' + '\n'
            'x q[0];' + '\n'
            'x q[1];' + '\n'
            'x q[2];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'cz q[2], q[3];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'x q[2];' + '\n'
            'x q[1];' + '\n'
            'x q[0];' + '\n'
            'h q[0];' + '\n'
            'h q[1];' + '\n'
            'h q[2];' + '\n'
            'z q[0];' + '\n'
            'x q[0];' + '\n'
            'z q[0];' + '\n'
            'x q[0];' + '\n'
            'x q[1];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'cz q[2], q[3];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'x q[1];' + '\n'
            'h q[0];' + '\n'
            'h q[1];' + '\n'
            'h q[2];' + '\n'
            'x q[0];' + '\n'
            'x q[1];' + '\n'
            'x q[2];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'cz q[2], q[3];' + '\n'
            'ccx q[0], q[1], q[3];' + '\n'
            'x q[2];' + '\n'
            'x q[1];' + '\n'
            'x q[0];' + '\n'
            'h q[0];' + '\n'
            'h q[1];' + '\n'
            'h q[2];' + '\n'
            'z q[0];' + '\n'
            'x q[0];' + '\n'
            'z q[0];' + '\n'
            'x q[0];'
        )

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
