#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the idict project.
#  Please respect the license - more about this in the section (*) below.
#
#  idict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  idict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with idict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.
from functools import cached_property
from json import dumps
from operator import rshift as aop
from operator import xor as cop
from random import Random
from typing import Union, Callable

from garoupa import ø40
from ldict.core.base import AbstractLazyDict
from ldict.customjson import CustomJSONEncoder
from ldict.parameter.abslet import AbstractLet


class iLet(AbstractLet):
    """
    Set values or sampling intervals for parameterized functions

    >>> from idict import idict, let
    >>> f = lambda x,y, a=[-1,-0.9,-0.8,...,1]: {"z": a*x + y}
    >>> f_a = let(f, a=0)
    >>> f_a
    λ{'a': 0}
    >>> d = idict(x=5,y=7)
    >>> d2 = d >> f_a
    >>> d2.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(a x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> d2.evaluate()
    >>> d2.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": 7,
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> from random import Random
    >>> d2 = d >> Random(0) >> let(f, a=[8,9])
    >>> d2.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(a x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> d2.evaluate()
    >>> d2.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": 52,
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> let(f, a=5) >> {"x": 5, "y": 7}
    «λ{'a': 5} × {'x': 5, 'y': 7}»
    >>> (idict({"x": 5, "y": 7}) >> let(f, a=5)).show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(a x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> from ldict.core.appearance import decolorize
    >>> print(decolorize(str(let(f, a=5) >> idict({"x": 5, "y": 7}))))
    «λ{'a': 5} × {
        "x": 5,
        "y": 7,
        "_id": "BB_fad4374ca911f344859dab8e4b016ba2fe65b",
        "_ids": "GS_cb0fda15eac732cb08351e71fc359058b93bd WK_6ba95267cec724067d58b3186ecbcaa4253ad"
    }»
    >>> let(f, a=5) >> ["mycache"]
    «λ{'a': 5} × ↑»
    >>> from idict.parameter.ifunctionspace import iFunctionSpace
    >>> let(f, a=5) >> iFunctionSpace()
    «λ{'a': 5}»
    >>> iFunctionSpace() >> let(f, a=5)
    «λ{'a': 5}»
    >>> (lambda x: {"z": x*8}) >> let(f, a=5)
    «λ × λ{'a': 5}»
    >>> d = {"x":3, "y": 8} >> let(f, a=5)
    >>> d.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(a x y)",
        "x": 3,
        "y": 8,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)",
            "y": "7Z_fb43f53bd25b4452c84de6ba3b3c5ffb29e31 (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> print(d.z)
    23
    >>> d >>= Random(0) >> let(f, a=[1,2,3]) >> let(f, a=[9,8,7])
    >>> d.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(a x y)",
        "x": 3,
        "y": 8,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)",
            "y": "7Z_fb43f53bd25b4452c84de6ba3b3c5ffb29e31 (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> print(d.z)
    32
    """

    def __init__(self, f, identity=ø40, **kwargs):
        from idict.core.idict_ import Idict

        super().__init__(f, Idict, config=None)
        self.config = {k: kwargs[k] for k in sorted(kwargs.keys())}
        #     TODO (minor): iLet needs to detect the identity from idict if it is induced by one
        self.identity = identity

    @cached_property
    def bytes(self):
        return dumps(self.config, sort_keys=True, cls=CustomJSONEncoder).encode()

    def __repr__(self):
        return "λ" + str(self.config)

    def __rrshift__(self, left: Union[dict, list, Random, Callable, "iLet"]):
        """
        >>> from idict.parameter.ilet import iLet
        >>> ({"x":5} >> iLet(lambda x=None:{"x": x**2}, x=5)).show(colored=False)  # doctest:+ELLIPSIS
        {
            "x": "→(x)",
            "_id": "...",
            "_ids": {
                "x": "..."
            }
        }
        >>> [{}] >> iLet(lambda x=None:{"x": x**2}, x=5)
        «↑ × λ{'x': 5}»
        >>> from idict import Ø, idict
        >>> d = idict() >> (Ø >> iLet(lambda x=None:{"x": x**2}, x=5))
        >>> d.show(colored=False)  # doctest:+ELLIPSIS
        {
            "x": "→(x)",
            "_id": "...",
            "_ids": {
                "x": "..."
            }
        }
        """
        from idict import iEmpty

        if isinstance(left, iEmpty):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(self)
        if isinstance(left, dict) and not isinstance(left, AbstractLazyDict):
            from idict.core.idict_ import Idict

            return Idict(left, identity=self.identity) >> self
        if isinstance(left, (list, Random, Callable)):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(left, aop, self)
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other: Union[dict, list, Random, Callable, "iLet", AbstractLazyDict]):
        """
        >>> iLet(lambda x:{"x": x**2}, x=5) >> [1]
        «λ{'x': 5} × ↑»
        """

        if isinstance(other, (dict, list, Random, Callable, iLet)):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(self, aop, other)
        return NotImplemented  # pragma: no cover

    def __rxor__(self, left: Union[dict, list, Random, Callable, "iLet"]):
        if isinstance(left, (dict, list, Random, Callable)) and not isinstance(left, AbstractLazyDict):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(left, cop, self)
        return NotImplemented  # pragma: no cover

    def __xor__(self, other: Union[dict, list, Random, Callable, "iLet", AbstractLazyDict]):
        if isinstance(other, (dict, list, Random, Callable, iLet)):
            from idict.parameter.ifunctionspace import iFunctionSpace

            return iFunctionSpace(self, cop, other)
        return NotImplemented  # pragma: no cover

    def __getattr__(self, item):  # pragma: no cover
        from idict.core.idict_ import Idict

        if hasattr(Idict, item):  # pragma: no cover
            raise Exception(
                "An expression will only become an 'idict' after being fed with data.\n"
                "E.g.: 'e = let(f, par1=5)' and 'e = Ø >> f' are non-applied expressions."
                "They need some input values to become an idict, e.g.: '{y=3} >> e'\n"
                f"Parameters provided for {self.f}: {self.config}"
            )
