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

import dataclasses as dtcl
from typing import Any, Optional, Sequence, Tuple, TypeVar, Union

import numpy as nmpy
import skimage.measure as msre

# Caution to avoid circular imports
import cell_tracking_BC.standard.uid as uqid
from cell_tracking_BC.in_out.graphics.type.annotation import (
    annotation_h,
    cell_annotation_h,
)
from cell_tracking_BC.in_out.graphics.type.color import colormap_h
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.frame import frame_t
from cell_tracking_BC.type.tracks import tracks_t


# 2 lines below: Avoid circular imports
cell_annotation_style_h = TypeVar("cell_annotation_style_h")
figure_h = TypeVar("figure_h")
#
array_t = nmpy.ndarray


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_t:
    def SetTitle(self, title: str, /) -> None:
        pass

    def SetAxisTicks(
        self,
        which: Union[str, Any],
        positions: Sequence[float],
        labels: Sequence[str],
        /,
    ) -> None:
        pass

    def SetTimeAxisProperties(self, latest: int, /) -> None:
        pass

    def TurnTicksOff(self) -> None:
        pass

    def PlotLines(
        self, xs, ys, *args, zdir="z", scalex=True, scaley=True, data=None, **kwargs
    ):
        pass

    def PlotCellAnnotation(
        self, position: Sequence[float], text: cell_annotation_h, /, **kwargs
    ) -> Union[annotation_h, Sequence[annotation_h]]:
        pass

    def PlotCellsDetails(
        self,
        frame: Union[array_t, frame_t],
        cell_contours: Optional[Sequence[array_t]],
        with_cell_labels: bool,
        cell_frame: Optional[frame_t],
        tracks: Optional[tracks_t],
        AnnotationStyle: cell_annotation_style_h,
        /,
        *,
        highlighted: int = -1,
        elevation: float = None,
        with_alpha_cell_uids: bool = True,
    ) -> Sequence[Tuple[int, Union[annotation_h, Sequence[annotation_h]]]]:
        """"""
        output = []

        if with_cell_labels or (tracks is not None):
            if elevation is None:
                self.RemoveLinesAndAnnotations()

            if cell_frame is None:
                labeled = msre.label(frame, connectivity=1)
                cells = msre.regionprops(labeled)
            else:
                cells = cell_frame.cells
            assert hasattr(cells[0], "centroid") and hasattr(
                cells[0], "label"
            ), "Please contact developer about API change"

            for cell in cells:
                if elevation is None:
                    position = nmpy.flipud(cell.centroid)
                else:
                    position = (*cell.centroid, elevation)

                text = []
                if with_cell_labels:
                    text.append(uqid.AlphaColumnFromLabel(cell.label))
                else:
                    text.append("")
                if (tracks is None) or not isinstance(cell, cell_t):
                    text.append("")
                else:
                    labels = tracks.TrackLabelsContainingCell(cell, tolerant_mode=True)
                    if labels is None:
                        text.append("?")
                    else:
                        if labels.__len__() > 1:
                            labels = "\n".join(str(_lbl) for _lbl in labels)
                        else:
                            labels = str(labels[0])
                        text.append(labels)

                if with_alpha_cell_uids:
                    text = "".join(text)
                    additionals = AnnotationStyle(
                        cell.label == highlighted, "\n" in text
                    )
                else:
                    if text[0].__len__() > 0:
                        multi_text = [(text[0], {})]
                    else:
                        multi_text = []
                    if text[1].__len__() > 0:
                        multi_text.extend(
                            (_pce, {"rotation": -90.0}) for _pce in text[1].split("\n")
                        )
                    text = multi_text
                    additionals = AnnotationStyle(cell.label == highlighted, False)

                annotation = self.PlotCellAnnotation(position, text, **additionals)

                output.append((cell.label, annotation))

        # Leave this block after cell annotation since, if placed before, the (new) contours are considered as previous
        # artists and removed.
        if cell_contours is not None:
            if elevation is None:
                for contour in cell_contours:
                    self.PlotLines(
                        contour[:, 1],
                        contour[:, 0],
                        linestyle=":",
                        color=(0.0, 1.0, 1.0, 0.3),
                    )
            else:
                for contour in cell_contours:
                    heights = contour.shape[0] * [elevation]
                    self.PlotLines(
                        contour[:, 0],
                        contour[:, 1],
                        heights,
                        linestyle=":",
                        color=(0.0, 1.0, 1.0, 0.3),
                    )

        return output

    def ShowLegend(self) -> None:
        pass

    def AddStandardColormap(
        self, name: str, colormap: str, /, *, position: str = "right"
    ) -> colormap_h:
        pass

    def AddColormapFromMilestones(
        self,
        name: str,
        milestones: Sequence[Tuple[float, str]],
        /,
        *,
        position: str = "right",
    ) -> colormap_h:
        pass

    def Freeze(self) -> None:
        pass

    def RemoveLinesAndAnnotations(self) -> None:
        pass

    def Figure(self) -> figure_h:
        pass


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_2d_t(axes_t):
    def SetTrackingAxesProperties(self, tick_positions: Sequence[float], /) -> None:
        pass

    def PlotPoints(
        self,
        x,
        y,
        s=None,
        c=None,
        marker=None,
        cmap=None,
        norm=None,
        vmin=None,
        vmax=None,
        alpha=None,
        linewidths=None,
        *,
        edgecolors=None,
        plotnonfinite=False,
        data=None,
        **kwargs,
    ):
        pass

    def PlotImage(
        self, image: array_t, /, *, interval: Tuple[float, float] = None
    ) -> None:
        """"""
        pass

    def UpdateImage(
        self,
        picture: array_t,
        /,
        *,
        interval: Tuple[float, float] = None,
        should_update_limits: bool = False,
    ) -> None:
        """"""
        pass

    def PlotText(self, x, y, s, fontdict=None, **kwargs):
        pass

    def PlotAnnotation(self, text, xy, *args, **kwargs):
        pass


@dtcl.dataclass(init=False, repr=False, eq=False)
class axes_3d_t(axes_t):
    @staticmethod
    def TimeScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        return 1.0

    @staticmethod
    def MillefeuilleScaling(shape: Sequence[int], length: int, /) -> float:
        """"""
        return 1.0

    def PlotPoints(
        self, xs, ys, zs=0, zdir="z", s=20, c=None, depthshade=True, *args, **kwargs
    ):
        pass

    def PlotIsosurface(
        self,
        volume: array_t,
        iso_value: float,
        /,
        should_be_capped: bool = False,
        keep_every: int = 2,
        **kwargs,
    ) -> None:
        pass

    def PlotImageInZ(
        self,
        image: array_t,
        all_rows: array_t,
        all_cols: array_t,
        n_levels: int,
        height: float,
        z_scaling: float,
        /,
        min_intensity: float = 0.0,
        intensity_range: float = 1.0,
        alpha: float = 0.8,
        **kwargs,
    ) -> None:
        pass

    def PlotText(self, x, y, z, s, zdir=None, **kwargs):
        pass

    def PlotAnnotation(self, text, xyz, *args, **kwargs):
        pass
