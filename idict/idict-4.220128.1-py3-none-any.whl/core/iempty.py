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
from typing import Callable, Dict, Union

from ldict.core.base import AbstractLazyDict
from ldict.exception import DependenceException, UndefinedSeed

from idict.core.frozenidentifieddict import FrozenIdentifiedDict
from idict.core.idict_ import Idict
from idict.parameter.ilet import iLet


class iEmpty(FrozenIdentifiedDict):
    def __init__(self):
        super().__init__()

    def __rrshift__(self, left: Union[Dict, Callable, iLet]):
        if isinstance(left, dict) and not isinstance(left, AbstractLazyDict):
            return Idict(left, identity=self.identity)
        if callable(left):
            return iLet(left)
        if isinstance(left, iLet):
            return left
        return NotImplemented  # pragma: no cover

    def __rshift__(self, other: Union[Dict, Callable]):
        if isinstance(other, AbstractLazyDict):
            return other
        if isinstance(other, dict):
            return Idict(other, identity=self.identity)
        if callable(other):
            try:
                return Idict(identity=self.identity) >> other
            except (DependenceException, UndefinedSeed):
                return iLet(other)
        return NotImplemented  # pragma: no cover

    __mul__ = __rshift__
