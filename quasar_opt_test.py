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

from typing import List
import unittest

from builtin_gates import X_GATE, U3_GATE, Y_GATE, Z_GATE, H_GATE
from quasar_cmd import ICommand, ResetCmd, MeasurementCmd, GateCmd
from quasar_opt import QuasarOpt

#
##
#

class QCompilerTest(unittest.TestCase):
    def __init__(self, *args) -> None:
        super().__init__(*args)

    def _test_one_qubit_command_1(self, cmd_class) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class, 0)
      cmd_2: ICommand = GateCmd(cmd_class, 0)
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_one_qubit_command_2(self, cmd_class) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class, 0)
      cmd_2: ICommand = GateCmd(cmd_class, 1)
      cmd_3: ICommand = GateCmd(cmd_class, 1)
      cmd_4: ICommand = GateCmd(cmd_class, 0)
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_one_qubit_command_3(self, cmd_class) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class, 0)
      cmd_2: ICommand = GateCmd(cmd_class, 1)
      commands: List[ICommand] = [cmd_1,cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def _test_one_qubit_command_4(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 0)
      cmd_2: ICommand = GateCmd(cmd_class, 1)
      cmd_3: ICommand = GateCmd(cmd_class, 1)
      cmd_4: ICommand = GateCmd(cmd_class, 2)
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_4]
      self.assertListEqual(actual, expected)

    def _test_one_qubit_commands_1(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 4
      cmd_1: ICommand = GateCmd(cmd_class_1, 0)
      cmd_2: ICommand = GateCmd(cmd_class_2, 1)
      cmd_3: ICommand = GateCmd(cmd_class_1, 2)
      cmd_4: ICommand = GateCmd(cmd_class_2, 3)
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      self.assertListEqual(actual, expected)

    def _test_one_qubit_commands_2(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 1
      cmd_1: ICommand = GateCmd(cmd_class_1, 0)
      cmd_2: ICommand = GateCmd(cmd_class_2, 0)
      cmd_3: ICommand = GateCmd(cmd_class_2, 0)
      cmd_4: ICommand = GateCmd(cmd_class_1, 0)
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_one_qubit_command_7(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class_1, 0)
      cmd_2: ICommand = GateCmd(cmd_class_2, 1)
      cmd_3: ICommand = GateCmd(cmd_class_2, 1)
      cmd_4: ICommand = GateCmd(cmd_class_1, 0)
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_two_qubits_command_1(self, cmd_class) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_two_qubits_command_2(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={1})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_command_3(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={1})
      cmd_3: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_command_4(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class, 0, control_qubit_ids={1})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_command_5(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class, 0, control_qubit_ids={1})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_command_6(self, cmd_class) -> None:
      min_unused_qubit_id = 4
      cmd_1: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class, 3, control_qubit_ids={2})
      cmd_3: ICommand = GateCmd(cmd_class, 1, control_qubit_ids={2})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_commands_1(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class_2, 1, control_qubit_ids={0})
      cmd_3: ICommand = GateCmd(cmd_class_2, 1, control_qubit_ids={0})
      cmd_4: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_two_qubits_commands_2(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class_2, 2, control_qubit_ids={1})
      cmd_3: ICommand = GateCmd(cmd_class_2, 2, control_qubit_ids={1})
      cmd_4: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_two_qubits_commands_3(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class_2, 0, control_qubit_ids={1})
      cmd_3: ICommand = GateCmd(cmd_class_2, 1, control_qubit_ids={0})
      cmd_4: ICommand = GateCmd(cmd_class_1, 0, control_qubit_ids={1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_1(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_2(self, cmd_class) -> None:
      min_unused_qubit_id = 4
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(cmd_class, 3, control_qubit_ids={1, 2})
      cmd_3: ICommand = GateCmd(cmd_class, 3, control_qubit_ids={1, 2})
      cmd_4: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_3(self, cmd_class) -> None:
      min_unused_qubit_id = 4
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(cmd_class, 3, control_qubit_ids={1, 2})
      commands: List[ICommand] = [cmd_1,cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_4(self, cmd_class) -> None:
      min_unused_qubit_id = 5
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(cmd_class, 3, control_qubit_ids={1, 2})
      cmd_3: ICommand = GateCmd(cmd_class, 3, control_qubit_ids={1, 2})
      cmd_4: ICommand = GateCmd(cmd_class, 4, control_qubit_ids={2, 3})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3, cmd_4]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_4]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_5(self, cmd_class) -> None:
      min_unused_qubit_id = 5
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(cmd_class, 0, control_qubit_ids={2, 1})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_6(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(X_GATE, 0)
      cmd_3: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_7(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(X_GATE, 1)
      cmd_3: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_command_8(self, cmd_class) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = GateCmd(X_GATE, 2)
      cmd_3: ICommand = GateCmd(cmd_class, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_one_qubit_reset_command_1(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class_1, 0)
      cmd_2: ICommand = cmd_class_2(0)
      cmd_3: ICommand = GateCmd(cmd_class_1, 0)
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_reset_command_1(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      cmd_2: ICommand = cmd_class_2(0)
      cmd_3: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_reset_command_2(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(cmd_class_2, 1)
      cmd_3: ICommand = GateCmd(cmd_class_1, 1, control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_reset_command_1(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class_1, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = cmd_class_2(0)
      cmd_3: ICommand = GateCmd(cmd_class_1, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_reset_command_2(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class_1, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = cmd_class_2(1)
      cmd_3: ICommand = GateCmd(cmd_class_1, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_three_qubits_reset_command_3(self, cmd_class_1, cmd_class_2) -> None:
      min_unused_qubit_id = 3
      cmd_1: ICommand = GateCmd(cmd_class_1, 2, control_qubit_ids={0, 1})
      cmd_2: ICommand = cmd_class_2(2)
      cmd_3: ICommand = GateCmd(cmd_class_1, 2, control_qubit_ids={0, 1})
      commands: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2, cmd_3]
      self.assertListEqual(actual, expected)

    def _test_one_qubit_u3_command_1(self) -> None:
      min_unused_qubit_id = 1
      cmd_1: ICommand = GateCmd(U3_GATE, 0, params=[1.1, 2.2, 3.3])
      cmd_2: ICommand = GateCmd(U3_GATE, 0, params=[-1.1, -3.3, -2.2])
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_one_qubit_u3_command_2(self) -> None:
      min_unused_qubit_id = 1
      cmd_1: ICommand = GateCmd(U3_GATE, 0, params=[1.1, 2.2, 3.3])
      cmd_2: ICommand = GateCmd(U3_GATE, 0, params=[1.1, 3.3, 2.2])
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def _test_two_qubits_cu3_command_1(self) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(U3_GATE, 1, params=[2.2, 3.3, 4.4], control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(U3_GATE, 1, params=[-2.2, -4.4, -3.3], control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = []
      self.assertListEqual(actual, expected)

    def _test_two_qubits_cu3_command_2(self) -> None:
      min_unused_qubit_id = 2
      cmd_1: ICommand = GateCmd(U3_GATE, 1, params=[2.2, 3.3, 4.4], control_qubit_ids={0})
      cmd_2: ICommand = GateCmd(U3_GATE, 1, params=[2.2, 3.3, 4.4], control_qubit_ids={0})
      commands: List[ICommand] = [cmd_1, cmd_2]
      actual: List[ICommand] = QuasarOpt().run(commands, min_unused_qubit_id)
      expected: List[ICommand] = [cmd_1, cmd_2]
      self.assertListEqual(actual, expected)

    def test_optimizer(self) -> None:
      builtins = (X_GATE, Y_GATE, Z_GATE, H_GATE)
      builtins2 = (Y_GATE, Z_GATE, H_GATE, X_GATE)

      for cmd_1q_class in builtins:
        self._test_one_qubit_command_1(cmd_1q_class)
        self._test_one_qubit_command_2(cmd_1q_class)
        self._test_one_qubit_command_3(cmd_1q_class)
        self._test_one_qubit_command_4(cmd_1q_class)

      for (cmd_1q_class_1, cmd_1q_class_2) in zip(builtins, builtins2):
        self._test_one_qubit_commands_1(cmd_1q_class_1, cmd_1q_class_2)
        self._test_one_qubit_commands_2(cmd_1q_class_1, cmd_1q_class_2)

      self._test_one_qubit_u3_command_1()
      self._test_one_qubit_u3_command_2()

      def _MeasurementCmdWrapper(qubit_id):
        return MeasurementCmd(qubit_id=qubit_id, bit_id=0)

      for cmd_reset in [ResetCmd, _MeasurementCmdWrapper]:
        for cmd_1q_class in builtins:
          self._test_one_qubit_reset_command_1(cmd_1q_class, cmd_reset)

      for cmd_2q_class in builtins:
        self._test_two_qubits_command_1(cmd_2q_class)
        self._test_two_qubits_command_2(cmd_2q_class)
        self._test_two_qubits_command_3(cmd_2q_class)
        self._test_two_qubits_command_4(cmd_2q_class)
        self._test_two_qubits_command_5(cmd_2q_class)
        self._test_two_qubits_command_6(cmd_2q_class)

      for (cmd_2q_class_1, cmd_2q_class_2) in zip(builtins, builtins2):
        self._test_two_qubits_commands_1(cmd_2q_class_1, cmd_2q_class_2)
        self._test_two_qubits_commands_2(cmd_2q_class_1, cmd_2q_class_2)
        self._test_two_qubits_commands_3(cmd_2q_class_1, cmd_2q_class_2)

      self._test_two_qubits_cu3_command_1()
      self._test_two_qubits_cu3_command_2()

      for cmd_reset in [ResetCmd, _MeasurementCmdWrapper]:
        for cmd_2q_class in builtins:
          self._test_two_qubits_reset_command_1(cmd_2q_class, cmd_reset)

      for cmd_3q_class in (X_GATE,):
        self._test_three_qubits_command_1(cmd_3q_class)
        self._test_three_qubits_command_2(cmd_3q_class)
        self._test_three_qubits_command_3(cmd_3q_class)
        self._test_three_qubits_command_4(cmd_3q_class)
        self._test_three_qubits_command_5(cmd_3q_class)
        self._test_three_qubits_command_6(cmd_3q_class)
        self._test_three_qubits_command_7(cmd_3q_class)
        self._test_three_qubits_command_8(cmd_3q_class)

      for cmd_reset in [ResetCmd, _MeasurementCmdWrapper]:
        for cmd_3q_class in (X_GATE,):
          self._test_three_qubits_reset_command_1(cmd_3q_class, cmd_reset)
          self._test_three_qubits_reset_command_2(cmd_3q_class, cmd_reset)
          self._test_three_qubits_reset_command_3(cmd_3q_class, cmd_reset)


if __name__ == '__main__':
    unittest.main()
