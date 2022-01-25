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

import matplotlib.pyplot as pypl
import numpy as nmpy
from skimage.draw import ellipse as ellipse_t

from cell_tracking_BC.task.segmentation import (
    CorrectSegmentationsBasedOnTemporalCoherence,
)


MIN_JACCARD = 0.75

shape = (100, 100)

cell_1 = (10, 12, nmpy.pi / 8.0)
cell_2 = (14, 16, nmpy.pi / 10.0)
cell_3 = (15, 18, -nmpy.pi / 4.0)

position_1 = (30, 50)
shift_2 = (15, 18)
shift_3 = (23, -12)

trajectory_1_shifts = (-4, 0)
trajectory_2_shifts = (1, 4)
trajectory_3_shifts = (5, 0)
# cells_shifts = ((0,0,0),(0,0,1),(0,1,0),(1,0,0),(1,1,1))  # For checking base configurations
cells_shifts = (
    (1, 1, 1),
    (1, 0, 0),
    (1, 1, 1),
    (1, 0, 0),
    (0, 0, 0),
    (1, 1, 1),
    (1, 0, 0),
    (0, 0, 0),
    (0, 0, 1),
    (1, 1, 1),
    (0, 0, 0),
    (1, 1, 1),
)


cells = (cell_1, cell_2, cell_3)
relative_shifts = ((0, 0), shift_2, shift_3)
trajectory_shifts = (trajectory_1_shifts, trajectory_2_shifts, trajectory_3_shifts)

trajectories = tuple([] for _ in range(3))
for cells_shift in cells_shifts:
    for cell_shift, relative_shift, trajectory_shift, trajectory in zip(
        cells_shift, relative_shifts, trajectory_shifts, trajectories
    ):
        position = list(position_1)
        for c_idx in range(2):
            position[c_idx] += (
                relative_shift[c_idx] + cell_shift * trajectory_shift[c_idx]
            )
        trajectory.append(position)

frames = []
for f_idx in range(trajectories[0].__len__()):
    frame = nmpy.zeros(shape, dtype=nmpy.uint8)
    for cell, trajectory in zip(cells, trajectories):
        position = trajectory[f_idx]
        cell_map = ellipse_t(*position, *(cell[:2]), shape=shape, rotation=cell[2])
        frame[cell_map] = 1
    frames.append(frame)
uncorrected = nmpy.concatenate(frames, axis=1)

_ = CorrectSegmentationsBasedOnTemporalCoherence(frames, min_jaccard=MIN_JACCARD)
corrected = nmpy.concatenate(frames, axis=1)

pypl.imsave("../../_dev/before-correction.png", uncorrected, cmap="gray")
pypl.imsave("../../_dev/after-correction.png", corrected, cmap="gray")

pypl.matshow(uncorrected, cmap="gray")
pypl.matshow(corrected, cmap="gray")
pypl.show()
