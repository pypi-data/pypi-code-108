# -*- coding: utf-8 -*-
"""
types.py
~~~~~~~~
Custom type declarations.

:copyright: (c) 2021 by Jochen Gerhaeusser.
:license: BSD, see LICENSE for details
"""

from typing import *

#: Numeric type
Number = Union[bool, int, float]

#: Sample type
Sample = Union[Number, str]

#: Samples type
Samples = Union[List[Sample], Iterable[Sample], Iterable[None]]

#: Operand type
Operand = Union[Iterable[Sample], Number]

#: Data frame type
DataFrame = Dict[str, Iterable[Sample]]
