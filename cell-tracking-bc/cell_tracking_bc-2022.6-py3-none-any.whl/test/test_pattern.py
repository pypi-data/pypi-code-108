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
from scipy.ndimage import gaussian_filter

import cell_tracking_BC.task.pattern as ptrn


signal = nmpy.zeros(100, dtype=nmpy.float64)
signal[(signal.size // 2) :] = 2.0
signal = gaussian_filter(signal, 2)
signal += 0.2 * nmpy.random.randn(signal.size)

pattern_abscissa = nmpy.linspace(-5.0, 5.0, num=20)
pattern = 1.0 / (1.0 + nmpy.exp(-pattern_abscissa))

matching = ptrn.match_template(signal, pattern, pad_input=True, mode="edge")

pypl.plot(signal, "g-", label="Signal")
pypl.plot(pattern, "r-", label="Pattern")
pypl.plot(matching, "b-", label="Matching")
pypl.show()
