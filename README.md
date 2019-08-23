## Copyright (c) 2019- Beit, Beit.Tech, Beit.Inc
----

# Quasar

Quasar is a utility tool to simplify writing quantum assembly code. It helps translate high level `if` statements into a sequence of controlled quantum commands. It can be easily integrated with [IBM Qiskit], [Google Cirq] or [OpenQASM].

Express your thoughts in a high-level way, let Quasar take care about details.

# Features

At the beginning of each program the `Program` object has to be created

```
prgm = Program()
```

Single qubit object can be created as follow

```
qbit_0 = prgm.QBit()
```

An initial value for a qubit can also be provided

```
qbit_1 = prgm.QBit( 1 )
```

Many qubits can be created in one statement

```
qbits = prgm.QBits( [ 0, 1, 0, 1, 0, 1, 0, 1 ] )
```

Instructions are composed either with `+=` and `+` operators

```
prgm += X( qbit_0 ) + Y( qbit_1 ) + Z( qubits[0] )
```

Or with a list syntax

```
prgm += [ X( qbit_0 ) , H( qbit_1 ) , Z( qubits[0] ) ]
```

Quasar simplifies writing `if` statements. It looks almost like in any high-level programming language

```
If( ... ).Then( ... )
If( ... ).Then( ... ).Else( ... )
```

For example

```
If( All( qbit_1 ) ).Then(
    X( qubit_0 )
)
```

Inside an `if` statements some functions can be used

`Any( qubits: List[ QBit ] ) -> Bool`, at least one qubit has to be set to 1

```
If( Any( qubits[0], qubits[1], qubits[2] ) )
```

`Zero( qubits: List[ QBit ] ) -> Bool`, all qubits have to be set to 0

```
If( Zero( qubits[0], qubits[1], qubits[2] ) )
```

`All( qubits: List[ QBit ] ) -> Bool`, all qubits has to be set to 1

```
If( All( qubits[0], qubits[1], qubits[2] ) )
```

`Match( qubits : List[ QBit ], mask: List[int] ) -> Bool`, all qubits has to be set as in a mask

```
If( Match( [qubits[0], qubits[1], qubits[2], qubits[3]], mask=[1, 0, 1, 0] ) )
```

To simplify writing Grover algorithm `If(...).Flip()` statement is provided. `Flip` make phase inversion for all states which satisfy the condition.

```
If( All( qubits[0], qubits[1], qubits[2] ).Flip()
```

# Installation and Requirements

Quasar is a single python file script. It does not have any non-standard dependencies. It is required to have python >= 3.7

# Extension

To generate an assembly code in your own format just define an implementation of the `IQAsmFormatter` class

```python
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
    def x(self, qubit: int) -> str:
        pass

    @abstractmethod
    def y(self, qubit: int) -> str:
        pass

    @abstractmethod
    def z(self, qubit: int) -> str:
        pass

    @abstractmethod
    def h(self, qubit: int) -> str:
        pass

    @abstractmethod
    def cx(self, ctrl_1: int, target: int) -> str:
        pass

    @abstractmethod
    def cy(self, ctrl_1: int, target: int) -> str:
        pass

    @abstractmethod
    def cz(self, ctrl_1: int, target: int) -> str:
        pass

    @abstractmethod
    def ch(self, ctrl_1: int, target: int) -> str:
        pass

    @abstractmethod
    def ccx(self, ctrl_1: int, ctrl_2: int, target: int) -> str:
        pass

    @abstractmethod
    def measure(self, qubit: int, bit: int) -> str:
        pass
```

# Quasar to IBM Qiskit intagration

```python
# Quasar

from quasar import All, H, If, Program, Quasar, X

prgm = Program()
q_bits = prgm.QBits([0, 0])
c_bits = prgm.CBits(2)

prgm += X(q_bits[0])
prgm += If(All(q_bits[0])).Then(
    H(q_bits[1])
)

# Quasar -> OpenQASM

qasm_str = Quasar().to_qasm_str(prgm)

# OpenQASM -> Qiskit

from qiskit import execute, Aer, QuantumCircuit

circuit = QuantumCircuit.from_qasm_str(qasm_str)
result = execute(circuit, Aer.get_backend('statevector_simulator')).result()
print(result.get_statevector(circuit, decimals=3))
```

# Syntax examples

```python
def example_nested_if() -> None:
    prgm = Program()

    q_vars = prgm.QBits(32 * [0])

    prgm += If(All([q_vars[1], q_vars[2], q_vars[3], q_vars[4]])).Then(
        X(q_vars[3]) +
        If(Not(All(q_vars[4]))).Then(
            X(q_vars[5]) + X(q_vars[6])
        ).Else(
            If(All(q_vars[7])).Then(
                [X(q_vars[8]), X(q_vars[9])]
            ).Else(
                [X(q_vars[10]), X(q_vars[11])]
            )
        )
    ).Else(
        If(Not(All(q_vars[11]))).Then(
            X(q_vars[12]) + X(q_vars[13])
        ).Else(
            If(All(q_vars[14])).Then(
                X(q_vars[15]) +
                X(q_vars[16]) +
                If(Not(All(q_vars[17]))).Then(
                    X(q_vars[18]) + X(q_vars[19])
                ).Else(
                    If(All(q_vars[20])).Then(
                        [X(q_vars[21]), X(q_vars[22])]
                    ).Else(
                        [X(q_vars[23]), X(q_vars[24])]
                    )
                )
            ).Else(
                If(Not(All(q_vars[25]))).Then(
                    X(q_vars[26]) + X(q_vars[27])
                ).Else(
                    If(All(q_vars[28])).Then(
                        [X(q_vars[29]), X(q_vars[30])]
                    ).Else(
                        [X(q_vars[31])]
                    )
                )
            )
        )
    )

    print('\n'.join(Quasar().compile(prgm, keep_comments=True)))
```

```python
def example_measurement() -> None:
    prgm = Program()

    q_vars = prgm.QBits([1, 0, 1, 0, 0])
    c_vars = prgm.CBits(5)

    prgm += (
        CX(q_vars[0], q_vars[1]) +
        If(All(q_vars[1])).Then(
            If(All(q_vars[2])).Then(
                CX(q_vars[3], q_vars[4])
            )
        ) +
        Measurement(q_vars[0], c_vars[0])
    )

    print('\n'.join(Quasar().compile(prgm, keep_comments=True)))
```

```python
def example_grover() -> None:
    def Grover(
        qbits: List[QBit],
        predicate: ASTNode
    ) -> Program:
        prgm = Program()

        for qbit in qbits:
            prgm += H(qbit)

        # IBM QisKit http://tiny.cc/wn7uaz
        number_of_iters_1 : Callable[[int], int] = \
            lambda size: int(sqrt(2 ** size))

        # arxiv http://tiny.cc/mo7uaz
        number_of_iters_2 : Callable[[int], int] = \
            lambda size: int(pi / 4 / asin(sqrt(1 / (2 ** size))))

        for _ in range(number_of_iters_1(len(qbits))):
            prgm += If(predicate).Flip()

            for qbit in qbits:
                prgm += H(qbit)

            prgm += If(Zero(qbits)).Flip()

            for qbit in qbits:
                prgm += H(qbit)

            prgm += Flip(qbits)

        return prgm

    prgm = Program()
    qbits = prgm.QBits([0, 0, 0])
    prgm += Grover(qbits, predicate=Match(qbits, mask=[0, 1, 0]))
    print('\n'.join(Quasar().compile(prgm, keep_comments=True)))
```

```python
def example_fourier() -> None:
    def Fourier(
        qbits: List[QBit]
    ) -> Program:
        prgm = Program()

        length = len(qbits)

        for i in range(length):
            prgm += H(qbits[i])

            for j in range(2, length + 1 - i):
                prgm += If(All(qbits[i + j - 1])).Then(
                    RZ(qbits[i], 2 * pi / (2 ** j))
                )

        for i in range(length // 2):
            prgm += CNot(qbits[i], qbits[length - i - 1])
            prgm += CNot(qbits[length - i - 1], qbits[i])
            prgm += CNot(qbits[i], qbits[length - i - 1])

        return prgm

    prgm = Program()
    qbits = prgm.QBits([0, 1])
    prgm += Fourier(qbits)
    print('\n'.join(Quasar().compile(prgm, keep_comments=True)))
```



# License

MIT

[IBM Qiskit]: https://qiskit.org/
[Google Cirq]: https://github.com/quantumlib/Cirq
[OpenQASM]: https://github.com/QISKit/openqasm
