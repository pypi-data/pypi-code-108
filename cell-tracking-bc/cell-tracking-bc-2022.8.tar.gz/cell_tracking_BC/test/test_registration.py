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
import skimage.data as data
import skimage.transform as trsf

import cell_tracking_BC.task.registration as rgst


angle = 18.0  # Must be between -20 and 20
print(f"true rotation={angle}")

image = data.retina()[..., 0]
threshold = nmpy.median(image)

image_as_int = (image > threshold).astype(nmpy.int8)

rotated = trsf.rotate(image_as_int, angle)
rotated_as_int = (rotated > 0.5 * nmpy.amax(rotated)).astype(nmpy.int8)

rotation = rgst.RotationInBinary(image_as_int, rotated_as_int)
print(f"{rotation=}")

rotated_back = rgst.RotatedLabeled(rotated_as_int, -rotation)

images = (image, image_as_int, rotated, rotated_as_int, rotated_back)
names = (
    "Original",
    "Thresholded",
    f"Rotated {angle}",
    "Rotated (int)",
    f"Rotated Back {-rotation}",
)
figure, all_axes = pypl.subplots(ncols=images.__len__())
for axes, image, name in zip(all_axes, images, names):
    axes.matshow(image, cmap="gray")
    axes.set_axis_off()
    axes.set_title(name)
figure.set_tight_layout(True)
pypl.show()
