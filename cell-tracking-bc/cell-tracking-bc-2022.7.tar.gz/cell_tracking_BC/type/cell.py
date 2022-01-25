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
from enum import Enum as enum_t
from typing import Any, Optional, Sequence, Tuple, Union

import numpy as nmpy
import scipy.ndimage.morphology as scph

from cell_tracking_BC.type.compartment import compartment_t
from cell_tracking_BC.type.cytoplasm import cytoplasm_t
from cell_tracking_BC.type.nucleus import nucleus_t


array_t = nmpy.ndarray
nucleus_or_nuclei_h = Union[nucleus_t, Tuple[nucleus_t, nucleus_t]]


@dcls.dataclass(repr=False, eq=False)
class state_t(enum_t):
    unknown = None
    pruned = -1
    living = 1
    dividing = 2
    dead = 0

    def IsActive(self) -> bool:
        """"""
        return self not in (state_t.dead, state_t.pruned)


@dcls.dataclass(repr=False, eq=False)
class cell_t(compartment_t):

    label: Any = None
    nucleus: Optional[nucleus_or_nuclei_h] = None
    cytoplasm: Optional[cytoplasm_t] = None
    # Inherited from compartment_t (among others): features
    state: state_t = state_t.unknown

    @classmethod
    def NewFromMap(cls, _: array_t, /, *, is_plain: bool = True) -> compartment_t:
        """"""
        raise RuntimeError(
            f"{cell_t.NewFromMap.__name__}: Not meant to be called from class {cell_t.__name__}; "
            f"Use {cell_t.NewFromMaps.__name__} instead"
        )

    @classmethod
    def NewFromMaps(
        cls,
        label: Any,
        /,
        *,
        cell_map: array_t = None,
        cytoplasm_map: array_t = None,
        nucleus_map: array_t = None,
    ) -> cell_t:
        """
        cell_map: Defined optional to follow cytoplasm and nucleus, but never None in fact
        """
        # TODO: make this implementation coherent with segmentation_t, and check the Map method. In particular, is it
        #       necessary to have nuclei and the associated management when the cytoplasm holes play this role already?
        #       Also, make clear in the doc that the 3 maps are supposed to be coherent since all the checks have been
        #       done in segmentation_t (at least should have been).
        cell = compartment_t.NewFromMap(cell_map)
        if cytoplasm_map is None:
            cytoplasm = None
        else:
            cytoplasm = cytoplasm_t.NewFromMap(cytoplasm_map, is_plain=False)
        if nucleus_map is None:
            nucleus = None
        else:
            nucleus = nucleus_t.NewFromMap(nucleus_map)

        instance = cls(
            label=label,
            nucleus=nucleus,
            cytoplasm=cytoplasm,
            centroid=cell.centroid,
            bb_slices=cell.bb_slices,
            touches_border=cell.touches_border,
            map_stream=cell.map_stream,
        )

        return instance

    def AddNucleus(self, nucleus_map: array_t, /) -> None:
        """
        For dividing cells
        """
        if self.nucleus is None:
            raise RuntimeError(f"Cannot add nucleus to a cell without a nucleus yet")

        nucleus = nucleus_t.NewFromMap(nucleus_map)
        self.nucleus = (self.nucleus, nucleus)

    @property
    def nuclei(self) -> Tuple[nucleus_t, ...]:
        """"""
        if self.nucleus is None:
            output = ()
        elif isinstance(self.nucleus, nucleus_t):
            output = (self.nucleus,)
        else:
            output = self.nucleus

        return output

    def Map(
        self,
        shape: Sequence[int],
        /,
        *,
        as_boolean: bool = False,
        with_labels: bool = False,
    ) -> array_t:
        """
        with_labels: cytoplasm will be marked with label 1, nuclei with subsequent labels
        """
        if as_boolean:
            dtype = nmpy.bool_
            one = True
        else:
            dtype = nmpy.uint8
            one = 1
        output = nmpy.zeros(shape, dtype=dtype)

        if self.cytoplasm is None:
            outer_compartment = self
        else:
            outer_compartment = self.cytoplasm
        nuclei = self.nuclei
        for c_idx, compartment in enumerate((outer_compartment, *nuclei), start=1):
            if compartment is self:
                map_ = super().Map(shape, as_boolean=True)
            else:
                map_ = compartment.Map(shape, as_boolean=True)
            if with_labels:
                output[map_] = c_idx
            else:
                output[map_] = one
        if nuclei.__len__() == 0:
            # TODO: this should not be necessary since the cell should represent the whole shape already
            output = scph.binary_fill_holes(output).astype(dtype, copy=False)

        return output

    def __str__(self) -> str:
        """"""
        super_str = super().__str__()

        lines = [super_str, "--- With compartments:"]
        initial_n_lines = lines.__len__()
        for compartment in (*self.nuclei, self.cytoplasm):
            if compartment is not None:
                lines.append(str(compartment))
        if lines.__len__() == initial_n_lines:
            return super_str

        return "\n".join(lines)
