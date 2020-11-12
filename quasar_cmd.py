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
from typing import List, Optional, Set

from builtin_gates import BuiltinGate, builtin_repr
from quasar_formatter import IQAsmFormatter

#
##
#

class ICmdVisitable(ABC):
    @abstractmethod
    def accept(self, visitor: 'ICmdVisitor') -> Optional['ICommand']:
        pass

#
##
#

class ICommand(ICmdVisitable):
    @abstractmethod
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        pass

    @abstractmethod
    def get_target_qubit_id(self) -> int:
        pass


class GateCmd(ICommand):
    def __init__(
        self,
        gate: BuiltinGate,
        target_qubit_id: int,
        control_qubit_ids: Set[int] = None,
        params: List[float] = None,
    ) -> None:
        self._gate = gate
        self._target_qubit_id = target_qubit_id
        self._params = params or []
        self._control_qubit_ids = control_qubit_ids or set()

    def __eq__(self, other):
        if not isinstance(other, GateCmd):
            return False
        return (self._gate, self._target_qubit_id, self._params, self._control_qubit_ids) \
            == (other._gate, other._target_qubit_id, other._params, other._control_qubit_ids)

    @property
    def gate(self) -> BuiltinGate:
        return self._gate

    def get_target_qubit_id(self) -> int:
        return self._target_qubit_id

    def get_control_qubit_ids(self) -> Set[int]:
        return self._control_qubit_ids

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [qasm_formatter.gate(self._gate, self._target_qubit_id, self._params, self._control_qubit_ids)]

    def accept(self, visitor: 'ICmdVisitor') -> None:
        visitor.on_gate(self)

    def __repr__(self):
        s = f'GateCmd({builtin_repr(self._gate)}, {self._target_qubit_id}'
        if self._control_qubit_ids:
            s += f', {repr(self._control_qubit_ids)}'
        if self._params:
            if not self._control_qubit_ids:
                s += f', set()'
        s += ')'
        return s


class MeasurementCmd(ICommand):
    def __init__(
        self,
        qubit_id: int,
        bit_id: int
    ) -> None:
        self._qubit_id = qubit_id
        self._bit_id = bit_id

    def get_target_qubit_id(self) -> int:
        return self._qubit_id

    def get_target_bit_id(self) -> int:
        return self._bit_id

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [
            qasm_formatter.measure(self._qubit_id, self._bit_id)
        ]

    def accept(self, visitor: 'ICmdVisitor') -> None:
        visitor.on_measurement(self)


class ResetCmd(ICommand):
    def __init__(
        self,
        qubit_id: int
    ) -> None:
        self._qubit_id = qubit_id

    def get_target_qubit_id(self) -> int:
        return self._qubit_id

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        lines = qasm_formatter.reset(self._qubit_id).split('\n')
        return [line for line in lines]

    def accept(self, visitor: 'ICmdVisitor') -> None:
        visitor.on_reset(self)

#
##
#

class ICmdVisitor(ABC):
    @abstractmethod
    def on_program(self, commands: List[ICommand]) -> None:
        for command in commands:
            command.accept(self)

    @abstractmethod
    def on_gate(self, cmd: GateCmd) -> None:
        pass

    @abstractmethod
    def on_measurement(self, m: MeasurementCmd) -> None:
        pass

    @abstractmethod
    def on_reset(self, reset: ResetCmd) -> None:
        pass
