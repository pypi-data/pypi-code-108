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

from typing import Any, Dict
from typing import Protocol, Sequence

# Can import everything
from cell_tracking_BC.in_out.graphics.type.axes import axes_2d_t, axes_t
from cell_tracking_BC.in_out.graphics.type.event import event_h, event_key_h, event_scroll_h
from cell_tracking_BC.in_out.graphics.type.figure import figure_t
from cell_tracking_BC.in_out.graphics.type.widget import element_h, slider_h


class signatures_p(Protocol):
    @staticmethod
    def cell_annotation_style_h(
        highlighted: bool, multi_track: bool, /
    ) -> Dict[str, Any]:
        ...

    @staticmethod
    def new_slider_h(figure: figure_t, n_steps: int, /) -> slider_h:
        ...

    @staticmethod
    def slider_value_h(slider: slider_h, /) -> float:
        ...

    @staticmethod
    def update_slider_h(slider: slider_h, value: float, /) -> None:
        ...

    @staticmethod
    def slider_bounds_h(slider: slider_h, /) -> Sequence[float]:
        ...

    @staticmethod
    def slider_axes_h(slider: slider_h, /) -> axes_2d_t:
        ...

    @staticmethod
    def get_visibility_h(what: element_h, /) -> bool:
        ...

    @staticmethod
    def set_visibility_h(what: element_h, visibility: bool, /) -> None:
        ...

    @staticmethod
    def is_target_of_event_h(axes: axes_t, event: event_h, /) -> bool:
        ...

    @staticmethod
    def key_event_key_h(event: event_key_h, /) -> str:
        ...

    @staticmethod
    def scroll_event_step_h(event: event_scroll_h, /) -> float:
        ...
