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

from typing import Any, Callable, Optional, Sequence, Tuple, Union

import numpy as nmpy
import skimage.measure as msre
from cell_tracking_BC.type.cell import cell_t


array_t = nmpy.ndarray


SKIMAGE_MORPHOLOGICAL_FEATURES: Tuple[str]  # Set below
SKIMAGE_RADIOMETRIC_FEATURES: Tuple[str]  # Set below
SKIMAGE_ALL_FEATURES: Tuple[str]  # Set below


def NumpyArrayScalarFeatureInCell(
    cell: cell_t, frame: array_t, Feature: Callable[[array_t], array_t], /
) -> Union[int, float]:
    """
    Feature: the array_t returned value must be an array with a single value
    """
    output = NumpyArrayAnyFeatureInCell(cell, frame, Feature)

    return output.item()


def NumpyArrayAnyFeatureInCell(
    cell: cell_t, frame: array_t, Feature: Callable[[array_t], array_t], /
) -> array_t:
    """"""
    map_ = cell.Map(frame.shape, as_boolean=True)
    output = Feature(frame[map_])

    return output


def CellSKImageMorphologicalFeatures(cell: cell_t, /) -> Sequence[Any]:
    """"""
    return _CellSKImageFeatures(cell, None, SKIMAGE_MORPHOLOGICAL_FEATURES)


def CellSKImageAllFeatures(cell: cell_t, frame: array_t, /) -> Sequence[Any]:
    """"""
    return _CellSKImageFeatures(
        cell, frame, SKIMAGE_MORPHOLOGICAL_FEATURES + SKIMAGE_RADIOMETRIC_FEATURES
    )


def _CellSKImageFeatures(
    cell: cell_t, frame: Optional[array_t], names: Sequence[str], /
) -> Sequence[Any]:
    """"""
    output = []

    if frame is None:
        # /!\ Because the bounding box map is used (as opposed to the full, frame-shaped map), features such as the
        # centroid are relative to the cell bounding box. However, features related to absolute positioning are usually
        # not used for clustering or classification.
        bb_map = cell.BBMap().astype(nmpy.int8)
        features = msre.regionprops(bb_map)[0]
    else:
        cell_map = cell.Map(frame.shape)
        features = msre.regionprops(cell_map, intensity_image=frame)[0]
    for name in names:
        output.append(features[name])

    return output


def CellArea(cell: cell_t, /) -> int:
    """"""
    bb_map = cell.BBMap()
    output = nmpy.count_nonzero(bb_map)

    return output


def IntensityEntropyInCell(
    cell: cell_t,
    frame: array_t,
    /,
    *,
    min_intensity: float = 0.0,
    max_intensity: float = 255.0,
    n_bins: int = None,
    normalized_version: bool = True,
) -> float:
    """
    normalized_version: It True, the entropy is normalized by 1/log(n_bins) so that the output belongs to [0,1]
    """
    map_ = cell.Map(frame.shape, as_boolean=True)
    intensities = frame[map_]

    if n_bins is None:
        n_bins = max(3, int(round(nmpy.sqrt(intensities.size))))
    histogram, _ = nmpy.histogram(
        intensities, range=(min_intensity, max_intensity), bins=n_bins
    )
    normed = histogram / nmpy.sum(histogram)
    non_zero = normed[normed > 0.0]

    output = -nmpy.sum(non_zero * nmpy.log(non_zero))
    if normalized_version:
        output /= nmpy.log(n_bins)

    return output.item()


def _CellSKImageMorphologicalFeatureNames() -> Tuple[str]:
    """"""
    return _CellSKImageFeatureNames(False)


def _CellSKImageAllFeatureNames() -> Tuple[str]:
    """"""
    return _CellSKImageFeatureNames(True)


def _CellSKImageFeatureNames(with_radiometry: bool, /) -> Tuple[str]:
    """"""
    output = []

    dummy = nmpy.zeros((10, 10), dtype=nmpy.int8)
    dummy[4:7, 4:7] = 1
    if with_radiometry:
        features = msre.regionprops(dummy, intensity_image=dummy)[0]
    else:
        features = msre.regionprops(dummy)[0]

    for name in dir(features):
        if (not name.startswith("_")) and hasattr(features, name):
            output.append(name)

    return tuple(output)


SKIMAGE_MORPHOLOGICAL_FEATURES = _CellSKImageMorphologicalFeatureNames()
SKIMAGE_RADIOMETRIC_FEATURES = tuple(
    set(_CellSKImageAllFeatureNames()).difference(SKIMAGE_MORPHOLOGICAL_FEATURES)
)
# Keep this sum instead of _CellSKImageAllFeatureNames() to guaranty the correct order
SKIMAGE_ALL_FEATURES = SKIMAGE_MORPHOLOGICAL_FEATURES + SKIMAGE_RADIOMETRIC_FEATURES
