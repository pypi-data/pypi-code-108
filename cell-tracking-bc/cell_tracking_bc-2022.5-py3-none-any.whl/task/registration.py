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

from typing import Sequence, Tuple

import numpy as nmpy
import scipy.ndimage as imge
import skimage.morphology as mrph
import skimage.transform as trsf


array_t = nmpy.ndarray


def InCommonNonZeroRectangles(
    reference: array_t,
    changed: array_t,
    /,
    *,
    as_squares: bool = False,
    for_rotation: bool = False,
    ensure_odd_sides: bool = False,
) -> Tuple[Sequence[array_t], Sequence[Sequence[int]]]:
    """"""
    rectangles = []
    corners = []

    tight_rectangles = []
    tight_shapes = []
    for image in (reference, changed):
        where = imge.find_objects(image > 0, max_label=1)[0]
        rectangle = image[where].copy()
        shape = nmpy.array(rectangle.shape)

        corners.append([_slc.start for _slc in where])
        tight_rectangles.append(rectangle)
        tight_shapes.append(shape)

    common_shape = nmpy.maximum(*tight_shapes)
    if for_rotation:
        side = int(nmpy.around(2.0 * nmpy.sqrt(nmpy.sum((0.5 * common_shape) ** 2))))
        common_shape = (side, side)
    elif as_squares:
        side = max(common_shape)
        common_shape = (side, side)
    if ensure_odd_sides:
        common_shape += 1 - (common_shape % 2)
    common_shape = nmpy.array(common_shape)

    for corner, shape, rectangle in zip(corners, tight_shapes, tight_rectangles):
        if nmpy.any(shape < common_shape):
            common_rectangle = nmpy.zeros(common_shape, dtype=rectangle.dtype)
            differences = (common_shape - shape) // 2
            common_rectangle[
                differences[0] : (differences[0] + shape[0]),
                differences[1] : (differences[1] + shape[1]),
            ] = rectangle
            rectangles.append(common_rectangle)
            for c_idx in range(2):
                corner[c_idx] -= differences[c_idx]
        else:
            rectangles.append(rectangle)

    return rectangles, corners


def RotationInBinary(reference: array_t, rotated: array_t, /) -> float:
    """"""
    output = 0.0

    distance_map = imge.distance_transform_edt(reference)
    highest_distance = 0.0
    for angle in nmpy.linspace(-20.0, 20.0, num=11):
        attempt = trsf.rotate(rotated, angle, preserve_range=True)
        distance = nmpy.sum(distance_map * attempt)
        if distance > highest_distance:
            highest_distance = distance
            output = angle

    return output


def RotatedLabeled(labeled: array_t, angle: float, /) -> array_t:
    """"""
    output = nmpy.zeros_like(labeled)

    rotated = trsf.rotate(labeled, angle, preserve_range=True)
    n_labels = nmpy.amax(labeled)
    for label in range(1, n_labels + 1):
        where = nmpy.logical_and(rotated >= label - 0.5, rotated < label + 0.5)
        sublabeled, n_sublabels = mrph.label(where, return_num=True, connectivity=1)

        highest_area = 0
        best_sublabel = None
        for sublabel in range(1, n_sublabels + 1):
            area = nmpy.count_nonzero(sublabeled == sublabel)
            if area > highest_area:
                highest_area = area
                best_sublabel = sublabel
        output[sublabeled == best_sublabel] = label

    return output
