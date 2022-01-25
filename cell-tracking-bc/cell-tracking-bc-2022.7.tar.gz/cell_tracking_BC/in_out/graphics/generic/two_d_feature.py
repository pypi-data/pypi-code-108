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

# from __future__ import annotations
#
# import dataclasses as dtcl
# import warnings as wrng
# from sys import maxsize as MAX_INTEGER
# from typing import Dict, List, Optional, Sequence, Tuple, cast, Union
#
# import networkx as grph
# import numpy as nmpy
#
# from cell_tracking_BC.in_out.file.archiver import archiver_t
# from cell_tracking_BC.in_out.graphics.context import axes_2d_t as axes_t
# from cell_tracking_BC.in_out.graphics.context import (
#     context_t,
#     annotation_h,
#     event_h,
#     figure_t,
# )
# from cell_tracking_BC.in_out.graphics.generic.tree_layout import (
#     VersionOfForkingForLayout,
# )
# from cell_tracking_BC.type.track import forking_track_t, single_track_t
#
#
# array_t = nmpy.ndarray
#
#
# @dtcl.dataclass(repr=False, eq=False)
# class f_viewer_2d_t:
#
#     figure: figure_t
#     axes_track: axes_t
#
#     annotation: annotation_h = dtcl.field(init=False, default=None)
#
#     features: Sequence[str] = dtcl.field(init=False, default=None)
#     values: Sequence[Dict[int,array_t]] = dtcl.field(init=False, default=None)
#
#     dbe: context_t = None
#
#     @classmethod
#     def NewForFeature(
#         cls,
#         feature: Union[str, Sequence[str]],
#         values: Union[Dict[int,array_t], Sequence[Dict[int,array_t]]],
#         dbe: context_t,
#         /,
#         *,
#         figure_name: str = "feature",
#         archiver: archiver_t = None,
#     ) -> f_viewer_2d_t:
#         """
#         Annotation-on-hover code adapted from:
#         https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-in-matplotlib
#         Answered by ImportanceOfBeingErnest on Nov 7 '17 at 20:23
#         Edited by waterproof on Aug 12 '19 at 20:08
#         """
#         figure, axes_track = dbe.figure_2d_t.NewFigureAndAxes()
#         axes_track = cast(axes_t, axes_track)
#
#         if isinstance(feature, str):
#             features = (feature,)
#             values = (values,)
#         else:
#             features = feature
#
#         max_label = max(values[0].keys())
#         axes_track.SetAxesPropertiesForTracking(
#             range(1, max_label+1, max(1,int(round(max_label / 10))))
#         )
#
#         instance = cls(
#             figure=figure,
#             axes_track=axes_track,
#             dbe=dbe,
#         )
#
#         rectangles = []
#         div_values = []
#         dea_values = []
#         for (label, division_response), death_response in zip(
#             cell_division_response[feature].items(), cell_death_response[feature].values()
#         ):
#             if division_response is None:
#                 continue
#
#             division_time_points = cell_division_frame_idc[feature][label]
#             death_frame_idx = cell_death_frame_idc[feature][label]
#
#             for t_idx, (div_value, dea_value) in enumerate(
#                 zip(division_response, death_response)
#             ):
#                 dividing = t_idx in division_time_points
#                 dying = t_idx == death_frame_idx
#                 rectangle = (
#                     rectangle_t((t_idx, label - 0.5), 1.0, 1.0, edgecolor="none"),
#                     (div_value, dea_value, dividing, dying),
#                 )
#                 rectangles.append(rectangle)
#             div_values.extend(division_response)
#             dea_values.extend(death_response)
#
#         if rectangles.__len__() > 0:
#             min_div_value = min(div_values)
#             max_div_value = max(div_values)
#             div_scaling = 1.0 / (max_div_value - min_div_value)
#             min_dea_value = min(dea_values)
#             max_dea_value = max(dea_values)
#             dea_scaling = 1.0 / (max_dea_value - min_dea_value)
#             events = []
#             for rectangle, (div_value, dea_value, dividing, dying) in rectangles:
#                 div = div_scaling * (div_value - min_div_value)
#                 dea = dea_scaling * (dea_value - min_dea_value)
#                 div_color = nmpy.array((1.0 - div, 1.0 - div, 1.0))
#                 dea_color = nmpy.array((1.0, 1.0 - dea, 1.0 - dea))
#                 color = nmpy.minimum(div_color, dea_color)
#                 rectangle.set_facecolor(color)
#                 if dividing or dying:
#                     where = tuple(_crd + 0.5 for _crd in rectangle.get_xy())
#                     if dividing:
#                         events.append(("3", 60, where))
#                     if dying:
#                         events.append(("x", 30, where))
#             figure, axes = pypl.subplots()
#             for rectangle, _ in rectangles:
#                 axes.add_artist(rectangle)
#             for what, size, where in events:
#                 axes.scatter(*where, c="k", marker=what, s=size)
#             max_label = max(cell_division_response[feature].keys())
#             axes.set_xlim((0, sequence.length))
#             axes.set_ylim((0,max_label + 1))
#             positions = range(1, max_label+1, max(1,int(round(max_label / 10))))
#             axes.yaxis.set_ticks(positions)
#             axes.yaxis.set_ticklabels(positions)
#             n_shades = 8
#             shades = nmpy.linspace(0.0, 1.0, num=n_shades)
#             div_legend = [
#                 rectangle_t(
#                     (0, 0),
#                     3.0,
#                     5.0,
#                     edgecolor="none",
#                     facecolor=(1.0 - _shd, 1.0 - _shd, 1.0),
#                 )
#                 for _shd in shades
#             ]
#             dea_legend = [
#                 rectangle_t(
#                     (0, 0),
#                     3.0,
#                     5.0,
#                     edgecolor="none",
#                     facecolor=(1.0, 1.0 - _shd, 1.0 - _shd),
#                 )
#                 for _shd in shades
#             ]
#             axes.legend(
#                 handles=(div_legend, dea_legend),
#                 labels=("Division Score", "Death Score"),
#                 loc="right",
#                 bbox_to_anchor=(1.3, 0.5),
#                 handler_map={list: tuple_handler_t(ndivide=None, pad=0)},
#             )
#
#         instance.features = features
#         instance.values = values
#
#         # figure.ActivateEvent("button_press_event", instance._OnButtonPress)
#
#         figure.ActivateTightLayout(h_pad=0.05)
#         figure.Archive(name=figure_name, archiver=archiver)
#
#         return instance
#
#     def _PlotSingleTrackEdges(
#         self,
#         track: single_track_t,
#         all_cell_heights: List[int],
#         is_valid: bool,
#         /,
#     ) -> Sequence[Tuple[float, int]]:
#         """"""
#         length, time_points, label, where = self._ElementsForTrackPieces(track)
#
#         self.labels.insert(where, track.root.label)
#         self.time_points.insert(where, track.root_time_point)
#         self.affinities.insert(where, 0.0)
#         self.colors.insert(where, self.colormap(0.0))
#
#         heights = (length + 1) * (label,)
#         all_cell_heights.extend(heights)
#
#         if is_valid:
#             color = "gray"
#         else:
#             color = "red"
#         self.axes_track.PlotLines(time_points, heights, color=color, zorder=1)
#
#         return ((label, label),)
#
#     def _PlotForkingTrackEdges(
#         self,
#         track: forking_track_t,
#         all_cell_heights: List[int],
#         is_valid: bool,
#         /,
#     ) -> Sequence[Tuple[float, int]]:
#         """"""
#         with_int_labels, integer_to_cell = VersionOfForkingForLayout(track)
#         try:
#             int_layout = grph.nx_agraph.pygraphviz_layout(with_int_labels, prog="dot")
#         except Exception as exc:
#             wrng.warn(f"Track layout failed for {track} with error:\n{exc}")
#             return ()
#         positions = {
#             integer_to_cell[_idx]: _pst
#             for _idx, _pst in int_layout.items()
#             if isinstance(_idx, int)
#         }
#
#         output = []
#
#         all_time_points, all_heights = [], []
#         min_height = max_height = positions[track.root][0]
#         min_label = MAX_INTEGER
#         root_height = None
#         where = None
#         for piece in track.Pieces():
#             _, time_points, label, new_where = self._ElementsForTrackPieces(piece)
#             heights = nmpy.fromiter(
#                 (positions[_cll][0] for _cll in piece), dtype=nmpy.float64
#             )
#             if piece[0] is track.root:
#                 root_height = heights[0]
#             if where is None:
#                 where = new_where
#
#             all_time_points.append(time_points)
#             all_heights.append(heights)
#             min_height = min(min_height, min(heights))
#             max_height = max(max_height, max(heights))
#             if label is not None:
#                 if label < min_label:
#                     min_label = label
#                 output.append((heights[-1], label))
#
#         height_scaling = (track.n_leaves - 1) / (max_height - min_height)
#         AdjustedHeight = lambda _hgt: height_scaling * (_hgt - min_height) + min_label
#
#         output = tuple((AdjustedHeight(_elm[0]), _elm[1]) for _elm in sorted(output))
#
#         if is_valid:
#             color = "gray"
#         else:
#             color = "red"
#         for time_points, heights in zip(all_time_points, all_heights):
#             heights = AdjustedHeight(heights)
#             self.axes_track.PlotLines(time_points, heights, color=color, zorder=1)
#             all_cell_heights.extend(heights[1:])
#         root_height = AdjustedHeight(root_height)
#
#         self.labels.insert(where, track.root.label)
#         self.time_points.insert(where, track.root_time_point)
#         self.affinities.insert(where, 0.0)
#         self.colors.insert(where, self.colormap(0.0))
#
#         all_cell_heights.insert(where, root_height)
#
#         return output
#
#     def _ElementsForTrackPieces(
#         self,
#         track: single_track_t,
#         /,
#     ) -> Tuple[int, Sequence[int], Optional[int], int]:
#         """"""
#         where = self.labels.__len__()
#
#         label = track.label
#         root_time_point = track.root_time_point
#         length = track.length
#         time_points = tuple(range(root_time_point, root_time_point + length + 1))
#         affinities = track.affinities
#
#         self.labels.extend(_cll.label for _cll in track[1:])
#         self.time_points.extend(time_points[1:])
#         self.affinities.extend(affinities)
#         self.colors.extend(self.colormap(affinities))
#
#         return length, time_points, label, where
#
#     def _ShowAnnotation(
#         self,
#         event: event_h,
#         /,
#     ) -> None:
#         """"""
#         raise NotImplementedError
#
#     def _OnButtonPress(
#         self,
#         event: event_h,
#         /,
#     ) -> None:
#         """"""
#         if self.dbe.IsTargetOfEvent(self.axes_track, event):
#             self._ShowAnnotation(event)
#         elif self.dbe.IsTargetOfEvent(self.viewer.axes, event):
#             pass
#         elif self.dbe.IsVisible(self.annotation):
#             self.dbe.SetVisibility(self.annotation, False)
#             self.figure.Update()
#
#     def Show(
#         self,
#         /,
#         *,
#         interactively: bool = True,
#         in_main_thread: bool = True,
#     ) -> None:
#         """"""
#         self.figure.Show(interactively=interactively, in_main_thread=in_main_thread)
