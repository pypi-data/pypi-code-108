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

from typing import Sequence, Union

import numpy as nmpy
import plotext as pltx


array_t = nmpy.ndarray


def PlotHistogram(
    data: Union[array_t, Sequence[float]],
    /,
    *,
    n_bins: int = None,
    n_displayed_bins: int = 10,
    color: str = "blue",
    background_color: str = "black",
    axes_color: str = "green",
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
    width: int = 120,
    height: int = 20,
    should_use_numpy: bool = True,
    center_decimals: int = None,
) -> None:
    """"""
    if n_bins is None:
        n_bins = int(round(nmpy.sqrt(data.__len__())))

    pltx.clear_figure()

    if should_use_numpy:
        counts, edges = nmpy.histogram(data, bins=n_bins)

        centers = 0.5 * (edges[:-1] + edges[1:])
        if center_decimals is not None:
            centers = nmpy.around(centers, decimals=center_decimals)
            if center_decimals == 0:
                centers = centers.astype(nmpy.uint64)
        centers = tuple(str(_ctr) for _ctr in centers)

        pltx.bar(centers, counts.tolist(), color=color)
    else:
        n_displayed_bins = min(n_displayed_bins, n_bins)

        pltx.hist(data, n_bins, color=color)
        pltx.xfrequency(n_displayed_bins)

    pltx.canvas_color(background_color)
    pltx.axes_color(background_color)
    pltx.ticks_color(axes_color)

    if xlabel is not None:
        pltx.xlabel(xlabel)
    if ylabel is not None:
        pltx.ylabel(ylabel)
    if title is not None:
        pltx.title(title)

    terminal_width, _ = pltx.terminal_size()
    pltx.plot_size(min(width, terminal_width), height)

    pltx.show()
