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

from __future__ import annotations

import dataclasses as dtcl
from pathlib import Path as path_t
from typing import Any, Callable, Sequence, Tuple, Union

from numpy import ndarray as array_t

# Can import axes
from cell_tracking_BC.in_out.file.archiver import archiver_t
from cell_tracking_BC.in_out.graphics.type.axes import axes_t
from cell_tracking_BC.in_out.graphics.type.event import event_h


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t:
    @classmethod
    def NewFigureAndAxes(
        cls,
        /,
        *,
        n_rows: int = 1,
        n_cols: int = 1,
        title: str = None,
        offline_version: bool = False,
    ) -> Tuple[figure_t, Union[axes_t, Sequence[axes_t], Sequence[Sequence[axes_t]]]]:
        pass

    def ActivateTightLayout(self, *, pad=1.08, h_pad=None, w_pad=None, rect=None):
        pass

    def Show(
        self,
        /,
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        pass

    @staticmethod
    def ShowAll(
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        pass

    def Update(self, /, *, gently: bool = True) -> None:
        pass

    def Content(self, /) -> array_t:
        pass

    def Save(self, path: Union[str, path_t], /) -> None:
        pass

    def Archive(
        self,
        /,
        *,
        name: str = "figure",
        archiver: archiver_t = None,
    ) -> None:
        pass

    def ActivateEvent(self, event: str, processor: Callable[[event_h], Any], /) -> None:
        pass

    def Close(self) -> None:
        pass
