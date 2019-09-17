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

from typing import Any, List, Union

from b2.qcompiler.qcompiler import All, CNot, If, Inv, X, Program, Qubit

#
##
#

def __number_of_digits(value: int, base=10) -> int:
    if (value == 0):
        return 0
    else:
        return 1 + __number_of_digits(value // base, base)


def _number_of_digits(value: int, base=10) -> int:
    return max(1, __number_of_digits(value, base))


def _number_of_bits(value: int) -> int:
    return _number_of_digits(value, base=2)


def _to_binary_mask(value: int) -> List[int]:
    if (value == 0):
        return []

    return _to_binary_mask(value // 2) + [value % 2]


def _to_list(obj: Union[Any, List[Any]]) -> List[Any]:
    if isinstance(obj, list):
        return obj
    else:
        return _to_list([obj])


def _list_intersection(list1: List[Any], list2: List[Any]) -> List[Any]:
    return [x for x in list1 if x in list2]


def _list_xor(list1: List[Any], list2: List[Any]) -> List[Any]:
    return [x for x in list1 if x not in list2] + [x for x in list2 if x not in list1]

#
##
#

def Set(
    qs: List[Qubit],
    value: int
) -> Program:
    if (value == 0) or (len(qs) == 0):
        return Program()

    if (value % 2 == 1):
        return Program(X(qs[-1])) + Set(qs[0: -1], value//2)
    else:
        return Set(qs[0: -1], value//2)


def Inc(
    qs: List[Qubit]
) -> Program:
    prgm = Program()

    for i in range(len(qs) - 1):
        prgm += If(All(qs[i + 1: ])).Then(
            X(qs[i])
        )

    prgm += X(qs[-1])

    return prgm


def Dec(
    qs: List[Qubit]
) -> Program:
    return Program(Inv(Inc(qs)))


def Swap(
    qs1: Union[Qubit, List[Qubit]],
    qs2: Union[Qubit, List[Qubit]]
) -> Program:
    qs1 = _to_list(qs1)
    qs2 = _to_list(qs2)

    prgm = Program()

    for (q1, q2) in zip(qs1, qs2):
        prgm += CNot(q1, q2)
        prgm += CNot(q2, q1)
        prgm += CNot(q1, q2)

    return prgm


def Equal(
    qs1: Union[Qubit, List[Qubit]],
    qs2: Union[Qubit, List[Qubit]]
) -> Program:
    qs1 = _to_list(qs1)
    qs2 = _to_list(qs2)

    prgm = Program()

    for (q1, q2) in zip(qs1, qs2):
        prgm += X(q1)
        prgm += CNot(q1, q2)
        prgm += X(q1)

    return prgm
