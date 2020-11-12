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

from math import asin, pi, sqrt
from typing import Callable, List

from quasar import ASTNode, H, Flip, If, Program, Qubit, Zero

#
##
#

def Grover(
    qubits: List[Qubit],
    predicate: ASTNode
) -> Program:
    prgm = Program()

    for qubit in qubits:
        prgm += H(qubit)

    # IBM QisKit http://tiny.cc/wn7uaz
    #number_of_iters : Callable[[int], int] = \
    #    lambda size: int(sqrt(2 ** size))

    #arxiv http://tiny.cc/mo7uaz
    number_of_iters : Callable[[int], int] = \
        lambda size: int(pi / 4 / asin(sqrt(1 / (2 ** size))))

    for _ in range(number_of_iters(len(qubits))):
        prgm += If(predicate).Flip()

        for qubit in qubits:
            prgm += H(qubit)

        prgm += If(Zero(qubits)).Flip()

        for qubit in qubits:
            prgm += H(qubit)

        prgm += Flip(qubits)

    return prgm
