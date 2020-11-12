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
from typing import Iterable, List, Optional, TypeVar, Union

from builtin_gates import BuiltinGate, X_GATE

#
##
#

T = TypeVar('T')

def to_list(obj: Union[T, List[T]]) -> List[T]:
    if isinstance(obj, list):
        return obj
    else:
        return [obj]

#
##
#

class IASTVisitable(ABC):
    @abstractmethod
    def accept(self, visitor: 'IASTVisitor') -> Optional['IASTNode']:
        pass

#
##
#

class IASTNode(IASTVisitable):
    def __init__(self) -> None:
        self._target_qubit_id : int = -1

        self._control_positive_qubit_ids : List[int] = []
        self._control_negative_qubit_ids : List[int] = []

    def __add__(self, other: Union['IASTNode', List['IASTNode'], 'Program']) -> 'Program':
        if (isinstance(other, IASTNode)):
            return Program([self] + [other])

        elif (isinstance(other, list)):
            return Program([self] + other)

        elif (isinstance(other, Program)):
            return Program([self] + other._nodes)

        raise TypeError(f'Cannot construct Program from type {type(other)}')

    def set_target_qubit_id(self, target_qubit_id: int) -> None:
        self._target_qubit_id = target_qubit_id

    def get_target_qubit_id(self) -> int:
        return self._target_qubit_id


ProgramLike = Union[IASTNode, List[IASTNode], 'Program']

class Program(IASTVisitable):
    _qubit_counter = 0
    _cbit_counter = 0

    def __init__(self, other: Optional[ProgramLike] = None) -> None:
        self._nodes : List[IASTNode] = []

        if isinstance(other, Program):
            self._nodes = other._nodes or []

        elif isinstance(other, IASTNode):
            self._nodes = [other]

        elif isinstance(other, list):
            self._nodes = other or []

        elif other is not None:
            raise Exception(f'Unknown type {type(other)}')

    def __add__(self, other: ProgramLike) -> 'Program':
        return Program(self._nodes + Program(other)._nodes)

    def __iadd__(self, other: ProgramLike) -> 'Program':
        self._nodes.extend(Program(other)._nodes)
        return self

    def __getitem__(self, index: int) -> IASTNode:
        return self._nodes[index]

    def __len__(self) -> int:
        return len(self._nodes)

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_program(self)

    def Qubit(self, init=0) -> 'QubitNode':
        qubit = QubitNode()
        qubit.set_name(f'$$_qubit_{Program._qubit_counter}')
        Program._qubit_counter += 1

        self._nodes.append(QubitDeclarationNode(qubit))

        if init == 1:
            self._nodes.append(GateNode(X_GATE, qubit))

        return qubit

    def Qubits(self, inits: Iterable[int]) -> List['QubitNode']:
        return [self.Qubit(init) for init in inits]

    def CBit(self) -> 'CBitNode':
        cbit = CBitNode()
        cbit.set_name(f'$$_cbit_{Program._cbit_counter}')
        Program._cbit_counter += 1
        self._nodes.append(cbit)
        return cbit

    def CBits(self, size: int) -> List['CBitNode']:
        return [self.CBit() for i in range(size)]


class QubitNode(IASTNode):
    def __init__(self, id_=-1) -> None:
        super().__init__()
        super().set_target_qubit_id(id_)

    def set_name(self, name: str) -> None:
        self._name = name

    def get_name(self) -> str:
        return self._name

    def get_id(self) -> int:
        return super().get_target_qubit_id()

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_qubit(self)


class QubitDeclarationNode(IASTNode):
    def __init__(self, qubit: QubitNode) -> None:
        self._qubit = qubit

    def get_qubit(self) -> QubitNode:
        return self._qubit

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_qubit_declaraion(self)


class CBitNode(IASTNode):

    def __init__(self, target_bit_id=-1) -> None:
        super().__init__()
        self._target_bit_id = target_bit_id

    def set_name(self, name: str) -> None:
        self._name = name

    def get_name(self) -> str:
        return self._name

    def set_id(self, target_bit_id: int) -> None:
        self._target_bit_id = target_bit_id

    def get_id(self) -> int:
        return self._target_bit_id

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_cvar(self)


class InvNode(IASTNode):
    def __init__(self, node: ProgramLike) -> None:
        super().__init__()
        self._body : Program = Program(node)

    def get_body(self) -> Program:
        return self._body

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_inv(self)


class ConditionNode(IASTNode):
    pass


class IfASTNode(IASTNode):
    def __init__(self, condition: ConditionNode, then_body: ProgramLike) -> None:
        super().__init__()
        self._condition = condition
        self._then_body = Program(then_body)

    def get_condition(self) -> ConditionNode:
        return self._condition

    def get_then_body(self) -> Program:
        return self._then_body


class IfThenElseNode(IfASTNode):
    def __init__(self, condition: ConditionNode, then_body: ProgramLike, else_body: ProgramLike) -> None:
        super().__init__(condition, then_body)
        self._else_body = Program(else_body)

    def get_else_body(self) -> Program:
        return self._else_body

    def set_control_positive_qubit_ids(self, control_positive_qubit_ids: List[int]) -> None:
        self._control_positive_qubit_ids = control_positive_qubit_ids

    def get_control_positive_qubit_ids(self) -> List[int]:
        return self._control_positive_qubit_ids

    def _set_control_negative_qubit_ids(self, control_negative_qubit_ids: List[int]) -> None:
        self._control_negative_qubit_ids = control_negative_qubit_ids

    def get_control_negative_qubit_ids(self) -> List[int]:
        return self._control_negative_qubit_ids

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_if_then_else(self)


class IfThenNode(IfASTNode):
    def __init__(self, condition: ConditionNode, then_body: ProgramLike) -> None:
        super().__init__(condition, then_body)

    def Else(self, else_body: ProgramLike) -> IfThenElseNode:
        return IfThenElseNode(self._condition, self._then_body, else_body)

    def set_control_positive_qubit_ids(self, control_positive_qubit_ids: List[int]) -> None:
        self._control_positive_qubit_ids = control_positive_qubit_ids

    def get_control_positive_qubit_ids(self) -> List[int]:
        return self._control_positive_qubit_ids

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_if_then(self)


class IfFlipNode(IASTNode):
    def __init__(self, condition: ConditionNode) -> None:
        super().__init__()
        self._condition = condition

    def get_condition(self) -> ConditionNode:
        return self._condition

    def set_control_positive_qubit_ids(self, control_positive_qubit_ids: List[int]) -> None:
        self._control_positive_qubit_ids = control_positive_qubit_ids

    def get_control_positive_qubit_ids(self) -> List[int]:
        return self._control_positive_qubit_ids

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_if_flip(self)


class IfNode(IASTNode):
    def __init__(self, condition: ConditionNode) -> None:
        super().__init__()
        self._condition = condition

    def Then(self, then_body: ProgramLike) -> IfThenNode:
        return IfThenNode(self._condition, then_body)

    def Flip(self) -> IfFlipNode:
        return IfFlipNode(self._condition)

    def get_control_negative_qubit_ids(self) -> List[int]:
        raise NotImplementedError()

    def accept(self, visitor: 'IASTVisitor') -> None:
        raise NotImplementedError()


class GateNode(IASTNode):
    """ This node represents an application of a builtin gate on a specified qubit. """

    def __init__(self, gate: BuiltinGate, qubit: QubitNode, params: List[float] = None) -> None:
        super().__init__()
        self._gate = gate
        self._params = params or []
        self._target_qubit = qubit
        assert len(self.params) == gate.num_params

    @property
    def gate(self) -> BuiltinGate:
        return self._gate

    @property
    def params(self) -> List[float]:
        return self._params

    def get_target_qubit(self) -> QubitNode:
        return self._target_qubit

    def get_target_qubit_id(self) -> int:
        return self._target_qubit.get_target_qubit_id()

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_gate(self)


class MatchNode(ConditionNode):
    def __init__(self, control_qubits: Union[QubitNode, List[QubitNode]], mask: List[int]) -> None:
        super().__init__()
        self._control_qubits = to_list(control_qubits)
        self._mask = mask
        self._control_positive_qubit_ids : List[int] = []
        self._control_negative_qubit_ids : List[int] = []

        if (len(self.get_control_qubits()) != len(self.get_mask())):
            raise Exception(
                'Inside MATCH statement: Var ' +
                ' should have the same size as a mask length'
            )

    def get_mask(self) -> List[int]:
        return self._mask

    def get_control_qubits(self) -> List[QubitNode]:
        return self._control_qubits

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_match(self)


class NotNode(ConditionNode):
    def __init__(self, condition: ConditionNode) -> None:
        super().__init__()
        self._condition = condition

    def get_condition(self) -> ConditionNode:
        return self._condition

    def set_target_qubit_id(self, target_qubit_id: int):
        self._condition.set_target_qubit_id(target_qubit_id)

    def get_target_qubit_id(self) -> int:
        return self._condition.get_target_qubit_id()

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_not(self)


class MeasurementNode(IASTNode):
    def __init__(self, qubit: QubitNode, bit: CBitNode) -> None:
        super().__init__()
        self._qubit = qubit
        self._bit = bit

    def get_qubit(self) -> QubitNode:
        return self._qubit

    def get_bit(self) -> CBitNode:
        return self._bit

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_measure(self)


class ResetNode(IASTNode):
    def __init__(self, qubit: QubitNode) -> None:
        super().__init__()
        self._qubit = qubit

    def get_qubit(self) -> QubitNode:
        return self._qubit

    def accept(self, visitor: 'IASTVisitor') -> None:
        visitor.on_reset(self)

#
##
#


class IASTVisitor:

    def on_program(self, program: Program) -> None:
        for node in program._nodes:
            node.accept(self)

    def on_qubit_declaraion(self, declaration: QubitDeclarationNode) -> None:
        pass

    def on_qubit(self, qubit: QubitNode) -> None:
        pass

    def on_cvar(self, bit: CBitNode) -> None:
        pass

    def on_inv(self, inv: InvNode) -> None:
        inv.get_body().accept(self)

    def on_if_then_else(self, if_then_else: IfThenElseNode) -> None:
        if_then_else.get_condition().accept(self)
        if_then_else.get_then_body().accept(self)
        if_then_else.get_else_body().accept(self)

    def on_if_then(self, if_then) -> None:
        if_then.get_condition().accept(self)
        if_then.get_then_body().accept(self)

    def on_if_flip(self, if_flip: IfFlipNode) -> None:
        if_flip.get_condition().accept(self)

    def on_gate(self, node: GateNode) -> None:
        pass

    def on_match(self, match: MatchNode) -> None:
        pass

    def on_not(self, not_: NotNode) -> None:
        not_.get_condition().accept(self)

    def on_measure(self, measure: MeasurementNode) -> None:
        pass

    def on_reset(self, reset: ResetNode) -> None:
        pass
