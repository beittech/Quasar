import unittest

from qiskit import QuantumCircuit

from builtin_gates import X_GATE, Z_GATE
from quasar_qasm import QASMFormatter


class QasmFormatterTest(unittest.TestCase):
    def test_formatter(self) -> None:
        f = QASMFormatter()
        self.assertEqual(f.gate(X_GATE, 10, [], set()).strip(),
                         'x q[10];')
        self.assertEqual(f.gate(X_GATE, 10, [], {20}).strip(),
                         'cx q[20], q[10];')
        self.assertEqual(f.gate(X_GATE, 10, [], {20, 30}).strip(),
                         'ccx q[20], q[30], q[10];')

    def test_is_loadable(self) -> None:
        f = QASMFormatter()
        f.set_qubits_counter(2)
        f.set_bits_counter(1)
        lines = [
            f.gate(X_GATE, 0, [], set()),
            f.gate(Z_GATE, 1, [], {0})
        ]
        lines = f.get_headers() + lines + f.get_footers()
        code = '\n'.join(lines)

        # Just test if it loads with no exceptions
        QuantumCircuit.from_qasm_str(code)


if __name__ == '__main__':
    unittest.main()
