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

from typing import Any, List, Set

import qiskit

from builtin_gates import BuiltinGate, X_GATE, Y_GATE, Z_GATE, H_GATE, U3_GATE
from quasar import IQAsmFormatter


#
##
#

class QiskitFormatter(IQAsmFormatter):
    GATES_MAPPING = {
        X_GATE: ['x', 'cx', 'ccx'],
        Y_GATE: ['y', 'cy'],
        Z_GATE: ['z', 'cz'],
        H_GATE: ['h', 'ch'],
        U3_GATE: ['u3', 'cu3'],
    }

    def get_headers(self) -> List[str]:
        return [
            f'self.q_register = qiskit.QuantumRegister({self.qubits_counter}, "q_register")',
            f'self.c_register = qiskit.ClassicalRegister({self.bits_counter}, "c_register")',
            f'self.circuit = qiskit.QuantumCircuit(self.q_register, self.c_register)'
        ]

    def get_footers(self) -> List[str]:
        return []

    def gate(self, gate: BuiltinGate, qubit: int, params: List[float], control_qubit_ids: Set[int]) -> str:
        method_name = self._get_for_gate(self.GATES_MAPPING, gate, len(control_qubit_ids))
        arguments: List[str] = []
        arguments.extend(map(str, params))
        arguments.extend(map(lambda i: f'self.q_register[{i}]', sorted(control_qubit_ids) + [qubit]))
        return f'self.circuit.{method_name}(' + ', '.join(arguments) + ')'

    def measure(self, qubit: int, bit: int) -> str:
        return f'self.circuit.measure(self.q_register[{qubit}], self.c_register[{bit}])'

    def reset(self, qubit: int) -> str:
        return f'self.reset(self.q_register[{qubit}])'

#
##
#

class QiskitBuilder(QiskitFormatter):
    def __init__(self) -> None:
        super().__init__()

        # These objects should not be really used,
        # the real ones are created in `get_headers`.
        self.q_register = qiskit.QuantumRegister(1, 'q_dummy_object')
        self.c_register = qiskit.ClassicalRegister(1, 'c_dummy_object')
        self.circuit = qiskit.QuantumCircuit(self.q_register, self.c_register)
        self._gates_mapping = self._build_gates_mapping()

    def _build_gates_mapping(self):
        return {
            X_GATE: [self.circuit.x, self.circuit.cx, self.circuit.ccx],
            Y_GATE: [self.circuit.y, self.circuit.cy],
            Z_GATE: [self.circuit.z, self.circuit.cz],
            H_GATE: [self.circuit.h, self.circuit.ch],
            U3_GATE: [self.circuit.u3, self.circuit.cu3],
        }

    def get_circuit(self):
        return self.circuit

    def get_headers(self) -> List[str]:
        self.q_register = qiskit.QuantumRegister(self.qubits_counter, 'q_register')
        self.c_register = qiskit.ClassicalRegister(self.bits_counter or 1, 'c_register')
        self.circuit = qiskit.QuantumCircuit(self.q_register, self.c_register)
        self._gates_mapping = self._build_gates_mapping()

        return super().get_headers()

    def get_footers(self) -> List[str]:
        return super().get_footers()

    def gate(self, gate: BuiltinGate, qubit: int, params: List[float], control_qubit_ids: Set[int]) -> str:
        method = self._get_for_gate(self._gates_mapping, gate, len(control_qubit_ids))
        arguments: List[Any] = []
        arguments.extend(params)
        arguments.extend(map(lambda i: self.q_register[i], sorted(control_qubit_ids) + [qubit]))
        method(*arguments)
        return super().gate(gate, qubit, params, control_qubit_ids)

    def measure(self, qubit: int, bit: int) -> str:
        self.circuit.measure(self.q_register[qubit], self.c_register[bit])
        return super().measure(qubit, bit)

    def reset(self, qubit: int) -> str:
        self.circuit.reset(self.q_register[qubit])
        return super().reset(qubit)
