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

import dataclasses as dtcl
from typing import Any, Dict, List, Sequence, Tuple

import numpy as nmpy
import skimage.morphology as mrph

import cell_tracking_BC.in_out.text.progress as prgs
from cell_tracking_BC.type.segmentation import (
    CellIssues_h,
    compartment_t,
    segmentation_t,
    version_id_h,
)


array_t = nmpy.ndarray


@dtcl.dataclass(repr=False, eq=False)
class segmentations_t(List[segmentation_t]):
    @classmethod
    def NewFromCompartmentSequences(
        cls,
        expected_length: int,
        /,
        *,
        cells_sgms: Sequence[array_t] = None,
        cytoplasms_sgms: Sequence[array_t] = None,
        nuclei_sgms: Sequence[array_t] = None,
    ) -> segmentations_t:
        """
        Valid options: see cell_tracking_BC.type.segmentation.segmentation_t.NewFromCompartments
        """
        instance = cls()

        fake_sequence = expected_length * [None]
        if cells_sgms is None:
            cells_sgms = fake_sequence
        if cytoplasms_sgms is None:
            cytoplasms_sgms = fake_sequence
        if nuclei_sgms is None:
            nuclei_sgms = fake_sequence
        all_sequences = (cells_sgms, cytoplasms_sgms, nuclei_sgms)
        if any(_sqc.__len__() != expected_length for _sqc in all_sequences):
            raise ValueError(
                f"Non-none sequences do not all have expected length {expected_length}"
            )

        for cell, cytoplasm, nucleus in zip(*all_sequences):
            segmentation = segmentation_t.NewFromCompartments(
                cell=cell, cytoplasm=cytoplasm, nucleus=nucleus
            )
            instance.append(segmentation)

        return instance

    @classmethod
    def NewFromDicts(cls, dictionaries: Sequence[Dict[str, Any]]) -> segmentations_t:
        """"""
        instance = cls()

        for dictionary in dictionaries:
            segmentation = segmentation_t.NewFromDict(dictionary)
            instance.append(segmentation)

        return instance

    @property
    def available_versions(
        self,
    ) -> Tuple[Tuple[compartment_t, ...], Sequence[version_id_h]]:
        """
        See cell_tracking_BC.type.segmentation.available_versions
        """
        return self[0].available_versions

    def CompartmentsWithVersion(
        self, compartment: compartment_t, /, *, index: int = None, name: str = None
    ) -> Sequence[array_t]:
        """
        index: see cell_tracking_BC.type.segmentation.CompartmentWithVersion
        """
        output = []

        for segmentation in self:
            version = segmentation.CompartmentWithVersion(
                compartment, index=index, name=name
            )
            output.append(version)

        return output

    @property
    def cell_areas(self) -> Sequence[int]:
        """"""
        output = []

        for segmentation in self:
            labeled, n_cells = mrph.label(
                segmentation.cell, return_num=True, connectivity=1
            )
            areas = (
                nmpy.count_nonzero(labeled == _lbl) for _lbl in range(1, n_cells + 1)
            )
            output.extend(areas)

        return output

    def CellAreaHistogram(
        self,
        /,
        *,
        n_bins: int = None,
        should_return_centers: bool = False,
        should_round_centers: bool = True,
    ) -> Tuple[array_t, array_t]:
        """"""
        areas = self.cell_areas

        if n_bins is None:
            n_bins = int(round(nmpy.sqrt(areas.__len__())))
        counts, edges = nmpy.histogram(areas, bins=n_bins)
        if should_return_centers:
            centers = 0.5 * (edges[:-1] + edges[1:])
            if should_round_centers:
                centers = nmpy.around(centers).astype(nmpy.uint64)
            edges = centers

        return counts, edges

    def ClearBorderObjects(self) -> None:
        """"""
        for segmentation in self:
            segmentation.ClearBorderObjects()

    def FilterCellsOut(
        self,
        CellIssues: CellIssues_h,
        /,
        **kwargs,
    ) -> None:
        """
        Currently, only applicable to the cell segmentation when no other compartments are present

        Parameters
        ----------
        CellIssues: Arguments are: cell label (from 1), labeled segmentation, and (optional) keyword arguments; Returned
            value can be None, an str, or a sequence of str.
        kwargs: Passed to CellIsInvalid as keyword arguments with "frame_idx" (from 0) automatically added
        """
        if "frame_idx" in kwargs:
            raise ValueError(
                f'{kwargs}: Parameter name "frame_idx" '
                f"is reserved by {segmentations_t.FilterCellsOut.__name__}"
            )

        kwargs["frame_idx"] = None
        for f_idx, segmentation in enumerate(self):
            kwargs["frame_idx"] = f_idx
            segmentation.FilterCellsOut(CellIssues, **kwargs)

    def CorrectBasedOnTemporalCoherence(
        self,
        /,
        *,
        min_jaccard: float = 0.75,
        max_area_discrepancy: float = 0.25,
        min_cell_area: int = 0,
    ) -> None:
        """
        Actually, Pseudo-Jaccard
        """
        base_description = "Segmentation Correction(s) "
        n_corrections = 0
        with prgs.ProgressDesign() as progress:
            progress_context = prgs.progress_context_t(
                progress,
                self.__len__() - 1,
                first=1,
                description=base_description + "0",
            )
            for f_idx in progress_context.elements:
                n_corrections += self[f_idx].CorrectBasedOnTemporalCoherence(
                    self[f_idx - 1],
                    min_jaccard=min_jaccard,
                    max_area_discrepancy=max_area_discrepancy,
                    min_cell_area=min_cell_area,
                    time_point=f_idx,
                )
                progress_context.UpdateDescription(
                    base_description + str(n_corrections)
                )

        # Otherwise, the first frame does not have the same versions as the other ones
        self[0].AddFakeVersion(self[1].version_name)

    def AsDicts(self) -> Sequence[Dict[str, Any]]:
        """"""
        return [_sgm.AsDict() for _sgm in self]
