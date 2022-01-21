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

import warnings as wrng
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as nmpy
import skimage.morphology as mrph

from cell_tracking_BC.standard.uid import ShortID
from cell_tracking_BC.type.cell import cell_t
from cell_tracking_BC.type.segmentation import segmentation_t


array_t = nmpy.ndarray
inner_outer_associations_h = Dict[int, Union[int, Tuple[int, int]]]


class frame_t(array_t):
    """
    A Frame is one plane, or channel, of a (potentially multi-channel) image
    """

    def __new__(cls, array: array_t, /) -> frame_t:
        """"""
        if (n_dims := array.ndim) != 2:
            raise ValueError(
                f"{n_dims}: Invalid number of dimensions of frame with shape {array.shape}; "
                f"Expected=2=ROWSxCOLUMNS"
            )

        instance = nmpy.asarray(array).view(cls)
        instance.path = None
        instance.cells = []
        instance.runtime = {}

        return instance

    def __array_finalize__(self, array: Optional[array_t], /) -> None:
        """"""
        if array is None:
            return
        self.path = getattr(array, "path", None)
        self.cells = getattr(array, "cells", None)

    def ApplyTransform(self, Transform: transform_h, /, **kwargs) -> None:
        """"""
        transformed = Transform(self, **kwargs)
        self[...] = transformed[...]

    def AddCellsFromSegmentation(
        self,
        segmentation: segmentation_t,
    ) -> None:
        """
        Segmentation are supposed to be binary (as opposed to already labeled)
        """
        # --- Generic inner and outer segmentation list for all options
        non_nones, parameters = segmentation.NonNoneAsList()

        # --- Segmentation labeling and (if needed) inner-outer label associations
        labeleds = []
        n_objects_per_sgm = []
        for non_none in non_nones:
            labeled, n_objects = mrph.label(non_none, return_num=True, connectivity=1)
            labeleds.append(labeled)
            n_objects_per_sgm.append(n_objects)
        if labeleds.__len__() > 1:
            inner_label_of_outer = _InnerOuterAssociations(labeleds, n_objects_per_sgm)
            _CheckInnerOuterAssociations(inner_label_of_outer, n_objects_per_sgm)
        else:
            inner_label_of_outer = None

        # --- Cell creation and addition
        for outer_label in range(1, n_objects_per_sgm[-1] + 1):
            if inner_label_of_outer is None:
                labels = (outer_label,)
            else:
                labels = (inner_label_of_outer[outer_label], outer_label)
            kwargs = {}
            additional_nucleus = None
            for parameter, labeled, label in zip(parameters, labeleds, labels):
                label: Union[int, Tuple[int, int]]
                if isinstance(label, int):
                    kwargs[parameter] = labeled == label
                else:
                    kwargs[parameter] = labeled == label[0]
                    additional_nucleus = label[1]
            cell = cell_t.NewFromMaps(labels[-1], **kwargs)
            if additional_nucleus is not None:
                cell.AddNucleus(labeleds[0] == additional_nucleus)
            self.cells.append(cell)

    def __str__(self) -> str:
        """"""
        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.path=}\n"
            f"    {self.shape=}\n"
            f"    {self.cells.__len__()=}"
        )


transform_h = Callable[[frame_t, Dict[str, Any]], array_t]


def _InnerOuterAssociations(
    segmentations: List[array_t], n_objects_per_sgm: Sequence[int], /
) -> inner_outer_associations_h:
    """"""
    output = {}

    for inner_label in range(1, n_objects_per_sgm[0] + 1):
        dilated = mrph.dilation(segmentations[0] == inner_label)
        outer_label = nmpy.amax(segmentations[1][dilated])
        if outer_label in output:
            output[outer_label] = (
                output[outer_label],
                inner_label,
            )
            if output[outer_label].__len__() > 2:
                raise RuntimeError("Cell with more than 2 nuclei")
        else:
            output[outer_label] = inner_label

    return output


def _CheckInnerOuterAssociations(
    inner_label_of_outer: inner_outer_associations_h,
    n_objects_per_sgm: Sequence[int],
    /,
) -> None:
    """"""
    if n_objects_per_sgm[0] != n_objects_per_sgm[1]:
        wrng.warn(
            f"Mismatch in number of segmented objects: {n_objects_per_sgm}; "
            f"Might be due to cell divisions"
        )

    inner_labels = []
    for label in inner_label_of_outer.values():
        if isinstance(label, int):
            inner_labels.append(label)
        else:
            inner_labels.extend(label)
    outer_labels = tuple(inner_label_of_outer.keys())
    n_inner_labels = nmpy.unique(inner_labels).size
    n_outer_labels = nmpy.unique(outer_labels).size
    if (n_missing_associations := n_objects_per_sgm[0] - n_inner_labels) > 0:
        wrng.warn(
            f"{n_missing_associations} inner comportment(s) not associated with outer compartments"
        )
    if (n_missing_associations := n_objects_per_sgm[1] - n_outer_labels) > 0:
        wrng.warn(
            f"{n_missing_associations} outer comportment(s) without inner compartment(s)"
        )
