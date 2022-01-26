#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""

import typing as t

if t.TYPE_CHECKING:
    from ..inputs_outputs import SingleOutputs


class Single:
    """TBW."""

    def __init__(self, outputs: "SingleOutputs"):
        self.outputs = outputs

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<outputs={self.outputs!r}>"
