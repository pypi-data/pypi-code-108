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
from multiprocessing import Process as process_t
from typing import Sequence, Tuple, Union

from vedo import Plotter as vedo_figure_t

from cell_tracking_BC.in_out.graphics.context import figure_t as base_figure_t


_UNSHOWN_FIGURES = []
_BBOX_AXES_MARGIN = 0.05


@dtcl.dataclass(init=False, repr=False, eq=False)
class figure_t(vedo_figure_t, base_figure_t):

    bbox: Sequence[Sequence[float]] = None

    @classmethod
    def NewFigureAndAxes(
        cls, /, *, n_rows: int = 1, n_cols: int = 1, title: str = None
    ) -> Tuple[
        figure_t,
        Union[figure_t, Sequence[figure_t], Sequence[Sequence[figure_t]]],
    ]:
        """"""
        figure = cls()
        axes = figure

        _UNSHOWN_FIGURES.append(figure)

        return figure, axes

    def UpdateBBoxFromOne(self, new_point: Sequence[float], /) -> None:
        """"""
        if self.bbox is None:
            self.bbox = (new_point, new_point)
        else:
            minima = [min(_new, _old) for _new, _old in zip(new_point, self.bbox[0])]
            maxima = [max(_new, _old) for _new, _old in zip(new_point, self.bbox[1])]
            self.bbox = (minima, maxima)

    def UpdateBBoxFromMany(
        self, exc_s: Sequence[float], why_s: Sequence[float], zee_s: Sequence[float], /
    ) -> None:
        """"""
        minima = [min(exc_s), min(why_s), min(zee_s)]
        maxima = [max(exc_s), max(why_s), max(zee_s)]
        if self.bbox is not None:
            minima = [min(_new, _old) for _new, _old in zip(minima, self.bbox[0])]
            maxima = [max(_new, _old) for _new, _old in zip(maxima, self.bbox[1])]
        self.bbox = (minima, maxima)

    @property
    def bbox_extent(self) -> Sequence[float]:
        """"""
        return tuple(_max - _min for _min, _max in zip(*self.bbox))

    @property
    def bbox_origin_and_corner(self) -> Tuple[Sequence[float], Sequence[float]]:
        """"""
        extent = self.bbox_extent
        output = tuple(
            (_min - _BBOX_AXES_MARGIN * _xtt, _max + _BBOX_AXES_MARGIN * _xtt)
            for _min, _max, _xtt in zip(self.bbox[0], self.bbox[1], extent)
        )

        return tuple(zip(*output))

    def Show(
        self,
        /,
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        """"""
        _UNSHOWN_FIGURES.remove(self)
        if in_main_thread:
            self.show().close()
        else:
            # Do not use "target=self.show().close"
            thread = process_t(target=lambda: self.show().close())
            thread.start()

    @staticmethod
    def ShowAll(
        *,
        interactively: bool = True,
        in_main_thread: bool = True,
    ) -> None:
        """"""
        while _UNSHOWN_FIGURES.__len__() > 1:
            _UNSHOWN_FIGURES[0].Show(interactively=interactively, in_main_thread=False)
        if _UNSHOWN_FIGURES.__len__() > 0:
            _UNSHOWN_FIGURES[0].Show(
                interactively=interactively, in_main_thread=in_main_thread
            )

    def Figure(self) -> figure_t:
        """"""
        return self
