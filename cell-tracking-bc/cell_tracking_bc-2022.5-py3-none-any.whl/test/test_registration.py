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
import skimage.data as data
import skimage.transform as trsf
import skimage.util as util

import cell_tracking_BC.task.registration as rgst


angle = 35.0
print(f"true rotation={angle}")

image = data.retina()[..., 0]
image = util.img_as_float(image)

rotated = trsf.rotate(image, angle)

rotation, scaling = rgst.RotationScaling(image, rotated)
print(f"{rotation=}\n{scaling=}")

transformed = rgst.RotatedScaled(rotated, -rotation, 1.0 / scaling)

pypl.matshow(image)
pypl.matshow(rotated)
pypl.matshow(transformed)
pypl.show()
