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

from abc import abstractmethod, ABC
from typing import List, Set, TypeVar, Dict

from builtin_gates import BuiltinGate


class IQAsmFormatter(ABC):
    def __init__(self):
        self.qubits_counter = 0
        self.bits_counter = 0
        self.groups : List[int] = []

    def set_qubits_counter(self, qubits_counter: int):
        self.qubits_counter = qubits_counter

    def set_bits_counter(self, bits_counter: int):
        self.bits_counter = bits_counter

    def set_groups(self, groups: List[int]):
        self.groups = groups

    @abstractmethod
    def get_headers(self) -> List[str]:
        pass

    @abstractmethod
    def get_footers(self) -> List[str]:
        pass

    @abstractmethod
    def gate(self, gate: BuiltinGate, qubit: int, params: List[float], control_qubit_ids: Set[int]) -> str:
        pass

    @abstractmethod
    def measure(self, qubit: int, bit: int) -> str:
        pass

    @abstractmethod
    def reset(self, qubit: int) -> str:
        pass

    T = TypeVar('T')
    def _get_for_gate(self, mapping: Dict[BuiltinGate, List[T]], gate: BuiltinGate, num_controls: int) -> T:
        if gate not in mapping:
            raise ValueError(f'Gate {gate} not supported')
        if len(mapping[gate]) < num_controls:
            raise ValueError(f'Gate {gate} cannot have at max {num_controls} control qubits.')
        return mapping[gate][num_controls]

