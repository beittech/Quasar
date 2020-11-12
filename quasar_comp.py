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


from copy import copy
from typing import Callable, Dict, List, Tuple, Union

from builtin_arithmetics import invert_gate
from builtin_gates import X_GATE, Z_GATE
from quasar_ast import \
    QubitNode, QubitDeclarationNode, CBitNode, InvNode, IASTVisitor, Program, \
    IfThenNode, IfThenElseNode, IfFlipNode, \
    MatchNode, NotNode, \
    MeasurementNode, ResetNode, IASTVisitable, GateNode, to_list
from quasar_cmd import \
    ICommand, MeasurementCmd, ResetCmd, GateCmd

# Mapping from control qubit id onto (0, 1)
# where 1 means positive control and 0 -- negative.
_ControlQubits = Dict[int, Union[int, int]]


class ResourceAllocator:
    def __init__(self) -> None:
        self.min_unused_qubit_id = 0 # the first currently available to use qubit id
        self.qubits_counter = 0 # the first qubit id that is never used up to the current moment
        self.bits_counter = 0 # the first bit id that is never used up to the current moment

    def get_qubits_counter(self) -> int:
        return self.qubits_counter

    def get_min_unused_qubit_id(self) -> int:
        return self.min_unused_qubit_id

    def get_bits_counter(self) -> int:
        return self.bits_counter

    def allocate_qubit(self) -> int:
        self.min_unused_qubit_id += 1
        self.qubits_counter = max(self.qubits_counter, self.min_unused_qubit_id)
        return self.min_unused_qubit_id - 1

    def free_qubit(self) -> None:
        self.min_unused_qubit_id -= 1

    def free_qubits(self, qubits) -> None:
        for _ in range(qubits):
            self.free_qubit()

    def allocate_bit(self) -> int:
        self.bits_counter += 1
        return self.bits_counter - 1


class CompileVisitor(IASTVisitor):
    def __init__(self, rsrc) -> None:
        self._rsrc = rsrc
        self._commands: List[ICommand] = []
        self._control_mapping: _ControlQubits = {} # The dict of currently controlling qubits

    @staticmethod
    def _invert_control_qubits(control_qubits: _ControlQubits) -> _ControlQubits:
        """ Most likely you need to assert if its length is equal to 1 before applying. """
        return {q: 0 if m == 1 else 1 for q, m in control_qubits.items()}

    @staticmethod
    def _get_reduced_commands(
        max_num_qubits,
        control_mapping,
        rsrc
    ) -> List[ICommand]:
        """ Ensures that the number of control qubits is at most one.
        This is usually required when the condition is going to be negated. """
        if len(control_mapping) <= max_num_qubits:
            return []

        control_qubit_ids, cccu_commands = CompileVisitor._get_cccu_commands(
            control_mapping,
            rsrc,
            max_num_qubits
        )

        control_mapping.clear()
        control_mapping.update(control_qubit_ids)
        return cccu_commands

    @staticmethod
    def _get_qubit_negation_commands(control_mapping) -> List[ICommand]:
        """ This function makes sure that all control qubits
        are in fact positively controlling. """
        result : List[ICommand] = []

        for qubit_id, mask in control_mapping.items():
            if mask == 0:
                result.append(GateCmd(X_GATE, qubit_id))
                control_mapping[qubit_id] = 1

        return result

    @staticmethod
    def _get_cccu_commands(
        control_mapping: _ControlQubits,
        rsrc: ResourceAllocator,
        max_num_qubits: int
    ) -> Tuple[_ControlQubits, List[ICommand]]:
        """
        Builds a circuit that computes the AND condition on the `control_mapping`
        qubits (some possibly negated) into one qubit.
        To acheive this, when the number of control bits is greater than `max_num_qubits`,
        an `ancilla_allocator` may be used to allocate extra qubits.
        The resulting computation consists of X gates (for negation) and CCX gates to
        construct a computation tree. This tree has a logarithmic depth.
        Returns a tuple consisting of a new control qubits dict and the computation commands.
        """

        commands: List[ICommand] = []

        for (qubit_id, is_positive) in control_mapping.items():
            if is_positive == 0:
                commands.append(GateCmd(X_GATE, qubit_id))

        control_qubit_ids = list(control_mapping)

        while len(control_qubit_ids) > max_num_qubits:
            q1 = control_qubit_ids.pop(0)
            q2 = control_qubit_ids.pop(0)
            q3 = rsrc.allocate_qubit()
            commands.append(GateCmd(X_GATE, q3, control_qubit_ids={q1, q2}))
            control_qubit_ids.append(q3)

        return {q: 1 for q in control_qubit_ids}, commands

    @property
    def commands(self) -> List[ICommand]:
        return self._commands

    def get_max_used_qubit_id(self) -> int:
        return self._rsrc.get_qubits_counter()

    def get_max_used_bit_id(self) -> int:
        return self._rsrc.get_bits_counter()

    def _get_commands_recursive(
        self,
        visitable: IASTVisitable,
        with_controls: _ControlQubits = None
    ) -> List[ICommand]:
        """ Gets the list of commands that is recursively generated by visiting `visitable`.
        Additional `with_controls` dict can be used to use additional controls
        in addition to the currently set."""

        with_controls = with_controls or {}
        subvisitor = CompileVisitor(self._rsrc)
        subvisitor._control_mapping = copy(self._control_mapping)
        assert not (set(with_controls) & set(subvisitor._control_mapping))
        subvisitor._control_mapping.update(with_controls)
        visitable.accept(subvisitor)
        return subvisitor._commands

    def on_qubit_declaraion(self, declaration: QubitDeclarationNode) -> None:
        declaration.get_qubit().set_target_qubit_id(self._rsrc.allocate_qubit())

    def on_qubit(self, qubit: QubitNode) -> None:
        self._control_mapping[qubit.get_id()] = 1

    def on_cvar(self, bit: CBitNode) -> None:
        bit.set_id(self._rsrc.allocate_bit())

    def on_inv(self, inv: InvNode) -> None:
        self._commands.extend(self._inversed(self._get_commands_recursive(inv.get_body())))

    def on_if_then(self, if_then: IfThenNode) -> None:
        qubits_counter = self._rsrc.get_min_unused_qubit_id()
        cvis = CompileVisitor(self._rsrc)
        if_then.get_condition().accept(cvis)
        if_commands = cvis._commands

        then_commands = self._get_commands_recursive(if_then.get_then_body(), cvis._control_mapping)

        self._commands.extend(
            if_commands +
            then_commands +
            self._inversed(if_commands)
        )

        num_ancillas = self._rsrc.get_min_unused_qubit_id() - qubits_counter
        self._rsrc.free_qubits(num_ancillas)

    def on_if_then_else(self, if_then_else: IfThenElseNode) -> None:
        qubits_counter = self._rsrc.get_min_unused_qubit_id()
        cvis = CompileVisitor(self._rsrc)
        if_then_else.get_condition().accept(cvis)

        cvis._commands.extend(
            CompileVisitor._get_reduced_commands(
                1,
                cvis._control_mapping,
                cvis._rsrc
            )
        )

        if_commands = cvis._commands

        then_commands: List[ICommand] = self._get_commands_recursive(
            if_then_else.get_then_body(),
            cvis._control_mapping
        )

        if len(cvis._control_mapping) == 0: # If(All([])).Then(...).Else(...)
            self._commands.extend(
                if_commands +
                then_commands +
                self._inversed(if_commands)
            )

        elif len(cvis._control_mapping) == 1: # Only one qubit could be easily inverted
            else_commands: List[ICommand] = self._get_commands_recursive(
                if_then_else.get_else_body(),
                CompileVisitor._invert_control_qubits(cvis._control_mapping)
            )

            self._commands.extend(
                if_commands +
                then_commands +
                else_commands +
                self._inversed(if_commands)
            )

        else:
            assert(False)

        num_ancillas = self._rsrc.get_min_unused_qubit_id() - qubits_counter
        self._rsrc.free_qubits(num_ancillas)

    def on_if_flip(self, if_flip: IfFlipNode) -> None:
        qubits_counter = self._rsrc.get_min_unused_qubit_id()
        cvis = CompileVisitor(self._rsrc)
        if_flip.get_condition().accept(cvis)

        cvis._commands.extend(
            CompileVisitor._get_reduced_commands(
                2,
                cvis._control_mapping,
                cvis._rsrc
            )
        )

        cvis._commands.extend(
            CompileVisitor._get_qubit_negation_commands(cvis._control_mapping)
        )
        control_qubit_ids = list(cvis._control_mapping)

        if_commands: List[ICommand] = cvis._commands

        flip_command = GateCmd(
            Z_GATE,
            control_qubit_ids[-1],
            control_qubit_ids=set(control_qubit_ids[:-1])
        )

        self._commands.extend(
            if_commands +
            [flip_command] +
            self._inversed(if_commands)
        )

        num_ancillas = self._rsrc.get_min_unused_qubit_id() - qubits_counter
        self._rsrc.free_qubits(num_ancillas)

    def _get_on_gate_commands(self, node: GateNode) -> List[ICommand]:
        if not self._control_mapping:
            return [GateCmd(node.gate, node.get_target_qubit_id(), params=node.params)]

        negate_negative_commands : List[ICommand] = []

        for qubit_id, mask in self._control_mapping.items():
            if mask == 0:
                negate_negative_commands.append(GateCmd(X_GATE, qubit_id))

        num_ancillas = 0
        commands: List[ICommand]
        control_commands: List[ICommand] = []
        control_qubit_ids = list(self._control_mapping)
        max_controls = 2 if node.gate == X_GATE else 1  # TODO(adsz): to be defined by gate / target architecture

        while len(control_qubit_ids) > max_controls:
            control_1 = control_qubit_ids.pop(0)
            control_2 = control_qubit_ids.pop(0)
            ancilla = self._rsrc.allocate_qubit()
            num_ancillas += 1
            control_qubit_ids.append(ancilla)
            control_commands.append(
                GateCmd(X_GATE, ancilla, control_qubit_ids={control_1, control_2})
            )

        controlled_command = GateCmd(
            node.gate,
            node.get_target_qubit_id(),
            params=node.params,
            control_qubit_ids=set(control_qubit_ids)
        )

        commands = (
            control_commands +
            [controlled_command] +
            self._inversed(control_commands)
        )

        self._rsrc.free_qubits(num_ancillas)

        return (
            negate_negative_commands +
            commands +
            self._inversed(negate_negative_commands)
        )

    def on_gate(self, node: GateNode) -> None:
        self._commands.extend(self._get_on_gate_commands(node))

    def _inversed(self, commands: Union[ICommand, List[ICommand]]) -> List[ICommand]:
        def inverse_command(command: ICommand):
            if not isinstance(command, GateCmd):
                raise ValueError(f"Inverse of {type(command)} is impossible.")

            inv_gate, inv_params = invert_gate(command._gate, command._params)

            return GateCmd(
                inv_gate,
                command.get_target_qubit_id(),
                command.get_control_qubit_ids(),
                inv_params
            )

        return [inverse_command(command) for command in to_list(commands)[::-1]]

    def on_match(self, match: MatchNode) -> None:
        controls: List[QubitNode] = match.get_control_qubits()
        mask: List[int] = match.get_mask()

        for (control, bit) in zip(controls, mask):
            subvisitor = CompileVisitor(self._rsrc)
            control.accept(subvisitor)
            self._commands.extend(subvisitor._commands)
            assert len(subvisitor._control_mapping) == 1

            if bit == 1:
                self._control_mapping.update(subvisitor._control_mapping)
            elif bit == 0:
                assert len(subvisitor._control_mapping) <= 1
                self._control_mapping.update(
                    CompileVisitor._invert_control_qubits(subvisitor._control_mapping)
                )
            else:
                raise Exception("Syntax error")

    def on_not(self, not_: NotNode) -> None:
        subvisitor = CompileVisitor(self._rsrc)
        not_.get_condition().accept(subvisitor)

        if len(subvisitor._control_mapping) <= 1:
            self._control_mapping.update(
                CompileVisitor._invert_control_qubits(subvisitor._control_mapping))
        else:
            control_bits, cccu_commands = CompileVisitor._get_cccu_commands(
                subvisitor._control_mapping,
                self._rsrc,
                max_num_qubits=1
            )
            assert len(control_bits) == 1
            result_bit = list(control_bits)[0]

            self._commands.extend(cccu_commands)
            self._control_mapping[result_bit] = 0

    def on_measure(self, measure: MeasurementNode) -> None:
        self._commands.append(
            MeasurementCmd(
                measure.get_qubit().get_id(),
                measure.get_bit().get_id()
            )
        )

    def on_reset(self, reset: ResetNode) -> None:
        self._commands.append(ResetCmd(reset.get_qubit().get_id()))
