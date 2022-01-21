# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import dataclasses as dcls
import logging as lggg
from typing import ClassVar

from rich.color import Color as color_t
from rich.highlighter import Highlighter as base_highlighter_t
from rich.logging import RichHandler as rich_handler_t
from rich.style import Style as style_t
from rich.text import Text as text_t


@dcls.dataclass(init=False, repr=False, eq=False)
class highlighter_t(base_highlighter_t):
    _WHERE: ClassVar[str] = r"[^:]+:[^:]+:[0-9]+"
    _ACTUAL: ClassVar[str] = r" Actual=[^.]+\."
    _EXPECTED: ClassVar[str] = r" Expected([!<>]=|: )[^.]+\."
    _GRAY_STYLE: ClassVar[style_t] = style_t(color=color_t.from_rgb(150, 150, 150))

    def highlight(self, text: text_t) -> None:
        """"""
        if text.plain[-1] != ".":
            text.append(".")
        text.highlight_regex(self.__class__._WHERE, style=self.__class__._GRAY_STYLE)
        text.highlight_regex(self.__class__._ACTUAL, style="red")
        text.highlight_regex(self.__class__._EXPECTED, style="green")


_HANDLER = rich_handler_t(
    highlighter=highlighter_t(),
    omit_repeated_times=False,
    enable_link_path=False,
    show_path=False,
)
_HANDLER.KEYWORDS = None
lggg.basicConfig(
    level="INFO",
    format="%(module)s:%(funcName)s:%(lineno)d %(message)s",
    datefmt="%Y-%m-%d@%H:%M:%S",
    handlers=[_HANDLER],
)

LOGGER = lggg.getLogger("rich")


def WhereFunction(function: object, /) -> str:
    """"""
    return f"{function.__module__}:{function.__name__}"


def WhereMethod(obj: object, method: object, /) -> str:
    """
    method: Could be a str instead, which would require changing method.__name__ into getattr(cls, method). But if the
        method name changes while forgetting to change the string in the call to WhereMethod accordingly, then an
        exception would be raised here.
    """
    cls = obj.__class__

    return f"{cls.__module__}:{cls.__name__}:{method.__name__}"
