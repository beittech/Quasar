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

#
##
#

from abc import abstractmethod, ABC
from math import asin, pi, sqrt
from typing import cast, Callable, Dict, Iterable, List, Optional, Type, Union
from itertools import chain

import typing

#
##
#

def to_list(obj: Union[typing.Any, List[typing.Any]]) -> List[typing.Any]:
    if isinstance(obj, list):
        return obj
    else:
        return to_list([obj])

#
##
#

class _IVisitable(ABC):
    @abstractmethod
    def _accept(self, visitor: '_ASTVisitor') -> Optional['_ASTNode']:
        pass

#
##
#

class Counter:
    def __init__(self) -> None:
        self.counter = 0

    def __str__(self) -> str:
        return str(self.counter)


class DepthGuard:
    def __init__(self, counter: Counter) -> None:
        self.counter = counter

    def __enter__(self) -> None:
        self.counter.counter += 1

    def __exit__(self, type, value, traceback) -> None:
        self.counter.counter -= 1

#
##
#

class IQAsmFormatter(ABC):
    @abstractmethod
    def comment(self, text: str) -> str:
        pass

    @abstractmethod
    def get_headers(self, qubits: int, groups: List[int], bits: int) -> List[str]:
        pass

    @abstractmethod
    def get_footers(self) -> List[str]:
        pass

    @abstractmethod
    def x(self, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def cx(self, control_qubit: int, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def ccx(self, control_qubit_id_1: int, control_qubit_id_2: int, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def y(self, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def cy(self, control_qubit_id: int, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def z(self, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def cz(self, control_qubit_id: int, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def h(self, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def ch(self, control_qubit_id: int, target_qubit_id: int) -> str:
        pass

    @abstractmethod
    def u3(self, target_qubit_id: int, arg1: float, arg2: float, arg3: float) -> str:
        pass

    @abstractmethod
    def cu3(self, control_qubit_id: int, target_qubit_id: int, arg1: float, arg2: float, arg3: float) -> str:
        pass

    @abstractmethod
    def measure(self, qubit: int, bit: int) -> str:
        pass


class QiskitFormatter(IQAsmFormatter):
    def __init__(self) -> None:
        self.q_registers = None
        self.q_circuit = None

    def get_quantum_register(self):
        return self.q_registers

    def get_quantum_circuit(self):
        return self.q_circuit

    def comment(self, text: str) -> str:
        return '# ' + text

    def get_headers(self, qubits: int, groups: List[int], bits: int) -> List[str]:
        # self.q_registers = qiskit.QuantumRegister(qubits, 'q_registers')
        # self.q_circuit = qiskit.QuantumCircuit(self.q_registers)

        return [
            f'self.q_registers = qiskit.QuantumRegister({qubits}, "q_registers")',
            f'self.c_register = qiskit.ClassicalRegister({bits}, "c_register")',
            f'self.q_circuit = qiskit.QuantumCircuit(self.q_registers)'
        ]

    def get_footers(self) -> List[str]:
        return []

    def x(self, target_qubit_id: int) -> str:
        return f'self.q_circuit.x(self.q_registers[{target_qubit_id}])'

    def cx(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'self.q_circuit.cx(self.q_registers[{control_qubit_id}], self.q_registers[{target_qubit_id}])'

    def ccx(self, control_qubit_id_1: int, control_qubit_id_2: int, target_qubit_id: int) -> str:
        return (
            f'self.q_circuit.ccx(self.q_registers[{control_qubit_id_1}], ' +
            f'self.q_registers[{control_qubit_id_2}], ' +
            f'self.q_registers[{target_qubit_id}])'
        )

    def y(self, target_qubit_id: int) -> str:
        return f'self.q_circuit.y(self.q_registers[{target_qubit_id}])'

    def cy(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'self.q_circuit.cy(self.q_registers[{control_qubit_id}], self.q_registers[{target_qubit_id}])'

    def z(self, target_qubit_id: int) -> str:
        return f'self.q_circuit.z(self.q_registers[{target_qubit_id}])'

    def cz(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'self.q_circuit.cz(self.q_registers[{control_qubit_id}], self.q_registers[{target_qubit_id}])'

    def h(self, target_qubit_id: int) -> str:
        return f'self.q_circuit.h(self.q_registers[{target_qubit_id}])'

    def ch(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'self.q_circuit.ch(self.q_registers[{control_qubit_id}], self.q_registers[{target_qubit_id}])'

    def u3(self, target_qubit_id: int, arg1: float, arg2: float, arg3: float) -> str:
        return (
            f'self.q_circuit.u3({arg1}, {arg2}, {arg3}, ' +
            f'self.q_registers[{target_qubit_id}]' +
            f')'
        )

    def cu3(self, control_qubit_id: int, target_qubit_id: int, arg1: float, arg2: float, arg3: float) -> str:
        return (
            f'self.q_circuit.cu3({arg1}, {arg2}, {arg3}, ' +
            f'self.q_registers[{control_qubit_id}], ' +
            f'self.q_registers[{target_qubit_id}]' +
            f')'
        )

    def measure(self, qubit: int, bit: int) -> str:
        return f'self.q_circuit.measure(self.q_registers[{qubit}], self.c_register[{bit}])'


class QASMFormatter(IQAsmFormatter):
    def __init__(self) -> None:
        pass

    def get_quantum_register(self):
        pass

    def get_quantum_circuit(self):
        pass

    def comment(self, text: str) -> str:
        return '// ' + text

    def get_headers(self, qubits_size: int, groups: List[int], bits_size: int) -> List[str]:
        return [
            f'OPENQASM 2.0;',
            f'include "qelib1.inc";',
            f' ',
            f'qreg q_registers[{qubits_size}];',
            f'creg c_registers[{bits_size}];',
            f' '
        ]

    def get_footers(self) -> List[str]:
        return []

    def x(self, target_qubit_id: int) -> str:
        return f'x q_registers[{target_qubit_id}];'

    def cx(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'cx q_registers[{control_qubit_id}], q_registers[{target_qubit_id}];'

    def ccx(self, control_qubit_id_1: int, control_qubit_id_2: int, target_qubit_id: int) -> str:
        return f'ccx q_registers[{control_qubit_id_1}], q_registers[{control_qubit_id_2}], q_registers[{target_qubit_id}];'

    def y(self, target_qubit_id: int) -> str:
        return f'y q_registers[{target_qubit_id}];'

    def cy(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'cy q_registers[{control_qubit_id}], q_registers[{target_qubit_id}];'

    def z(self, target_qubit_id: int) -> str:
        return f'z q_registers[{target_qubit_id}];'

    def cz(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'cz q_registers[{control_qubit_id}], q_registers[{target_qubit_id}];'

    def h(self, target_qubit_id: int) -> str:
        return f'h q_registers[{target_qubit_id}];'

    def ch(self, control_qubit_id: int, target_qubit_id: int) -> str:
        return f'ch q_registers[{control_qubit_id}], q_registers[{target_qubit_id}];'

    def u3(self, target_qubit_id: int, arg1: float, arg2: float, arg3: float) -> str:
        return f'u3({arg1}, {arg2}, {arg3}), q_registers[{target_qubit_id}];'

    def cu3(self, control_qubit_id: int, target_qubit_id: int, arg1: float, arg2: float, arg3: float) -> str:
        return (
            f'cu3({arg1}, {arg2}, {arg3}), ' +
            f'q_registers[{control_qubit_id}], ' +
            f'.q_registers[{target_qubit_id}];'
        )

    def measure(self, qubit: int, bit: int) -> str:
        return f'measure q_registers[{qubit}] -> c_register[{bit}];'

#
##
#

class _ASTNode(_IVisitable):
    def __init__(self) -> None:
        self._target_qubit_ids : List[int] = []

        self._control_positive_qubit_ids : List[int] = []
        self._control_negative_qubit_ids : List[int] = []

        self._parents_control_positive_qubit_ids : List[int] = []
        self._parents_control_negative_qubit_ids : List[int] = []

        self._ancilla_qubit_ids : List[int] = []

    def __add__(self, other: Union['_ASTNode', List['_ASTNode'], '_Program']) -> '_Program':
        if (isinstance(other, _ASTNode)):
            return _Program([self] + [other])

        elif (isinstance(other, list)):
            return _Program([self] + other)

        elif (isinstance(other, _Program)):
            return _Program([self] + other._nodes)

        raise Exception(f'Unknown type {type(other)}')

    def _set_target_qubit_ids(self, _target_qubit_ids: List[int]) -> None:
        self._target_qubit_ids = _target_qubit_ids

    def _get_target_qubit_ids(self) -> List[int]:
        return self._target_qubit_ids

    def _set_parents_control_positive_qubit_ids(self, parents_control_positive_qubit_ids: List[int]) -> None:
        self._parents_control_positive_qubit_ids = parents_control_positive_qubit_ids

    def _get_parents_control_positive_qubit_ids(self) -> List[int]:
        return self._parents_control_positive_qubit_ids

    def _set_parents_control_negative_qubit_ids(self, parents_control_negative_qubit_ids: List[int]) -> None:
        self._parents_control_negative_qubit_ids = parents_control_negative_qubit_ids

    def _get_parents_control_negative_qubit_ids(self) -> List[int]:
        return self._parents_control_negative_qubit_ids

    def _set_ancilla_qubit_ids(self, ancilla_qubit_ids: List[int]):
        self._ancilla_qubit_ids = ancilla_qubit_ids

    def _get_ancilla_qubit_ids(self) -> List[int]:
        return self._ancilla_qubit_ids

    @staticmethod
    @abstractmethod
    def _get_label() -> str:
        pass


class _Program:
    @staticmethod
    def _get_label() -> str:
        return 'PROGRAM'

    def __init__(self, other: Optional[Union[_ASTNode, List[_ASTNode], '_Program']] = None) -> None:
        self._nodes : List[_ASTNode] = []

        if isinstance(other, _Program):
            self._nodes = other._nodes or []

        if isinstance(other, _ASTNode):
            self._nodes = [other]

        if isinstance(other, list):
            self._nodes = other or []

    def __add__(self, other: Union[_ASTNode, List[_ASTNode], '_Program']) -> '_Program':
        if (isinstance(other, _ASTNode)):
            return _Program(self._nodes + [other])

        elif (isinstance(other, list)):
            return _Program(self._nodes + other)

        elif (isinstance(other, _Program)):
            return _Program(self._nodes + other._nodes)

        else:
            raise Exception(f'Unknown type {type(other)}')

    def __iadd__(self, other: Union[_ASTNode, List[_ASTNode], '_Program']) -> '_Program':
        if (isinstance(other, _ASTNode)):
            self._nodes.append(other)
            return self

        elif (isinstance(other, list)):
            self._nodes.extend(other)
            return self

        elif (isinstance(other, _Program)):
            self._nodes.extend(other._nodes)
            return self

        else:
            raise Exception(f'Unknown type {type(other)}')

    def __getitem__(self, index: int) -> _ASTNode:
        return self._nodes[index]

    def __len__(self) -> int:
        return len(self._nodes)

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_program(self)

    def Qubit(self, init=0) -> '_QubitNode':
        qubit = _QubitNode(init)
        self._nodes.append(qubit)
        return qubit

    def Qubits(self, inits: Iterable[int]) -> List['_QubitNode']:
        return [self.Qubit(init) for init in inits]

    def CBit(self) -> '_CBitNode':
        cbit = _CBitNode()
        self._nodes.append(cbit)
        return cbit

    def CBits(self, size: int) -> List['_CBitNode']:
        return [self.CBit() for i in range(size)]


class _QubitNode(_ASTNode):
    _qubit_counter = 0

    def __init__(self, init: int) -> None:
        super().__init__()
        self._name = f'$$_qubit_{_QubitNode._get_qvar_counter()}'
        self._init = init

    def _get_name(self) -> str:
        return self._name

    def _get_init(self) -> int:
        return self._init

    def _set_target_qubit_ids(self, _target_qubit_ids: List[int]) -> None:
        super()._set_target_qubit_ids(_target_qubit_ids)
        self._size = len(_target_qubit_ids)

    def _get_size(self) -> int:
        return 1

    @staticmethod
    def _get_label() -> str:
        return 'QUBIT'

    @staticmethod
    def _get_qvar_counter() -> int:
        _QubitNode._qubit_counter += 1
        return _QubitNode._qubit_counter

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_qubit(self)


class _CBitNode(_ASTNode):
    _cbit_counter = 0

    def __init__(self) -> None:
        super().__init__()
        self._name = f'$$_cbit_{_CBitNode._get_cvar_counter()}'
        self._target_bit_ids : List[int] = []

    def _get_name(self) -> str:
        return self._name

    def _set_target_bit_ids(self, target_bit_ids: List[int]) -> None:
        self._target_bit_ids = target_bit_ids
        self._size = len(target_bit_ids)

    def _get_target_bit_ids(self) -> List[int]:
        return self._target_bit_ids

    def _get_size(self) -> int:
        return 1

    @staticmethod
    def _get_label() -> str:
        return 'CBIT'

    @staticmethod
    def _get_cvar_counter() -> int:
        _CBitNode._cbit_counter += 1
        return _CBitNode._cbit_counter

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_cvar(self)


class _InvNode(_ASTNode):
    def __init__(self, node: Union[_ASTNode, List[_ASTNode], _Program]) -> None:
        super().__init__()
        self._body : _Program = _Program(node)

    def _get_body(self) -> _Program:
        return self._body

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_inv(self)

    @staticmethod
    def _get_label() -> str:
        return 'INV'


class _IfASTNode(_ASTNode):
    def __init__(
        self,
        condition: Union[_ASTNode, List[_ASTNode], _Program],
        then_body: Union[_ASTNode, List[_ASTNode], _Program],
    ) -> None:
        super().__init__()
        self._condition = _Program(condition)
        self._then_body = _Program(then_body)

    def _get_condition(self) -> _Program:
        return self._condition

    def _get_then_body(self) -> _Program:
        return self._then_body

    @staticmethod
    def _get_label() -> str:
        return 'IF'


class _IfThenElseNode(_IfASTNode):
    def __init__(
        self,
        condition: Union[_ASTNode, List[_ASTNode], _Program],
        then_body: Union[_ASTNode, List[_ASTNode], _Program],
        else_body: Union[_ASTNode, List[_ASTNode], _Program]
    ) -> None:
        super().__init__(condition, then_body)
        self._else_body = _Program(else_body)

    def _get_else_body(self) -> _Program:
        return self._else_body

    def _set_control_positive_qubit_ids(self, control_positive_qubit_ids: List[int]) -> None:
        self._control_positive_qubit_ids = control_positive_qubit_ids

    def _get_control_positive_qubit_ids(self) -> List[int]:
        return self._control_positive_qubit_ids

    def _set_control_negative_qubit_ids(self, control_negative_qubit_ids: List[int]) -> None:
        self._control_negative_qubit_ids = control_negative_qubit_ids

    def _get_control_negative_qubit_ids(self) -> List[int]:
        return self._control_negative_qubit_ids

    @staticmethod
    def _get_label() -> str:
        return 'IF_THEN_ELSE'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_if_then_else(self)


class _IfThenNode(_IfASTNode):
    def __init__(
        self,
        expression: Union[_ASTNode, List[_ASTNode], _Program],
        then_body: Union[_ASTNode, List[_ASTNode], _Program]
    ) -> None:
        super().__init__(expression, then_body)

    def Else(self, else_body: Union[_ASTNode, List[_ASTNode]]) -> _IfThenElseNode:
        return _IfThenElseNode(self._condition, self._then_body, else_body)

    def _set_control_positive_qubit_ids(self, control_positive_qubit_ids: List[int]) -> None:
        self._control_positive_qubit_ids = control_positive_qubit_ids

    def _get_control_positive_qubit_ids(self) -> List[int]:
        return self._control_positive_qubit_ids

    @staticmethod
    def _get_label() -> str:
        return 'IF_THEN'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_if_then(self)


class _IfFlipNode(_ASTNode):
    def __init__(self, condition: Union[_ASTNode, List[_ASTNode], _Program]) -> None:
        super().__init__()
        self._condition = _Program(condition)

    def _get_condition(self) -> _Program:
        return self._condition

    def _set_control_positive_qubit_ids(self, control_positive_qubit_ids: List[int]) -> None:
        self._control_positive_qubit_ids = control_positive_qubit_ids

    def _get_control_positive_qubit_ids(self) -> List[int]:
        return self._control_positive_qubit_ids

    @staticmethod
    def _get_label() -> str:
        return 'IF_FLIP'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_if_flip(self)


class _IfNode(_ASTNode):
    def __init__(self, expression: Union[_ASTNode, List[_ASTNode], _Program]) -> None:
        super().__init__()
        self._expression = _Program(expression)

    def Then(
        self,
        then_body: Union[_ASTNode, List[_ASTNode], _Program]
    ) -> _IfThenNode:
        return _IfThenNode(self._expression, then_body)

    def Flip(self) -> _IfFlipNode:
        return _IfFlipNode(self._expression)

    def _get_control_negative_qubit_ids(self) -> List[int]:
        raise NotImplementedError()

    @staticmethod
    def _get_label() -> str:
        raise NotImplementedError()

    def _accept(self, visitor: '_ASTVisitor') -> None:
        raise NotImplementedError()


class _U0Node(_ASTNode):
    def __init__(self, target_qubit: _QubitNode) -> None:
        super().__init__()
        self._target_qubit = target_qubit

    def _get_target_qubit(self) -> _QubitNode:
        return self._target_qubit

    def _get_target_qubit_ids(self) -> List[int]:
        return self._get_target_qubit()._get_target_qubit_ids()


class _XNode(_U0Node):
    @staticmethod
    def _get_label() -> str:
        return 'X'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_x(self)


class _YNode(_U0Node):
    @staticmethod
    def _get_label() -> str:
        return 'Y'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_y(self)


class _ZNode(_U0Node):
    @staticmethod
    def _get_label() -> str:
        return 'Z'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_z(self)


class _HNode(_U0Node):
    @staticmethod
    def _get_label() -> str:
        return 'H'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_h(self)


class _U1Node(_ASTNode):
    def __init__(self, target_qubit: _QubitNode, arg1: float) -> None:
        super().__init__()
        self._target_qubit = target_qubit
        self._arg1 = arg1

    def _get_target_qubit(self) -> _QubitNode:
        return self._target_qubit

    def _get_arg1(self) -> float:
        return self._arg1

    def _get_target_qubit_ids(self) -> List[int]:
        return self._get_target_qubit()._get_target_qubit_ids()


class _U3Node(_ASTNode):
    @staticmethod
    def _get_label() -> str:
        return 'U3'

    def __init__(self, target_qubit: _QubitNode, arg1: float, arg2: float, arg3: float) -> None:
        super().__init__()
        self._target_qubit = target_qubit
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def _get_target_qubit(self) -> _QubitNode:
        return self._target_qubit

    def _get_target_qubit_ids(self) -> List[int]:
        return self._get_target_qubit()._get_target_qubit_ids()

    def _get_arg1(self) -> float:
        return self._arg1

    def _get_arg2(self) -> float:
        return self._arg2

    def _get_arg3(self) -> float:
        return self._arg3

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_u3(self)


class _AllNode(_ASTNode):
    def __init__(self, controls: Union[_QubitNode, List[_QubitNode]]) -> None:
        super().__init__()
        self._controls = to_list(controls)

    def _get_control_qubits(self) -> List[_QubitNode]:
        return self._controls

    def _get_control_positive_qubit_ids(self) -> List[int]:
        control_positive_qubit_ids : List[int] = []

        for control_qubit in self._controls:
            control_positive_qubit_ids.extend(control_qubit._get_target_qubit_ids())

        return control_positive_qubit_ids

    @staticmethod
    def _get_label() -> str:
        return 'ALL'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_all(self)


class _MatchNode(_ASTNode):
    def __init__(self, controls: Union[_QubitNode, List[_QubitNode]], mask: List[int]) -> None:
        super().__init__()
        self._controls = to_list(controls)
        self._mask = mask
        self._control_positive_qubit_ids : List[int] = []
        self._control_negative_qubit_ids : List[int] = []

    def _get_control_qubits(self) -> List[_QubitNode]:
        return self._controls

    def _get_control_qubit_ids(self) -> List[int]:
        return sum([control_qubit._get_target_qubit_ids() for control_qubit in self._controls], [])

    def _get_mask(self) -> List[int]:
        return self._mask

    def _set_control_positive_qubit_ids(self, control_positive_qubit_ids: List[int]) -> None:
        self._control_positive_qubit_ids = control_positive_qubit_ids

    def _get_control_positive_qubit_ids(self) -> List[int]:
        return self._control_positive_qubit_ids

    def _set_control_negative_qubit_ids(self, control_negative_qubit_ids: List[int]) -> None:
        self._control_negative_qubit_ids = control_negative_qubit_ids

    def _get_control_negative_qubit_ids(self) -> List[int]:
        return self._control_negative_qubit_ids

    @staticmethod
    def _get_label() -> str:
        return 'MATCH'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_match(self)


class _ZeroNode(_ASTNode):
    def __init__(self, controls: Union[_QubitNode, List[_QubitNode]]) -> None:
        super().__init__()
        self._controls = to_list(controls)

    def _get_control_qubits(self) -> List[_QubitNode]:
        return self._controls

    def _get_control_positive_qubit_ids(self) -> List[int]:
        control_positive_qubit_ids : List[int] = []

        for control_qubit in self._controls:
            control_positive_qubit_ids.extend(control_qubit._get_target_qubit_ids())

        return control_positive_qubit_ids

    @staticmethod
    def _get_label() -> str:
        return 'ZERO'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_zero(self)


class _NotNode(_ASTNode):
    def __init__(self, target_qubit: _ASTNode) -> None:
        super().__init__()
        self._target_qubit = target_qubit

    def _get_target_qubit(self) -> _ASTNode:
        return self._target_qubit

    def _set_target_qubit_ids(self, _target_qubit_ids: List[int]):
        self._target_qubit._set_target_qubit_ids(_target_qubit_ids)

    def _get_target_qubit_ids(self) -> List[int]:
        return self._target_qubit._get_target_qubit_ids()

    @staticmethod
    def _get_label() -> str:
        return 'NOT'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_not(self)


class _MeasurementNode(_ASTNode):
    def __init__(self, qubit: _QubitNode, bit: _CBitNode) -> None:
        super().__init__()
        self._qubit = qubit
        self._bit = bit

    def _get_qubit(self) -> _QubitNode:
        return self._qubit

    def _get_bit(self) -> _CBitNode:
        return self._bit

    @staticmethod
    def _get_label() -> str:
        return 'MEASURE'

    def _accept(self, visitor: '_ASTVisitor') -> None:
        visitor.on_measure(self)

#
##
#

class _ASTVisitor:

    def on_program(self, program: _Program) -> None:
        for node in program._nodes:
            node._accept(self)

    def on_qubit(self, var: _QubitNode) -> None:
        pass

    def on_cvar(self, var: _CBitNode) -> None:
        pass

    def on_inv(self, inv: _InvNode) -> None:
        inv._get_body()._accept(self)

    def on_if_then_else(self, if_then_else: _IfThenElseNode) -> None:
        if_then_else._get_condition()._accept(self)
        if_then_else._get_then_body()._accept(self)
        if_then_else._get_else_body()._accept(self)


    def on_if_then(self, if_then) -> None:
        if_then._get_condition()._accept(self)
        if_then._get_then_body()._accept(self)

    def on_if_flip(self, if_flip: _IfFlipNode) -> None:
        if_flip._get_condition()._accept(self)

    def on_x(self, x: _XNode) -> None:
        pass

    def on_y(self, y: _YNode) -> None:
        pass

    def on_z(self, z: _ZNode) -> None:
        pass

    def on_h(self, h: _HNode) -> None:
        pass

    def on_u3(self, u3: _U3Node) -> None:
        pass

    def on_all(self, all_: _AllNode) -> None:
        pass

    def on_match(self, match: _MatchNode) -> None:
        pass

    def on_zero(self, zero: _ZeroNode) -> None:
        pass

    def on_not(self, not_: _NotNode) -> None:
        not_._get_target_qubit()._accept(self)

    def on_measure(self, measure: _MeasurementNode) -> None:
        pass


class _VarQubitsMgrVisitor(_ASTVisitor):
    def __init__(self) -> None:
        self.min_unused_qubit_id = 0
        self.var_qubit_ids_mapping : Dict[str, List[int]] = dict()

        self.min_unused_bit_id = 0
        self.var_bit_ids_mapping : Dict[str, List[int]] = dict()

    def on_qubit(self, var: _QubitNode) -> None:
        if var._get_name() in self.var_qubit_ids_mapping:
            return

        qubit_ids = list(range(
            self.min_unused_qubit_id,
            self.min_unused_qubit_id + var._get_size()
        ))

        self.min_unused_qubit_id += var._get_size()

        self.var_qubit_ids_mapping[var._get_name()] = qubit_ids
        var._set_target_qubit_ids(qubit_ids)

    def on_cvar(self, var: _CBitNode) -> None:
        if var._get_name() in self.var_qubit_ids_mapping:
            return

        bit_ids = list(range(
            self.min_unused_bit_id,
            self.min_unused_bit_id + var._get_size()
        ))

        self.min_unused_bit_id += var._get_size()

        self.var_bit_ids_mapping[var._get_name()] = bit_ids
        var._set_target_bit_ids(bit_ids)

    def on_match(self, match: _MatchNode) -> None:
        if (len(match._get_control_qubit_ids()) != len(match._get_mask())):
            raise Exception(
                f'Inside {type(match)._get_label()} statement: Var ' +
                f' should have the same size as a mask length'
            )

        control_positive_qubit_ids : List[int] = []
        control_negative_qubit_ids : List[int] = []

        for (target_qubit_id, bit) in zip(match._get_control_qubit_ids(), match._get_mask()):
            if (bit == 0):
                control_negative_qubit_ids.append(target_qubit_id)
            elif (bit == 1):
                control_positive_qubit_ids.append(target_qubit_id)
            else:
                raise Exception(
                f'Inside {type(match)._get_label()} statement: Mask `{match._get_mask()}`' +
                f' should contain only "0" or "1" but it contains {bit}'
            )

        match._set_control_positive_qubit_ids(control_positive_qubit_ids)
        match._set_control_negative_qubit_ids(control_negative_qubit_ids)

    def get_min_unused_qubit_id(self) -> int:
        return self.min_unused_qubit_id

    def get_min_unused_bit_id(self) -> int:
        return self.min_unused_bit_id

    def get_var_qubit_range(self, var_id: str) -> List[int]:
        return self.var_qubit_ids_mapping[var_id]


class _AncillaQubitsMgrVisitor(_ASTVisitor):
    def __init__(self, min_unused_qubit_id: int, min_unused_bit_id: int) -> None:
        self.min_unused_qubit_id = min_unused_qubit_id
        self.max_min_unused_qubit_id = min_unused_qubit_id

        self.min_unused_bit_id = min_unused_bit_id
        self.max_min_unused_bit_id = min_unused_bit_id

        self._parents_control_positive_qubit_ids_stack : List[List[int]] = []
        self._parents_control_negative_qubit_ids_stack : List[List[int]] = []

    def get_min_unused_qubit_id(self) -> int:
        return self.max_min_unused_qubit_id

    def get_min_unused_bit_id(self) -> int:
        return self.max_min_unused_bit_id

    def _on_if(self, if_then) -> None:
        if_then._get_condition()[0]._set_target_qubit_ids(if_then._get_ancilla_qubit_ids())
        if_then._get_condition()[0]._accept(self)

    def _on_then(self, if_then) -> None:
        if_then._set_control_positive_qubit_ids(if_then._get_ancilla_qubit_ids())

        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        if_then._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        if_then._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

        self._parents_control_positive_qubit_ids_stack.append(if_then._get_ancilla_qubit_ids())
        if_then._get_then_body()._accept(self)
        self._parents_control_positive_qubit_ids_stack.pop()

    def _on_flip(self, if_flip: _IfFlipNode) -> None:
        if_flip._set_control_positive_qubit_ids(if_flip._get_ancilla_qubit_ids())

        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        if_flip._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        if_flip._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

    def _on_else(self, if_then_else) -> None:
        if_then_else._set_control_negative_qubit_ids(if_then_else._get_ancilla_qubit_ids())

        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        if_then_else._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        if_then_else._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

        self._parents_control_negative_qubit_ids_stack.append(if_then_else._get_ancilla_qubit_ids())
        if_then_else._get_else_body()._accept(self)
        self._parents_control_negative_qubit_ids_stack.pop()

    def on_if_then_else(self, if_then_else: _IfThenElseNode) -> None:
        if_then_else._set_ancilla_qubit_ids([self.min_unused_qubit_id])
        self.min_unused_qubit_id += 1
        self.max_min_unused_qubit_id = max(self.max_min_unused_qubit_id, self.min_unused_qubit_id)

        self._on_if(if_then_else)
        self._on_then(if_then_else)
        self._on_else(if_then_else)

        self.min_unused_qubit_id -= 1

    def on_if_then(self, if_then) -> None:
        if_then._set_ancilla_qubit_ids([self.min_unused_qubit_id])
        self.min_unused_qubit_id += 1
        self.max_min_unused_qubit_id = max(self.max_min_unused_qubit_id, self.min_unused_qubit_id)

        self._on_if(if_then)
        self._on_then(if_then)

        self.min_unused_qubit_id -= 1

    def on_if_flip(self, if_flip: _IfFlipNode) -> None:
        if_flip._set_ancilla_qubit_ids([self.min_unused_qubit_id])
        self.min_unused_qubit_id += 1
        self.max_min_unused_qubit_id = max(self.max_min_unused_qubit_id, self.min_unused_qubit_id)

        self._on_if(if_flip)
        self._on_flip(if_flip)

        # no need for min_unused_qubit_id decrement

    def _on_u0(self, u0) -> None:
        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        u0._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        u0._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

        ancilla_qubit_ids = list(range(
            self.min_unused_qubit_id,
            self.min_unused_qubit_id +
                len(parents_control_positive_qubit_ids) +
                len(parents_control_negative_qubit_ids) +
                -1
        ))

        u0._set_ancilla_qubit_ids(ancilla_qubit_ids)
        self.max_min_unused_qubit_id = max(self.max_min_unused_qubit_id, max(ancilla_qubit_ids + [0]) + 1)

    def on_x(self, x: _XNode) -> None:
        self._on_u0(x)

    def on_y(self, y: _YNode) -> None:
        self._on_u0(y)

    def on_z(self, z: _ZNode) -> None:
        self._on_u0(z)

    def on_h(self, h: _HNode) -> None:
        self._on_u0(h)

    def on_u3(self, u3: _U3Node) -> None:
        self._on_u0(u3)

    def on_match(self, match: _MatchNode) -> None:
        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        match._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        match._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

        ancilla_qubit_ids = list(range(
            self.min_unused_qubit_id,
            self.min_unused_qubit_id +
                len(match._get_control_positive_qubit_ids()) +
                len(match._get_control_negative_qubit_ids()) +
                len(parents_control_positive_qubit_ids) +
                len(parents_control_negative_qubit_ids) +
                -1
        ))

        match._set_ancilla_qubit_ids(ancilla_qubit_ids)
        self.max_min_unused_qubit_id = max(self.max_min_unused_qubit_id, max(ancilla_qubit_ids + [0]) + 1)

    def on_all(self, all_: _AllNode) -> None:
        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        all_._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        all_._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

        ancilla_qubit_ids = list(range(
            self.min_unused_qubit_id,
            self.min_unused_qubit_id +
                len(all_._get_control_positive_qubit_ids()) +
                len(parents_control_positive_qubit_ids) +
                len(parents_control_negative_qubit_ids) +
                -1
        ))

        all_._set_ancilla_qubit_ids(ancilla_qubit_ids)
        self.max_min_unused_qubit_id = max(self.max_min_unused_qubit_id, max(ancilla_qubit_ids + [0]) + 1)

    def on_zero(self, zero: _ZeroNode) -> None:
        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        zero._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        zero._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

        ancilla_qubit_ids = list(range(
            self.min_unused_qubit_id,
            self.min_unused_qubit_id +
                len(zero._get_control_positive_qubit_ids()) +
                len(parents_control_positive_qubit_ids) +
                len(parents_control_negative_qubit_ids) +
                -1
        ))

        zero._set_ancilla_qubit_ids(ancilla_qubit_ids)
        self.max_min_unused_qubit_id = max(self.max_min_unused_qubit_id, max(ancilla_qubit_ids + [0]) + 1)

    def on_not(self, not_: _NotNode) -> None:
        not_._get_target_qubit()._accept(self)

        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        not_._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        not_._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

    def _set_parents_control_qubit_ids(self, node) -> None:
        parents_control_positive_qubit_ids = list(chain(*self._parents_control_positive_qubit_ids_stack))
        parents_control_negative_qubit_ids = list(chain(*self._parents_control_negative_qubit_ids_stack))

        node._set_parents_control_positive_qubit_ids(parents_control_positive_qubit_ids)
        node._set_parents_control_negative_qubit_ids(parents_control_negative_qubit_ids)

#
##
#

class _ICommand:
    def __init__(self, depth: int) -> None:
        self._depth = depth

    def set_depth(self, depth: int) -> None:
        self._depth = depth

    @abstractmethod
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        pass

    @abstractmethod
    def get_inverse(self) -> '_ICommand':
        pass

    def _get_indent(self) -> str:
        return 4 * self._depth * ' '


class _CommentCmd(_ICommand):
    def __init__(self, text: str, depth: int) -> None:
        super().__init__(depth)
        self.text = text

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.comment(self.text)]

    def get_inverse(self) -> '_CommentCmd':
        return _CommentCmd('~' + self.text, self._depth)


class _U0Cmd(_ICommand):
    def __init__(self, target_qubit_id: int, depth: int) -> None:
        super().__init__(depth)
        self._qubit_id = target_qubit_id


class _CU0Cmd(_ICommand):
    def __init__(
        self,
        control_qubit_id: int,
        target_qubit_id: int,
        depth: int
    ) -> None:
        super().__init__(depth)
        self._control_qubit_id = control_qubit_id
        self._target_qubit_id = target_qubit_id


class _CCU0Cmd(_ICommand):
    def __init__(
        self,
        control_qubit_id_1: int,
        control_qubit_id_2: int,
        target_qubit_id: int,
        depth: int
    ) -> None:
        super().__init__(depth)
        self._control_qubit_id_1 = control_qubit_id_1
        self._control_qubit_id_2 = control_qubit_id_2
        self._target_qubit_id = target_qubit_id


class _XCmd(_U0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.x(self._qubit_id)]

    def get_inverse(self) -> '_XCmd':
        return self


class _CXCmd(_CU0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.cx(self._control_qubit_id, self._target_qubit_id)]

    def get_inverse(self) -> '_CXCmd':
        return self


class _CCXCmd(_CCU0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [
            self._get_indent() +
            qasm_formatter.ccx(self._control_qubit_id_1, self._control_qubit_id_2, self._target_qubit_id)
        ]

    def get_inverse(self) -> '_CCXCmd':
        return self


class _YCmd(_U0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.y(self._qubit_id)]

    def get_inverse(self) -> '_YCmd':
        return self


class _CYCmd(_CU0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.cy(self._control_qubit_id, self._target_qubit_id)]

    def get_inverse(self) -> '_CYCmd':
        return self


class _ZCmd(_U0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.z(self._qubit_id)]

    def get_inverse(self) -> '_ZCmd':
        return self


class _CZCmd(_CU0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [
            self._get_indent() +
            qasm_formatter.cz(self._control_qubit_id, self._target_qubit_id)
        ]

    def get_inverse(self) -> '_CZCmd':
        return self


class _HCmd(_U0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.h(self._qubit_id)]

    def get_inverse(self) -> '_HCmd':
        return self


class _CHCmd(_CU0Cmd):
    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [self._get_indent() + qasm_formatter.ch(self._control_qubit_id, self._target_qubit_id)]

    def get_inverse(self) -> '_CHCmd':
        return self


class _U1Cmd(_ICommand):
    def __init__(self, target_qubit_id: int, arg1: float, depth: int) -> None:
        super().__init__(depth)
        self._target_qubit_id = target_qubit_id
        self._arg1 = arg1


class _CU1Cmd(_ICommand):
    def __init__(
        self,
        control_qubit_id: int,
        target_qubit_id: int,
        arg1: float,
        depth: int
    ) -> None:
        super().__init__(depth)
        self._control_qubit_id = control_qubit_id
        self._target_qubit_id = target_qubit_id
        self._arg1 = arg1


class _U3Cmd(_ICommand):
    def __init__(self, target_qubit_id: int, arg1: float, arg2: float, arg3: float, depth: int) -> None:
        super().__init__(depth)
        self._target_qubit_id = target_qubit_id
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [
            self._get_indent() +
            qasm_formatter.u3(self._target_qubit_id, self._arg1, self._arg2, self._arg3)
        ]

    def get_inverse(self) -> '_U3Cmd':
        # https://github.com/Qiskit/qiskit-terra/blob/master/qiskit/extensions/standard/u3.py
        return _U3Cmd(
            self._target_qubit_id,
            -self._arg1,    # theta   ->  -theta
            -self._arg3,    # phi     ->  -lambda
            -self._arg2,    # lambda  ->  -phi
            self._depth
        )


class _CU3Cmd(_ICommand):
    def __init__(self, control_qubit_id: int, target_qubit_id: int, arg1: float, arg2: float, arg3: float, depth: int) -> None:
        super().__init__(depth)
        self._control_qubit_id = control_qubit_id
        self._target_qubit_id = target_qubit_id
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [
            self._get_indent() +
            qasm_formatter.cu3(self._control_qubit_id, self._target_qubit_id, self._arg1, self._arg2, self._arg3)
        ]

    def get_inverse(self) -> '_CU3Cmd':
        # https://github.com/Qiskit/qiskit-terra/blob/master/qiskit/extensions/standard/u3.py
        return _CU3Cmd(
            self._control_qubit_id,
            self._target_qubit_id,
            -self._arg1,    # theta   ->  -theta
            -self._arg3,    # phi     ->  -lambda
            -self._arg2,    # lambda  ->  -phi
            self._depth
        )


class _MeasurementCmd(_ICommand):
    def __init__(
        self,
        qubit_id: int,
        bit_id: int,
        depth: int
    ) -> None:
        super().__init__(depth)
        self._qubit_id = qubit_id
        self._bit_id = bit_id

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return [
            self._get_indent() +
            qasm_formatter.measure(self._qubit_id, self._bit_id)
        ]

    def get_inverse(self) -> '_MeasurementCmd':
        raise NotImplementedError('Inverse Measurement, really???')


class _InversedCmd(_ICommand):
    def __init__(self, command: _ICommand, depth: int) -> None:
        super().__init__(depth)
        self.command = command

    def set_depth(self, depth: int) -> None:
        super().set_depth(depth)
        self.command.set_depth(depth)

    def get_lines(self, qasm_formatter: IQAsmFormatter) -> List[str]:
        return self.command.get_inverse().get_lines(qasm_formatter)

    def get_inverse(self) -> _ICommand:
        return self.command

#
##
#

class _CommentMgr:
    def get_qubits_str(self, positive_qubits: List[int], negative_qubits: List[int]) -> str:
        text = ', '.join(map(str, sorted(positive_qubits)))

        if negative_qubits:
            if positive_qubits:
                text += ', '

            text += '!'

        text += ', !'.join(map(str, sorted(negative_qubits)))

        return text

    def get_on_qubit_comment(self, var: _QubitNode) -> str:
        return (
            f'QUBIT `{var._get_name()}`' +
            f' [size: {var._get_size()}]' +
            f' [qubits: {var._get_target_qubit_ids()}]' +
            (('') if (var._get_init() == 0) else (' [init=1]'))
        )

    def get_on_cvar_comment(self, var: _CBitNode) -> str:
        return (
            f'CBIT `{var._get_name()}`' +
            f' [size: {var._get_size()}]' +
            f' [bits: {var._get_target_bit_ids()}]'
        )

    def get_on_inv_comment(self, var: _InvNode) -> str:
        return 'INV'

    def get_on_if_comment(self, if_then) -> str:
        comment = 'IF'

        if if_then._get_ancilla_qubit_ids():
            comment += f' ANC (qubits: [{" ".join(map(str, if_then._get_ancilla_qubit_ids()))}])'

        return comment

    def get_on_then_comment(self, if_then) -> str:
        qubits_str = self.get_qubits_str(
            if_then._get_control_positive_qubit_ids() +
            if_then._get_parents_control_positive_qubit_ids(),
            if_then._get_parents_control_negative_qubit_ids()
        )

        return 'THEN (qubits: [' + qubits_str + '])'

    def get_on_else_comment(self, if_then_else: _IfThenElseNode) -> str:
        qubits_str = self.get_qubits_str(
            if_then_else._get_parents_control_positive_qubit_ids(),
            if_then_else._get_control_negative_qubit_ids() +
            if_then_else._get_parents_control_negative_qubit_ids()
        )

        return 'ELSE (qubits: [' + qubits_str + '])'

    def get_on_flip_comment(self, if_flip: _IfFlipNode) -> str:
        return if_flip._get_label()

    def _get_on_u0_comment(self, u0_node: _U0Node) -> str:
        comment = (
            (u0_node._get_label() + ' ') +
            f'(qubit: {u0_node._get_target_qubit_ids()[0]}) ' +
            f'-> (qubit: {u0_node._get_target_qubit_ids()[0]})'
        )

        if (u0_node._get_parents_control_positive_qubit_ids() or
            u0_node._get_parents_control_negative_qubit_ids()
        ):
            qubits_str = self.get_qubits_str(
                u0_node._get_parents_control_positive_qubit_ids(),
                u0_node._get_parents_control_negative_qubit_ids()
            )

            comment += ' CONTROLLED (qubits: [' + qubits_str + '])'

        if u0_node._get_ancilla_qubit_ids():
            comment += f' ANC (qubits: [{", ".join(map(str, u0_node._get_ancilla_qubit_ids()))}])'

        return comment

    def _get_on_u1_comment(self, u1_node: _U1Node, arg1: float) -> str:
        comment = (
            f'{u1_node._get_label()} ' +
            f'{arg1} ' +
            f'(qubit: {u1_node._get_target_qubit_ids()[0]}) ' +
            f'-> (qubit: {u1_node._get_target_qubit_ids()[0]})'
        )

        if (u1_node._get_parents_control_positive_qubit_ids() or
            u1_node._get_parents_control_negative_qubit_ids()
        ):
            qubits_str = self.get_qubits_str(
                u1_node._get_parents_control_positive_qubit_ids(),
                u1_node._get_parents_control_negative_qubit_ids()
            )

            comment += ' CONTROLLED (qubits: [' + qubits_str + '])'

        if u1_node._get_ancilla_qubit_ids():
            comment += f' ANC (qubits: [{", ".join(map(str, u1_node._get_ancilla_qubit_ids()))}])'

        return comment

    def _get_on_u3_comment(self, u3_node: _U3Node, arg1: float, arg2: float, arg3: float) -> str:
        comment = (
            f'{u3_node._get_label()} ' +
            f'{arg1} {arg2} {arg3} ' +
            f'(qubit: {u3_node._get_target_qubit_ids()[0]}) ' +
            f'-> (qubit: {u3_node._get_target_qubit_ids()[0]})'
        )

        if (u3_node._get_parents_control_positive_qubit_ids() or
            u3_node._get_parents_control_negative_qubit_ids()
        ):
            qubits_str = self.get_qubits_str(
                u3_node._get_parents_control_positive_qubit_ids(),
                u3_node._get_parents_control_negative_qubit_ids()
            )

            comment += ' CONTROLLED (qubits: [' + qubits_str + '])'

        if u3_node._get_ancilla_qubit_ids():
            comment += f' ANC (qubits: [{", ".join(map(str, u3_node._get_ancilla_qubit_ids()))}])'

        return comment

    def get_on_x_comment(self, x: _XNode) -> str:
        return self._get_on_u0_comment(x)

    def get_on_y_comment(self, y: _YNode) -> str:
        return self._get_on_u0_comment(y)

    def get_on_z_comment(self, z: _ZNode) -> str:
        return self._get_on_u0_comment(z)

    def get_on_h_comment(self, h: _HNode) -> str:
        return self._get_on_u0_comment(h)

    def get_on_u3_comment(self, u3: _U3Node) -> str:
        return self._get_on_u3_comment(u3, u3._get_arg1(), u3._get_arg2(), u3._get_arg3())

    def get_on_all_comment(self, all_: _AllNode) -> str:
        qubits = []

        for var in all_._get_control_qubits():
            qubits.extend(var._get_target_qubit_ids())

        target_qubit_ids = all_._get_target_qubit_ids()

        comment = f'{all_._get_label()} (qubits: {qubits}) -> (qubit: {target_qubit_ids[0]})'

        if all_._get_ancilla_qubit_ids():
            comment += f' ANC (qubits: [{", ".join(map(str, all_._get_ancilla_qubit_ids()))}])'

        return comment

    def get_on_match_comment(self, match: _MatchNode) -> str:
        qubits: List[int] = sum(
            [control_qubit._get_target_qubit_ids() for control_qubit in match._get_control_qubits()],
            []
        )

        mask = match._get_mask()
        target_qubit_ids = match._get_target_qubit_ids()

        comment = f'{match._get_label()} (qubits: {qubits}) (mask: {mask}) -> (qubit: {target_qubit_ids[0]})'

        if match._get_ancilla_qubit_ids():
            comment += f' ANC (qubits: [{", ".join(map(str, match._get_ancilla_qubit_ids()))}])'

        return comment

    def get_on_zero_comment(self, zero: _ZeroNode) -> str:
        qubits = []

        for var in zero._get_control_qubits():
            qubits.extend(var._get_target_qubit_ids())

        return f'{zero._get_label()} (qubits: {qubits}) -> (qubit: {zero._get_target_qubit_ids()[0]})'

    def get_on_not_comment(self, not_: _NotNode) -> str:
        return (
            f'{not_._get_label()} (qubit: {not_._get_target_qubit()._get_target_qubit_ids()[0]}) ' +
            f'-> (qubit: {not_._get_target_qubit()._get_target_qubit_ids()[0]})'
        )

    def get_on_measure_comment(self, measure: _MeasurementNode) -> str:
        return (
            f'{measure._get_label()} (qubit: {measure._get_qubit()._get_target_qubit_ids()[0]}) ' +
            f'-> (bit: {measure._get_bit()._get_target_bit_ids()[0]})'
        )

class _CompileVisitor(_ASTVisitor):
    def __init__(self) -> None:
        self.__commands_stack : List[List[_ICommand]] = [[]]
        self.counter = Counter()
        self.cm = _CommentMgr()

    def _get_commands_stack(self) -> List[List[_ICommand]]:
        return self.__commands_stack

    def _commands_stack_top_extend(self, command) -> None:
        if not(isinstance(command, list)):
            return self._commands_stack_top_extend([command])
        else:
            self._commands_stack_top().extend(command)

    def _commands_stack_pop(self) -> List[_ICommand]:
        result = self._commands_stack_top()
        self.__commands_stack.pop()
        return result

    def _commands_stack_push(self, commands) -> None:
        self.__commands_stack.append(commands)

    def _commands_stack_top(self) -> List[_ICommand]:
        return self.__commands_stack[-1]

    def on_qubit(self, var: _QubitNode) -> None:
        self._commands_stack_top_extend(_CommentCmd(self.cm.get_on_qubit_comment(var), self.counter.counter))

        if var._get_init() == 0:
            pass
        elif var._get_init() == 1:
            self._commands_stack_top_extend(_XCmd(var._get_target_qubit_ids()[0], self.counter.counter))
        else:
            assert(False)

        return super().on_qubit(var)

    def on_cvar(self, var: _CBitNode) -> None:
        self._commands_stack_top_extend(_CommentCmd(self.cm.get_on_cvar_comment(var), self.counter.counter))
        return super().on_cvar(var)

    def _get_on_inv_commands(self, inv: _InvNode) -> List[_ICommand]:
        self._commands_stack_push([])
        inv._get_body()._accept(self)
        inv_commands : List[_ICommand] = self._commands_stack_pop()
        return self._inversed(inv_commands)

    def on_inv(self, inv: _InvNode) -> None:
        self._commands_stack_top_extend(self._get_on_inv_commands(inv))

    def _get_on_if_then_commands(self, if_then: _IfThenNode) -> List[_ICommand]:
        if_comment_commands  : List[_ICommand] = [
            _CommentCmd(self.cm.get_on_if_comment(if_then), self.counter.counter)
        ]

        self._commands_stack_push([])
        with DepthGuard(self.counter):
            if_then._get_condition()._accept(self)
        if_commands = self._commands_stack_pop()

        then_comment_commands : List[_ICommand] = [
            _CommentCmd(self.cm.get_on_then_comment(if_then), self.counter.counter)
        ]

        self._commands_stack_push([])
        with DepthGuard(self.counter):
            if_then._get_then_body()._accept(self)
        then_commands = self._commands_stack_pop()

        return (
            if_comment_commands +
            if_commands +
            then_comment_commands +
            then_commands +
            self._inversed(if_comment_commands) +
            self._inversed(if_commands)
        )

    def on_if_then(self, if_then: _IfThenNode) -> None:
        self._commands_stack_top_extend(self._get_on_if_then_commands(if_then))

    def _get_on_if_then_else_commands(self, if_then_else: _IfThenElseNode) -> List[_ICommand]:
        if_comment_commands : List[_ICommand] = [
            _CommentCmd(self.cm.get_on_if_comment(if_then_else), self.counter.counter)
        ]

        self._commands_stack_push([])
        with DepthGuard(self.counter):
            if_then_else._get_condition()._accept(self)
        if_commands : List[_ICommand] = self._commands_stack_pop()

        then_comment_commands : List[_ICommand] = [
            _CommentCmd(self.cm.get_on_then_comment(if_then_else), self.counter.counter)
        ]

        self._commands_stack_push([])
        with DepthGuard(self.counter):
            if_then_else._get_then_body()._accept(self)
        then_commands : List[_ICommand] = self._commands_stack_pop()

        else_comment_commands : List[_ICommand] = [
            _CommentCmd(self.cm.get_on_else_comment(if_then_else), self.counter.counter)
        ]

        self._commands_stack_push([])
        with DepthGuard(self.counter):
            if_then_else._get_else_body()._accept(self)
        else_commands : List[_ICommand] = self._commands_stack_pop()

        return (
            if_comment_commands +
            if_commands +
            then_comment_commands +
            then_commands +
            else_comment_commands +
            else_commands +
            self._inversed(if_comment_commands) +
            self._inversed(if_commands)
        )

    def on_if_then_else(self, if_then_else: _IfThenElseNode) -> None:
        self._commands_stack_top_extend(self._get_on_if_then_else_commands(if_then_else))

    def _get_on_if_flip_commands(self, if_flip: _IfFlipNode) -> List[_ICommand]:
        if_comment_commands : List[_ICommand] = [
            _CommentCmd(self.cm.get_on_if_comment(if_flip), self.counter.counter)
        ]

        self._commands_stack_push([])
        with DepthGuard(self.counter):
            if_flip._get_condition()._accept(self)
        if_commands : List[_ICommand] = self._commands_stack_pop()

        flip_comment_commands : List[_ICommand] = [
            _CommentCmd(self.cm.get_on_flip_comment(if_flip), self.counter.counter)
        ]

        with DepthGuard(self.counter):
            flip_commands : List[_ICommand] = [
                _ZCmd(if_flip._get_condition()[0]._get_target_qubit_ids()[0], self.counter.counter)
            ]

        return (
            if_comment_commands +
            if_commands +
            flip_comment_commands +
            flip_commands +
            self._inversed(if_comment_commands) +
            self._inversed(if_commands)
        )

    def on_if_flip(self, if_flip: _IfFlipNode) -> None:
        self._commands_stack_top_extend(self._get_on_if_flip_commands(if_flip))

    def _get_on_u0_commands(
        self,
        u0_node: _U0Node,
        u0_cmd_class: Type[_U0Cmd],
        cu0_cmd_class: Type[_CU0Cmd],
        get_on_u0_comment_callback: Callable[[_U0Node], str]
    ) -> List[_ICommand]:
        comment_commands : List[_ICommand] = [_CommentCmd(get_on_u0_comment_callback(u0_node), self.counter.counter)]

        parents_control_positive_qubit_ids = u0_node._get_parents_control_positive_qubit_ids()
        parents_control_negative_qubit_ids = u0_node._get_parents_control_negative_qubit_ids()

        if (len(parents_control_positive_qubit_ids) == 0) and (len(parents_control_negative_qubit_ids) == 0):
            return comment_commands + [u0_cmd_class(u0_node._get_target_qubit_ids()[0], self.counter.counter)]
        else:
            negate_negative_commands : List[_ICommand] = [
                _XCmd(control_negative_qubit, self.counter.counter)
                    for control_negative_qubit in parents_control_negative_qubit_ids
            ]

            controlled_commands : List[_ICommand] = self._get_on_cccu0_commands(
                sorted(parents_control_positive_qubit_ids + parents_control_negative_qubit_ids),
                u0_node._get_target_qubit_ids()[0],
                cu0_cmd_class
            )

            return (
                comment_commands +
                negate_negative_commands +
                controlled_commands +
                self._inversed(negate_negative_commands)
            )

    def _on_u0(
        self,
        u0_node: _U0Node,
        u0_cmd_class: Type[_U0Cmd],
        cu0_cmd_class: Type[_CU0Cmd],
        get_on_u0_comment_callback
    ) -> None:
        self._commands_stack_top_extend(
            self._get_on_u0_commands(
                u0_node,
                u0_cmd_class,
                cu0_cmd_class,
                get_on_u0_comment_callback
            )
        )

    def _get_on_u1_commands(
        self,
        u1_node: _U1Node,
        u1_cmd_class: Type[_U1Cmd],
        cu1_cmd_class: Type[_CU1Cmd],
        get_on_u1_comment_callback: Callable[[_U1Node], str]
    ) -> List[_ICommand]:
        comment_commands : List[_ICommand] = [_CommentCmd(get_on_u1_comment_callback(u1_node), self.counter.counter)]

        parents_control_positive_qubit_ids = u1_node._get_parents_control_positive_qubit_ids()
        parents_control_negative_qubit_ids = u1_node._get_parents_control_negative_qubit_ids()

        if (len(parents_control_positive_qubit_ids) == 0) and (len(parents_control_negative_qubit_ids) == 0):
            return (
                comment_commands +
                [u1_cmd_class(u1_node._get_target_qubit_ids()[0], u1_node._get_arg1(), self.counter.counter)]
            )
        else:
            negate_negative_commands : List[_ICommand] = [
                _XCmd(control_negative_qubit, self.counter.counter)
                    for control_negative_qubit in parents_control_negative_qubit_ids
            ]

            controlled_commands : List[_ICommand] = self._get_on_cccu1_commands(
                sorted(parents_control_positive_qubit_ids + parents_control_negative_qubit_ids),
                u1_node._get_target_qubit_ids()[0],
                u1_node._get_arg1(),
                cu1_cmd_class
            )

            return (
                comment_commands +
                negate_negative_commands +
                controlled_commands +
                self._inversed(negate_negative_commands)
            )

    def _get_on_u3_commands(
        self,
        u3_node: _U3Node,
        u3_cmd_class: Type[_U3Cmd],
        cu3_cmd_class: Type[_CU3Cmd],
        get_on_u3_comment_callback: Callable[[_U3Node], str]
    ) -> List[_ICommand]:
        comment_commands : List[_ICommand] = [_CommentCmd(get_on_u3_comment_callback(u3_node), self.counter.counter)]

        parents_control_positive_qubit_ids = u3_node._get_parents_control_positive_qubit_ids()
        parents_control_negative_qubit_ids = u3_node._get_parents_control_negative_qubit_ids()

        if (len(parents_control_positive_qubit_ids) == 0) and (len(parents_control_negative_qubit_ids) == 0):
            return (
                comment_commands + [
                    u3_cmd_class(
                        u3_node._get_target_qubit_ids()[0],
                        u3_node._get_arg1(),
                        u3_node._get_arg2(),
                        u3_node._get_arg3(),
                        self.counter.counter
                    )
                ]
            )
        else:
            negate_negative_commands : List[_ICommand] = [
                _XCmd(control_negative_qubit, self.counter.counter)
                    for control_negative_qubit in parents_control_negative_qubit_ids
            ]

            controlled_commands : List[_ICommand] = self._get_on_cccu3_commands(
                sorted(parents_control_positive_qubit_ids + parents_control_negative_qubit_ids),
                u3_node._get_target_qubit_ids()[0],
                u3_node._get_arg1(),
                u3_node._get_arg2(),
                u3_node._get_arg3(),
                cu3_cmd_class
            )

            return (
                comment_commands +
                negate_negative_commands +
                controlled_commands +
                self._inversed(negate_negative_commands)
            )

    def _on_u1(
        self,
        u1_node: _U1Node,
        u1_cmd_class: Type[_U1Cmd],
        cu1_cmd_class: Type[_CU1Cmd],
        get_on_u1_comment_callback
    ) -> None:
        self._commands_stack_top_extend(
            self._get_on_u1_commands(
                u1_node,
                u1_cmd_class,
                cu1_cmd_class,
                get_on_u1_comment_callback
            )
        )

    def _on_u3(
        self,
        u3_node: _U3Node,
        u3_cmd_class: Type[_U3Cmd],
        cu3_cmd_class: Type[_CU3Cmd],
        get_on_u3_comment_callback
    ) -> None:
        self._commands_stack_top_extend(
            self._get_on_u3_commands(
                u3_node,
                u3_cmd_class,
                cu3_cmd_class,
                get_on_u3_comment_callback
            )
        )

    def on_x(self, x: _XNode) -> None:
        self._on_u0(x, _XCmd, _CXCmd, self.cm.get_on_x_comment)

    def on_y(self, y: _YNode) -> None:
        self._on_u0(y, _YCmd, _CYCmd, self.cm.get_on_y_comment)

    def on_z(self, z: _ZNode) -> None:
        self._on_u0(z, _ZCmd, _CZCmd, self.cm.get_on_z_comment)

    def on_h(self, h: _HNode) -> None:
        self._on_u0(h, _HCmd, _CHCmd, self.cm.get_on_h_comment)

    def on_u3(self, u3: _U3Node) -> None:
        self._on_u3(u3, _U3Cmd, _CU3Cmd, self.cm.get_on_u3_comment)

    def _inversed(self, commands) -> List[_ICommand]:
        if not(isinstance(commands, list)):
            return self._inversed([commands])

        return [_InversedCmd(command, command._depth) for command in commands[:: -1]]

    def _get_on_cccu0_commands(
        self,
        control_qubit_ids: List[int],
        target_qubit_id: int,
        cu0_cmd_class: Type[_CU0Cmd]
    ) -> List[_ICommand]:
        first_unused_qubit_id = max(control_qubit_ids + [target_qubit_id]) + 1

        ancillas : List[int] = list(range(first_unused_qubit_id, first_unused_qubit_id + len(control_qubit_ids) + 1))

        controlled_commands : List[_ICommand] = []

        while len(control_qubit_ids) > 1:
            control_1 = control_qubit_ids.pop(0)
            control_2 = control_qubit_ids.pop(0)
            ancilla = ancillas.pop(0)
            control_qubit_ids.append(ancilla)

            controlled_commands.append(
                _CCXCmd(control_1, control_2, ancilla, self.counter.counter)
            )

        cu0_commands : List[_ICommand] = [
            cu0_cmd_class(
                control_qubit_ids[-1],
                target_qubit_id,
                self.counter.counter
            )
        ]

        control_qubit_ids.pop(0)

        return (
            controlled_commands +
            cu0_commands +
            self._inversed(controlled_commands)
        )

    def _get_on_cccu1_commands(
        self,
        control_qubit_ids: List[int],
        target_qubit_id: int,
        arg1: float,
        cu1_cmd_class: Type[_CU1Cmd]
    ) -> List[_ICommand]:
        first_unused_qubit_id = max(control_qubit_ids + [target_qubit_id]) + 1

        ancillas : List[int] = list(range(first_unused_qubit_id, first_unused_qubit_id + len(control_qubit_ids) + 1))

        controlled_commands : List[_ICommand] = []

        while len(control_qubit_ids) > 1:
            control_1 = control_qubit_ids.pop(0)
            control_2 = control_qubit_ids.pop(0)
            ancilla = ancillas.pop(0)
            control_qubit_ids.append(ancilla)

            controlled_commands.append(
                _CCXCmd(control_1, control_2, ancilla, self.counter.counter)
            )

        cu1_commands : List[_ICommand] = [
            cu1_cmd_class(
                control_qubit_ids[-1],
                target_qubit_id,
                arg1,
                self.counter.counter
            )
        ]

        control_qubit_ids.pop(0)

        return (
            controlled_commands +
            cu1_commands +
            self._inversed(controlled_commands)
        )


    def _get_on_cccu3_commands(
        self,
        control_qubit_ids: List[int],
        target_qubit_id: int,
        arg1: float,
        arg2: float,
        arg3: float,
        cu3_cmd_class: Type[_CU3Cmd]
    ) -> List[_ICommand]:
        first_unused_qubit_id = max(control_qubit_ids + [target_qubit_id]) + 1

        ancillas : List[int] = list(range(first_unused_qubit_id, first_unused_qubit_id + len(control_qubit_ids) + 1))

        controlled_commands : List[_ICommand] = []

        while len(control_qubit_ids) > 1:
            control_1 = control_qubit_ids.pop(0)
            control_2 = control_qubit_ids.pop(0)
            ancilla = ancillas.pop(0)
            control_qubit_ids.append(ancilla)

            controlled_commands.append(
                _CCXCmd(control_1, control_2, ancilla, self.counter.counter)
            )

        cu3_commands : List[_ICommand] = [
            cu3_cmd_class(
                control_qubit_ids[-1],
                target_qubit_id,
                arg1,
                arg2,
                arg3,
                self.counter.counter
            )
        ]

        control_qubit_ids.pop(0)

        return (
            controlled_commands +
            cu3_commands +
            self._inversed(controlled_commands)
        )

    def _get_on_cccx_commands(self, control_qubit_ids: List[int], target_qubit_id: int) -> List[_ICommand]:
        return self._get_on_cccu0_commands(control_qubit_ids, target_qubit_id, _CXCmd)

    def _get_on_all_commands(self, all_: _AllNode) -> List[_ICommand]:
        qubit_ids : List[int] = []
        commands : List[_ICommand] = [_CommentCmd(self.cm.get_on_all_comment(all_), self.counter.counter)]

        for var in all_._get_control_qubits():
            qubit_ids.extend(var._get_target_qubit_ids())

        control_qubit_ids : List[int] = sum((var._get_target_qubit_ids() for var in all_._get_control_qubits()), [])
        target_qubit_ids : List[int] = all_._get_target_qubit_ids()
        commands.extend(self._get_on_cccx_commands(control_qubit_ids, target_qubit_ids[0]))

        return commands

    def on_all(self, all_: _AllNode) -> None:
        self._commands_stack_top_extend(self._get_on_all_commands(all_))

    def _get_on_match_commands(self, match: _MatchNode) -> List[_ICommand]:
        with DepthGuard(self.counter):
            negate_negative_commands : List[_ICommand] = []
            comment_commands : List[_ICommand] = [_CommentCmd(self.cm.get_on_match_comment(match), self.counter.counter)]

            for control_negative_qubit_id in match._get_control_negative_qubit_ids():
                negate_negative_commands.append(_XCmd(control_negative_qubit_id, self.counter.counter))

            on_all_commands : List[_ICommand] = self._get_on_all_commands(cast(_AllNode, match))

            return (
                comment_commands +
                negate_negative_commands +
                on_all_commands +
                self._inversed(negate_negative_commands)
            )

    def on_match(self, match: _MatchNode) -> None:
        self._commands_stack_top_extend(self._get_on_match_commands(match))

    def _get_on_zero_commands(self, zero: _ZeroNode) -> List[_ICommand]:
        with DepthGuard(self.counter):
            qubit_ids : List[int] = []
            negate_negative_commands : List[_ICommand] = []
            comment_commands : List[_ICommand] = [_CommentCmd(self.cm.get_on_zero_comment(zero), self.counter.counter)]

            for control_qubit in zero._get_control_qubits():
                qubit_ids.extend(control_qubit._get_target_qubit_ids())

            control_qubit_ids : List[int] = sum(
                [control_qubit._get_target_qubit_ids() for control_qubit in zero._get_control_qubits()],
                []
            )

            for control_qubit_id in control_qubit_ids:
                negate_negative_commands.append(_XCmd(control_qubit_id, self.counter.counter))

            on_all_commands : List[_ICommand] = self._get_on_all_commands(cast(_AllNode, zero))

            return (
                comment_commands +
                negate_negative_commands +
                on_all_commands +
                self._inversed(negate_negative_commands)
            )

    def on_zero(self, zero: _ZeroNode) -> None:
        self._commands_stack_top_extend(self._get_on_zero_commands(zero))

    def _get_on_not_commands(self, not_: _NotNode) -> List[_ICommand]:
        with DepthGuard(self.counter):
            comment_commands : List[_ICommand] = [_CommentCmd(self.cm.get_on_not_comment(not_), self.counter.counter)]

            self._commands_stack_push([])
            with DepthGuard(self.counter):
                not_._get_target_qubit()._accept(self)
            target_commands : List[_ICommand] = self._commands_stack_pop()

            not_commands : List[_ICommand] = [
                _XCmd(
                    not_._get_target_qubit()._get_target_qubit_ids()[0],
                    self.counter.counter
                )
            ]

            return (
                comment_commands +
                target_commands +
                not_commands
            )

    def on_not(self, not_: _NotNode) -> None:
        self._commands_stack_top_extend(self._get_on_not_commands(not_))

    def _get_on_measure_commands(self, measure: _MeasurementNode) -> List[_ICommand]:
        with DepthGuard(self.counter):
            comment_commands : List[_ICommand] = [
                _CommentCmd(self.cm.get_on_measure_comment(measure), self.counter.counter)
            ]

            measure_commands : List[_ICommand] = [
                _MeasurementCmd(
                    measure._get_qubit()._get_target_qubit_ids()[0],
                    measure._get_bit()._get_target_bit_ids()[0],
                    self.counter.counter
                )
            ]

            return (
                comment_commands +
                measure_commands
            )

    def on_measure(self, measure: _MeasurementNode) -> None:
        self._commands_stack_top_extend(self._get_on_measure_commands(measure))

#
##
#

class Quasar:

    def _commands_to_code(
        self,
        commands_stack: List[List[_ICommand]],
        qasm_formatter: IQAsmFormatter,
        keep_comments=True
    ) -> List[str]:
        code : List[str] = []

        for commands in commands_stack:
            for command in commands:
                if (not keep_comments):
                    command.set_depth(0)

                for line in command.get_lines(qasm_formatter):
                    if (not keep_comments) and (line.find('#') != -1):
                        continue

                    code.append(line)

        return code

    def compile(
        self,
        root: Union[_ASTNode, List[_ASTNode], _Program],
        keep_comments = False,
        qasm_formatter = QiskitFormatter()
    ) -> List[str]:
        _QubitNode._qubit_counter = 0
        _CBitNode._cbit_counter = 0

        root = _Program(root)

        var_qubits_mgr_visitor = _VarQubitsMgrVisitor()
        root._accept(var_qubits_mgr_visitor)

        min_unused_qubit_id = var_qubits_mgr_visitor.get_min_unused_qubit_id()
        min_unused_bit_id = var_qubits_mgr_visitor.get_min_unused_bit_id()

        ancilla_qubits_mgr_visitor = _AncillaQubitsMgrVisitor(min_unused_qubit_id, min_unused_bit_id)
        root._accept(ancilla_qubits_mgr_visitor)

        min_unused_qubit_id = ancilla_qubits_mgr_visitor.get_min_unused_qubit_id()
        min_unused_bit_id = ancilla_qubits_mgr_visitor.get_min_unused_bit_id()

        qasm_visitor = _CompileVisitor()
        root._accept(qasm_visitor)

        headers = qasm_formatter.get_headers(
            min_unused_qubit_id,
            [min_unused_qubit_id],
            min_unused_bit_id
        )

        code = self._commands_to_code(
            qasm_visitor._get_commands_stack(),
            qasm_formatter,
            keep_comments
        )

        footers = qasm_formatter.get_footers()

        return headers + code + footers

    def to_qasm_str(
        self,
        root: Union[_ASTNode, List[_ASTNode], _Program],
        keep_comments = False,
        qasm_formatter = QiskitFormatter()
    ) -> str:
        return '\n'.join(self.compile(root, keep_comments, qasm_formatter=QASMFormatter()))

#
##
#

ASTNode = _ASTNode

All = _AllNode

def Any(controls: Union[_QubitNode, List[_QubitNode]]) -> _ASTNode:
    return _NotNode(_ZeroNode(controls))

def U1(target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return _U3Node(target_qubit, 0, 0, arg1)

def CU1(control_qubit: _QubitNode, target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return _IfNode(_AllNode(control_qubit)).Then(U1(target_qubit, arg1))

def U2(target_qubit: _QubitNode, arg1: float, arg2: float) -> _ASTNode:
    return _U3Node(target_qubit, pi/2, arg1, arg2)

def CU2(control_qubit: _QubitNode, target_qubit: _QubitNode, arg1: float, arg2: float) -> _ASTNode:
    return _IfNode(_AllNode(control_qubit)).Then(U2(target_qubit, arg1, arg2))

def U3(target_qubit: _QubitNode, arg1: float, arg2: float, arg3: float) -> _ASTNode:
    return _U3Node(target_qubit, arg1, arg2, arg3)

def CU3(control_qubit: _QubitNode, target_qubit: _QubitNode, arg1: float, arg2: float, arg3: float) -> _ASTNode:
    return _IfNode(_AllNode(control_qubit)).Then(U3(target_qubit, arg1, arg2, arg3))

def CX(control_qubit: _QubitNode, target_qubit: _QubitNode) -> _ASTNode:
    return _IfNode(_AllNode(control_qubit)).Then(_XNode(target_qubit))

CNot = CX

def CCX(control_qubit_1: _QubitNode, control_qubit_2: _QubitNode, target_qubit: _QubitNode) -> _ASTNode:
    return _IfNode(_AllNode([control_qubit_1, control_qubit_2])).Then(_XNode(target_qubit))

# Unconditional Flip <=> If(True).Flip() <=> For_Each_State().Flip()
# With these two statements
#     If(    ( condition ) ).Then( code )
#     If( not( condition ) ).Then( code )
# code is always executed.
def Flip(qubits: List[_QubitNode]) -> List[_ASTNode]:
    return [
        _IfNode(          ( _AllNode(qubits[0]) )  ).Flip(),
        _IfNode(  _NotNode( _AllNode(qubits[0]) )  ).Flip()
    ]

If = _IfNode
Inv = _InvNode
Match = _MatchNode
Measurement = _MeasurementNode
Not = _NotNode

def Phase(target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return U1(target_qubit, arg1)

def Id(target_qubit: _QubitNode) -> _ASTNode:
    return U1(target_qubit, 0)

Program = _Program
Qubit = _QubitNode

def RX(target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return _U3Node(target_qubit, arg1, -pi/2, pi/2)

def CRX(control_qubit: _QubitNode, target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return _IfNode(_AllNode(control_qubit)).Then(RX(target_qubit, arg1))

def RY(target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return _U3Node(target_qubit, arg1, 0, 0)

def CRY(control_qubit: _QubitNode, target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return _IfNode(_AllNode(control_qubit)).Then(RY(target_qubit, arg1))

def RZ(target_qubit: _QubitNode, arg1: float) -> _Program:
    return _Program([
        Phase(target_qubit, arg1/2),
        X(target_qubit),
        Phase(target_qubit, -arg1/2),
        X(target_qubit)
    ])

def CRZ(control_qubit: _QubitNode, target_qubit: _QubitNode, arg1: float) -> _ASTNode:
    return _IfNode(_AllNode(control_qubit)).Then(RZ(target_qubit, arg1))

def S(target_qubit: _QubitNode) -> _ASTNode:
    return Phase(target_qubit, pi/2)

def T(target_qubit: _QubitNode) -> _ASTNode:
    return Phase(target_qubit, pi/4)

def Seq(*nodes) -> _Program:
    return _Program(list(nodes))

X = _XNode
Y = _YNode
Z = _ZNode
H = _HNode
Zero = _ZeroNode
