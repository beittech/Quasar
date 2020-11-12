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

from typing import List, Set

from builtin_gates import X_GATE, Y_GATE, Z_GATE, H_GATE, U3_GATE, BuiltinGate
from quasar_formatter import IQAsmFormatter


class QASMFormatter(IQAsmFormatter):
    GATES_MAPPING = {
        X_GATE: ['x', 'cx', 'ccx'],
        Y_GATE: ['y', 'cy'],
        Z_GATE: ['z', 'cz'],
        H_GATE: ['h', 'ch'],
        U3_GATE: ['u3', 'cu3'],
    }

    def get_headers(self) -> List[str]:
        return [
            f'OPENQASM 2.0;',
            f'include "qelib1.inc";',
            f' ',
            f'qreg q[{self.qubits_counter}];',
            f'creg c[{self.bits_counter}];',
            f' '
        ]

    def get_footers(self) -> List[str]:
        return []

    def gate(self, gate: BuiltinGate, qubit: int, params: List[float], control_qubit_ids: Set[int]) -> str:
        operator_name = self._get_for_gate(self.GATES_MAPPING, gate, len(control_qubit_ids))
        if params:
            operator_name += '(' + ', '.join(map(str, params)) + ')'
        return operator_name + ' ' + ', '.join(map(lambda i: f'q[{i}]', sorted(control_qubit_ids) + [qubit])) + ';'

    def measure(self, qubit: int, bit: int) -> str:
        return f'measure q[{qubit}] -> c[{bit}];'

    def reset(self, qubit: int) -> str:
        return f'reset q[{qubit}];'
