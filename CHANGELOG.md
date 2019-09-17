## Copyright (c) 2019- Beit, Beit.Tech, Beit.Inc
----

# Changelog

## 1.0.1
### Breaking compatibility changes
- `QBit` has been renamed to `Qubit`
- `Program.QBit` has been renamed to `Program.Qubit`
- `Program.QBits` has been renamed to `Program.Qubits`

### Bug fixes
- Fix for `_Program._accept` implementation
- Fix in `Fourier` example. Use `Phase` gate insted of `RZ` one.

### New features
- New [U3]`(phi, theta, lambda)` has been implemented
- New gates `Id`, `RX`, `CRX`, `RY`, `CRY`, `RZ`, `CRZ`, `Phase` have been implemented
- New file `qfourier.py` with Fourier algorithm implementation
- New file `qgrover.py` with Grover algorithm implementation
- New file `qutils.py` with:
  - `Set(qs: List[Qubit], value: int) -> Program` - set clear register to specific little-endian unsigned value.
  - `Inc(qs: List[Qubit]) -> Program` - increment little-endian unsigned value
  - `Dec(qs: List[Qubit]) -> Program` - decrement little-endian unsigned value
  - `Swap(qs1: Union[Qubit, List[Qubit]], qs2: Union[Qubit, List[Qubit]]) -> Program` - swap two registers
  - `Equal(qs1: Union[Qubit, List[Qubit]], qs1: Union[Qubit, List[Qubit]]) -> Program` - check if two registers are equal


[U3]: https://github.com/Qiskit/qiskit-terra/blob/master/qiskit/extensions/standard/u3.py
