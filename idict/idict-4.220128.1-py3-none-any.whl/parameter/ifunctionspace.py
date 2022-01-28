#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the ldict project.
#  Please respect the license - more about this in the section (*) below.
#
#  ldict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ldict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ldict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.
import operator
from itertools import chain, repeat
from operator import rshift as aop
from operator import xor as cop
from random import Random
from typing import Union, Callable

from ldict.core.base import AbstractLazyDict

from idict.parameter.ilet import iLet


class iFunctionSpace:
    """Aglutination for future application

    >>> from idict import idict, empty
    >>> fs = iFunctionSpace({"x": 5})
    >>> fs
    «{'x': 5}»
    >>> (idict(y=7) >> fs).show(colored=False)
    {
        "y": 7,
        "x": 5,
        "_id": "BB_fad4374ca911f344859dab8e4b016ba2fe65b",
        "_ids": {
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
        }
    }
    >>> fs >>= idict(y=7)
    >>> from ldict.core.appearance import decolorize
    >>> print(decolorize(str(fs)))
    «{'x': 5} × {
        "y": 7,
        "_id": "WK_6ba95267cec724067d58b3186ecbcaa4253ad",
        "_ids": "WK_6ba95267cec724067d58b3186ecbcaa4253ad"
    }»
    >>> fs >>= lambda x,y: {"z": x*y}
    >>> print(decolorize(str(fs)))
    «{'x': 5} × {
        "y": 7,
        "_id": "WK_6ba95267cec724067d58b3186ecbcaa4253ad",
        "_ids": "WK_6ba95267cec724067d58b3186ecbcaa4253ad"
    } × λ»
    """

    def __init__(self, *args):
        self.functions_and_ops = args

    @staticmethod
    def fromfunctions(*functions):
        return iFunctionSpace(*intersperse(functions, operator.rshift))

    def __rrshift__(self, left: Union[dict, list, Random, Callable, iLet]):
        if isinstance(left, AbstractLazyDict):
            from idict.core.idict_ import Idict

            return reduce3(lambda a, op, b: op(a, b), (left, aop) + self.functions_and_ops)
        if isinstance(left, dict):
            from idict.core.idict_ import Idict

            # TODO (minor):
            #  iFunctionSpace lacks 'self.identity' to be able to provide here, e.g., number of digits to Idict(..)

            return reduce3(lambda a, op, b: op(a, b), (Idict(left), aop) + self.functions_and_ops)
        if isinstance(left, (list, Random, Callable, iLet)):
            return iFunctionSpace(left, aop, *self.functions_and_ops)
        return NotImplemented

    def __rshift__(self, other: Union[dict, list, Random, Callable, iLet, AbstractLazyDict, "iFunctionSpace"]):
        if isinstance(other, (dict, list, Random, Callable, iLet)):
            return iFunctionSpace(*self.functions_and_ops, aop, other)
        if isinstance(other, iFunctionSpace):
            return iFunctionSpace(*self.functions_and_ops, aop, *other.functions_and_ops)
        return NotImplemented

    def __rxor__(self, left: Union[dict, list, Random, Callable, iLet]):
        if isinstance(left, (dict, list, Random, Callable, iLet)) and not isinstance(left, AbstractLazyDict):
            return iFunctionSpace(left, aop, *self.functions_and_ops)
        return NotImplemented

    def __xor__(self, other: Union[dict, list, Random, Callable, iLet, AbstractLazyDict, "iFunctionSpace"]):
        if isinstance(other, (dict, list, Random, Callable, iLet, AbstractLazyDict)):
            return iFunctionSpace(*self.functions_and_ops, cop, other)
        if isinstance(other, iFunctionSpace):
            return iFunctionSpace(*self.functions_and_ops, cop, *other.functions_and_ops)
        return NotImplemented

    def __repr__(self):
        txt = []
        for f in self.functions_and_ops:
            if str(f).startswith("<built-in "):  # Skip >> and ^.
                continue
            if isinstance(f, list):
                s = "↑"
            elif isinstance(f, Random):
                s = "~"
            elif str(f).startswith("<function "):
                s = "λ"
            else:
                s = str(f)
            txt.append(s)
        return "«" + " × ".join(txt) + "»"


def reduce3(f, lst):
    """
    Based on https://stackoverflow.com/a/69667949/9681577
    """
    lst_iter = iter(lst)
    next_args = []
    while True:
        try:
            while len(next_args) < 3:
                next_args.append(next(lst_iter))
        except StopIteration:
            break
        next_args = [f(*next_args)]
    return next_args[0]


def intersperse(lst, fill=...):
    """
    >>> list(intersperse([1,2,3,4]))
    [1, Ellipsis, 2, Ellipsis, 3, Ellipsis, 4]
    """
    return chain(*zip(lst[:-1], repeat(fill)), [lst[-1]])
