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

from typing import NamedTuple as named_tuple_t
from typing import Type, TypeVar

# Can import everything but drawers and viewers
from cell_tracking_BC.in_out.graphics.type.axes import axes_2d_t, axes_3d_t
from cell_tracking_BC.in_out.graphics.type.figure import figure_t
from cell_tracking_BC.in_out.graphics.type.signatures import signatures_p


path_collection_h = TypeVar("path_collection_h")
# Do not import *_t (=> circular imports)
s_drawer_2d_h = TypeVar("s_drawer_2d_h")
s_viewer_2d_h = TypeVar("s_viewer_2d_h")
t_viewer_2d_h = TypeVar("t_viewer_2d_h")


class context_t(named_tuple_t):
    figure_2d_t: Type[figure_t] = None
    figure_3d_t: Type[figure_t] = None
    axes_2d_t: Type[axes_2d_t] = None
    axes_3d_t: Type[axes_3d_t] = None
    s_drawer_2d_t: Type[s_drawer_2d_h] = None
    s_viewer_2d_t: Type[s_viewer_2d_h] = None
    t_viewer_2d_t: Type[t_viewer_2d_h] = None
    #
    CellAnnotationStyle: signatures_p.cell_annotation_style_h = lambda: {}
    #
    NewSlider: signatures_p.new_slider_h = None
    SliderValue: signatures_p.slider_value_h = None
    UpdateSlider: signatures_p.update_slider_h = None
    SliderBounds: signatures_p.slider_bounds_h = None
    SliderAxes: signatures_p.slider_axes_h = lambda: None
    #
    IsVisible: signatures_p.get_visibility_h = None
    SetVisibility: signatures_p.set_visibility_h = None
    #
    IsTargetOfEvent: signatures_p.is_target_of_event_h = lambda: True
    KeyEventKey: signatures_p.key_event_key_h = None
    ScrollEventStep: signatures_p.scroll_event_step_h = None
