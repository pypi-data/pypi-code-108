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

import dataclasses as dcls
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as nmpy
import scipy.ndimage as spim
import skimage.feature as ftre
import pca_b_stream as pcst
from PIL import Image as pil_image_t

from cell_tracking_BC.standard.uid import ShortID


array_t = nmpy.ndarray


@dcls.dataclass(repr=False, eq=False)
class compartment_t:

    centroid: array_t = None  # In frame coordinates
    bb_slices: Tuple[slice, slice] = None  # bb=bounding box; In frame coordinates
    touches_border: bool = None
    map_stream: Optional[bytes] = None  # Built from a numpy.bool_ array
    features: Dict[str, Any] = dcls.field(init=False, default_factory=dict)

    @classmethod
    def NewFromMap(cls, map_: array_t, /, *, is_plain: bool = True) -> compartment_t:
        """"""
        if is_plain:
            # By default, ftre.peak_local_max excludes peaks on the frame border. This can be parameterized otherwise,
            # but this would lead to an "off-center" peak anyway. Instead, the compartment map is padded.
            padded = nmpy.pad(map_, 1)
            distance_map = spim.distance_transform_edt(padded)
            centroid = ftre.peak_local_max(distance_map, num_peaks=1)[0] - 1
        else:
            pixels = nmpy.nonzero(map_)
            centroid_as_it = (
                nmpy.mean(pixels[_idx]) for _idx in range(pixels.__len__())
            )
            centroid = nmpy.fromiter(centroid_as_it, dtype=nmpy.float64)

        map_as_pil = pil_image_t.fromarray(map_)
        auto_crop_lengths = map_as_pil.getbbox()
        # auto_crop_lengths[2 and 3] already include the +1 for slices
        bb_slices = (
            slice(auto_crop_lengths[1], auto_crop_lengths[3]),
            slice(auto_crop_lengths[0], auto_crop_lengths[2]),
        )
        touches_border = (
            (auto_crop_lengths[0] == 0)
            or (auto_crop_lengths[1] == 0)
            or (auto_crop_lengths[2] == map_.shape[1])
            or (auto_crop_lengths[3] == map_.shape[0])
        )

        cropped = map_as_pil.crop(auto_crop_lengths)
        # TODO: Changing bool_ to int8 or uint8 breaks map generation (To be investigated one day)
        map_stream = pcst.PCA2BStream(nmpy.array(cropped, dtype=nmpy.bool_))

        instance = cls(
            centroid=centroid,
            bb_slices=bb_slices,
            touches_border=touches_border,
            map_stream=map_stream,
        )

        return instance

    def AddFeature(self, name: str, value: Any, /) -> None:
        """"""
        self.features[name] = value

    def AddFeaturesFromDictionary(self, features: Dict[str, Any], /) -> None:
        """"""
        self.features.update(features)

    @property
    def available_features(self) -> Sequence[str]:
        """"""
        return sorted(self.features.keys())

    def Map(self, shape: Sequence[int], /, *, as_boolean: bool = False) -> array_t:
        """"""
        if as_boolean:
            dtype = nmpy.bool_
            one = True
        else:
            dtype = nmpy.int8  # Do not use uint8 to allow map subtraction
            one = 1
        output = nmpy.zeros(shape, dtype=dtype)

        bb_map = self.BBMap()
        output[self.bb_slices][bb_map] = one

        return output

    def BBMap(self) -> array_t:
        """
        BB=Bounding box=Map limited to the compartment bounding box. Dtype: numpy.bool_
        """
        return pcst.BStream2PCA(self.map_stream)

    def NonZeroPixels(self, shape: Sequence[int], /) -> Tuple[array_t, array_t]:
        """"""
        return nmpy.nonzero(self.Map(shape))

    def __str__(self) -> str:
        """"""
        return (
            f"{self.__class__.__name__.upper()}.{ShortID(id(self))}:\n"
            f"    {self.centroid=}\n"
            f"    {self.bb_slices=}\n"
            f"    {self.map_stream=}\n"
            f"    {self.features=}"
        )
