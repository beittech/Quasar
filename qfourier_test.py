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

from typing import Dict, Tuple

import unittest

from quasar import Program, Quasar
from qfourier import Fourier

#
##
#

class FourierTest(unittest.TestCase):

    def test_fourier(self) -> None:
        prgm = Program()
        qubits = prgm.Qubits([0, 0, 0, 0])
        prgm += Fourier(qubits)

        actual = Quasar().to_qasm_str(prgm)
        expected = (
            'OPENQASM 2.0;' + '\n' +
            'include "qelib1.inc";' + '\n' +
            ' ' + '\n' +
            'qreg q[4];' + '\n' +
            'creg c[0];' + '\n' +
            ' ' + '\n' +
            'h q[0];' + '\n' +
            'cu3(0, 0, 1.5707963267948966) q[1], q[0];' + '\n' +
            'cu3(0, 0, 0.7853981633974483) q[2], q[0];' + '\n' +
            'cu3(0, 0, 0.39269908169872414) q[3], q[0];' + '\n' +
            'h q[1];' + '\n' +
            'cu3(0, 0, 1.5707963267948966) q[2], q[1];' + '\n' +
            'cu3(0, 0, 0.7853981633974483) q[3], q[1];' + '\n' +
            'h q[2];' + '\n' +
            'cu3(0, 0, 1.5707963267948966) q[3], q[2];' + '\n' +
            'h q[3];' + '\n' +
            'cx q[0], q[3];' + '\n' +
            'cx q[3], q[0];' + '\n' +
            'cx q[0], q[3];' + '\n' +
            'cx q[1], q[2];' + '\n' +
            'cx q[2], q[1];' + '\n' +
            'cx q[1], q[2];'
        )

        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
