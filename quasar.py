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

from math import pi
from typing import List, Union

from builtin_gates import U3_GATE, X_GATE, Y_GATE, Z_GATE, H_GATE
from quasar_ast import Program, ProgramLike, GateNode, IASTNode, IfNode, MatchNode, NotNode, MeasurementNode, ResetNode, QubitNode, InvNode
from quasar_cmd import ICommand
from quasar_comp import CompileVisitor, ResourceAllocator, to_list
from quasar_formatter import IQAsmFormatter
from quasar_opt import QuasarOpt
from quasar_qasm import QASMFormatter

#
##
#

class Quasar:
    def _commands_to_code(
        self,
        commands: List[ICommand],
        qasm_formatter: IQAsmFormatter
    ) -> List[str]:
        code : List[str] = []

        for command in commands:
            for line in command.get_lines(qasm_formatter):
                code.append(line)

        return code

    def to_qasm_str(
        self,
        root: ProgramLike,
        optimize: bool = True
    ) -> str:
        return '\n'.join(Quasar().compile(root, QASMFormatter(), optimize))

    def compile(
        self,
        root: ProgramLike,
        qasm_formatter,
        optimize: bool = True
    ) -> List[str]:
        root = Program(root)
        rsrc = ResourceAllocator()
        compile_visitor = CompileVisitor(rsrc)
        root.accept(compile_visitor)

        max_used_qubit_id = compile_visitor.get_max_used_qubit_id()
        max_used_bit_id = compile_visitor.get_max_used_bit_id()

        commands: List[ICommand] = compile_visitor.commands

        if optimize:
            commands = QuasarOpt.run(commands, max_used_qubit_id)

        qasm_formatter.set_qubits_counter(max_used_qubit_id)
        qasm_formatter.set_bits_counter(max_used_bit_id)
        qasm_formatter.set_groups([max_used_qubit_id])

        headers = qasm_formatter.get_headers()

        code = self._commands_to_code(
            commands,
            qasm_formatter,
        )

        footers = qasm_formatter.get_footers()

        return headers + code + footers

#
##
#

ASTNode = IASTNode

Not = NotNode

def All(qubits: Union[QubitNode, List[QubitNode]]) -> MatchNode:
    qubits = to_list(qubits)
    return MatchNode(qubits, [1]*len(qubits))

def Zero(qubits: Union[QubitNode, List[QubitNode]]) -> MatchNode:
    qubits = to_list(qubits)
    return MatchNode(qubits, [0]*len(qubits))

def Any(controls: Union[QubitNode, List[QubitNode]]) -> NotNode:
    return Not(Zero(controls))

def U1(target_qubit: QubitNode, arg1: float) -> IASTNode:
    return GateNode(U3_GATE, target_qubit, params=[0, 0, arg1])

def CU1(control_qubit: QubitNode, target_qubit: QubitNode, arg1: float) -> IASTNode:
    return IfNode(All(control_qubit)).Then(U1(target_qubit, arg1))

def U2(target_qubit: QubitNode, arg1: float, arg2: float) -> IASTNode:
    return GateNode(U3_GATE, target_qubit, params=[pi/2, arg1, arg2])

def CU2(control_qubit: QubitNode, target_qubit: QubitNode, arg1: float, arg2: float) -> IASTNode:
    return IfNode(All(control_qubit)).Then(U2(target_qubit, arg1, arg2))

def U3(target_qubit: QubitNode, arg1: float, arg2: float, arg3: float) -> IASTNode:
    return GateNode(U3_GATE, target_qubit, params=[arg1, arg2, arg3])

def CU3(control_qubit: QubitNode, target_qubit: QubitNode, arg1: float, arg2: float, arg3: float) -> IASTNode:
    return IfNode(All(control_qubit)).Then(U3(target_qubit, arg1, arg2, arg3))

def CX(control_qubit: QubitNode, target_qubit: QubitNode) -> IASTNode:
    return IfNode(All(control_qubit)).Then(GateNode(X_GATE, target_qubit))

CNot = CX

def CCX(control_qubit_1: QubitNode, control_qubit_2: QubitNode, target_qubit: QubitNode) -> IASTNode:
    return IfNode(All([control_qubit_1, control_qubit_2])).Then(GateNode(X_GATE, target_qubit))

# Unconditional Flip <=> If(True).Flip() <=> For_Each_State().Flip()
# With these two statements
#     If(    ( condition ) ).Then( code )
#     If( not( condition ) ).Then( code )
# code is always executed.
def Flip(qubits: List[QubitNode]) -> List[IASTNode]:
    return [
        IfNode(          ( All(qubits[0]) )  ).Flip(),
        IfNode(  NotNode( All(qubits[0]) )  ).Flip()
    ]

If = IfNode

Inv = InvNode

Match = MatchNode

Measurement = MeasurementNode

Reset = ResetNode

def Phase(target_qubit: QubitNode, arg1: float) -> IASTNode:
    return U1(target_qubit, arg1)

def Id(target_qubit: QubitNode) -> IASTNode:
    return U1(target_qubit, 0)

Qubit = QubitNode

def RX(target_qubit: QubitNode, arg1: float) -> IASTNode:
    return U3(target_qubit, arg1, -pi/2, pi/2)

def CRX(control_qubit: QubitNode, target_qubit: QubitNode, arg1: float) -> IASTNode:
    return IfNode(All(control_qubit)).Then(RX(target_qubit, arg1))

def RY(target_qubit: QubitNode, arg1: float) -> IASTNode:
    return U3(target_qubit, arg1, 0, 0)

def CRY(control_qubit: QubitNode, target_qubit: QubitNode, arg1: float) -> IASTNode:
    return IfNode(All(control_qubit)).Then(RY(target_qubit, arg1))

def RZ(target_qubit: QubitNode, arg1: float) -> Program:
    return Program([
        Phase(target_qubit, arg1/2),
        X(target_qubit),
        Phase(target_qubit, -arg1/2),
        X(target_qubit)
    ])

def CRZ(control_qubit: QubitNode, target_qubit: QubitNode, arg1: float) -> IASTNode:
    return IfNode(All(control_qubit)).Then(RZ(target_qubit, arg1))

def CZ(control_qubit: QubitNode, target_qubit: QubitNode) -> IASTNode:
    # CZ(c, t) != CRZ(c, t, pi/2)
    return IfNode(All(control_qubit)).Then(Z(target_qubit))

def CCZ(control_qubit_1: QubitNode, control_qubit_2: QubitNode, target_qubit: QubitNode) -> Program:
    return Program([
        H(target_qubit),
        CCX(control_qubit_1, control_qubit_2, target_qubit),
        H(target_qubit)
    ])

def S(target_qubit: QubitNode) -> IASTNode:
    return Phase(target_qubit, pi/2)

def Sdg(target_qubit: QubitNode) -> IASTNode:
    return Phase(target_qubit, -pi/2)

def T(target_qubit: QubitNode) -> IASTNode:
    return Phase(target_qubit, pi/4)

def Tdg(target_qubit: QubitNode) -> IASTNode:
    return Phase(target_qubit, -pi/4)

def Seq(*nodes) -> Program:
    return Program(list(nodes))

def Swap(q1: QubitNode, q2: QubitNode) -> Program:
    return Seq(
        CX(q1, q2),
        CX(q2, q1),
        CX(q1, q2)
    )

def X(target_qubit: QubitNode) -> GateNode:
    return GateNode(X_GATE, target_qubit)

def Y(target_qubit: QubitNode) -> GateNode:
    return GateNode(Y_GATE, target_qubit)

def Z(target_qubit: QubitNode) -> GateNode:
    return GateNode(Z_GATE, target_qubit)

def H(target_qubit: QubitNode) -> GateNode:
    return GateNode(H_GATE, target_qubit)
