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

from itertools import chain
from typing import List, Set, Tuple

from builtin_arithmetics import invert_gate
from quasar_cmd import ICommand, ICmdVisitor, \
  GateCmd, MeasurementCmd, ResetCmd


class _CmdStackInserterVisitor(ICmdVisitor):
  def run(
    self,
    commands: List[ICommand],
    commands_stack: List[List[Tuple[int, ICommand]]]
  ) -> List[List[Tuple[int, ICommand]]]:

    #
    # Stacks for individual qubits, representing all the gates/operations/...
    #   affecting that qubit, putting the latest applied operation on the top of the stack.
    #
    # Prog: X(0), X(1), CX(1, 2), CCX(0, 1, 2), ...
    #
    #             [CCX(0,1,2)]
    # [CCX(0,1,2)][CX(1,2)   ][CCX(0,1,2)]
    # [X(0)      ][X(1)      ][CX(1,2)   ]
    # [----Q0----][----Q1----][----Q2----]...[----QN----]
    #
    self._commands_stack = commands_stack

    self._id = 0

    for (id_, command) in enumerate(commands):
      self.set_id(id_)
      command.accept(self)

    return self._commands_stack

  def set_id(self, id_: int) -> None:
    self._id = id_

  def on_gate(self, cmd: GateCmd) -> None:
    affected_qubit_ids: Set[int] = {cmd._target_qubit_id} | cmd._control_qubit_ids

    inverse_gate, inverse_params = invert_gate(cmd._gate, cmd._params)

    eliminate = True
    for qubit_id in affected_qubit_ids:
      if not self._commands_stack[qubit_id]:
        eliminate = False
        continue
      _, last_cmd = self._commands_stack[qubit_id][-1]
      if not isinstance(last_cmd, GateCmd):
        eliminate = False
        continue
      if last_cmd._control_qubit_ids != cmd._control_qubit_ids:
        eliminate = False
      if last_cmd._target_qubit_id != cmd._target_qubit_id:
        eliminate = False
      if last_cmd._gate != inverse_gate:
        eliminate = False
      if last_cmd._params != inverse_params:
        # TODO(adsz): Allow approx.
        eliminate = False

    if eliminate:
      for qubit_id in affected_qubit_ids:
        self._commands_stack[qubit_id].pop()
    else:
      for qubit_id in affected_qubit_ids:
        self._commands_stack[qubit_id].append((self._id, cmd))

  def on_program(self, commands: List[ICommand]) -> None:
    pass

  def on_measurement(self, m: MeasurementCmd) -> None:
    self._commands_stack[m.get_target_qubit_id()].append((self._id, m))

  def on_reset(self, reset: ResetCmd) -> None:
    self._commands_stack[reset.get_target_qubit_id()].append((self._id, reset))

#
##
#

class QuasarOpt:
  @staticmethod
  def _serialize(commands_stacks: List[List[Tuple[int, ICommand]]]) -> List[ICommand]:
    flat = chain.from_iterable(commands_stacks)
    unique = dict(flat).items()
    return [cmd for (_, cmd) in sorted(unique)]

  @staticmethod
  def run(commands: List[ICommand], max_used_qubit_id: int) -> List[ICommand]:
    commands_stacks: List[List[Tuple[int, ICommand]]] = [[] for _ in range(max_used_qubit_id + 1)]
    commands_stacks = _CmdStackInserterVisitor().run(commands, commands_stacks)
    return QuasarOpt._serialize(commands_stacks)
