import unittest

from qiskit.circuit.library.standard_gates import CXGate

from builtin_gates import X_GATE
from quasar_qiskit import QiskitFormatter, QiskitBuilder


class QiskitFormatterTest(unittest.TestCase):

    def test_formatter(self) -> None:
        f = QiskitFormatter()
        self.assertEqual(f.gate(X_GATE, 10, [], {20}),
                         'self.circuit.cx(self.q_register[20], self.q_register[10])')

    def test_builder(self) -> None:
        f = QiskitBuilder()
        f.set_qubits_counter(3)
        f.get_headers()
        f.gate(X_GATE, 1, [], {2})

        cdata = f.get_circuit().data
        self.assertEqual(len(cdata), 1)
        cmd, qs, cs = cdata[0]
        self.assertIsInstance(cmd, CXGate)
        self.assertSetEqual({q.index for q in qs}, {1, 2})
        self.assertEqual(len(cs), 0)


if __name__ == '__main__':
    unittest.main()
