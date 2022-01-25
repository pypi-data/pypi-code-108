# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "30/10/2018"

"""Include default settings for the tofu widget"""

# default parameters for slice stack
SLICE_STACK_RANGE_HS = 50
"""default range half size for slice stack reconstruction"""
SLICE_STACK_STEP_SIZE = 1
"""default step size for slice stack reconstruction"""
SLICE_STACK_NB_SLICES = 100
"""default number of slices for slice stack reconstruction"""

# default parameters for rotation center
ROT_CENTER_RANGE_HS = 25
"""default range half size for rotation center reconstruction"""
ROT_CENTER_STEP_SIZE = 0.5
"""default step size for rotation center reconstruction"""
ROT_CENTER_NB_SLICES = 50
"""default number of slices for rotation center reconstruction"""

# default parameters for lamino angle
LAMINO_ANG_RANGE_HS = 0.5
"""default range half size for the lamino angle reconstruction"""
LAMINO_ANG_STEP_SIZE = 0.01
"""default step size for the lamino angle reconstruction"""
LAMINO_ANG_NB_SLICES = 100
"""default number of slices for lamino angle reconstruction"""

# default parameters for psi angle
PSI_ANG_RANGE_HS = 0.5
"""default range half size for the psi angle reconstruction"""
PSI_ANG_STEP_SIZE = 0.01
"""default step size for the psi angle reconstruction"""
PSI_ANG_NB_SLICES = 100
"""default number of slices for psi angle reconstruction"""


_N_SLICE_LIMITS_HIGH = 350
"""If the number of slices is upper than this limits then this will generate a
warning and display the information into"""

_COLOR_HIGH = 250, 0, 0

_N_SLICE_LIMITS_MEDIUM = 100
"""If the number of slices is upper this than limits then this will display the
cut selection information into"""

_COLOR_MEDIUM = 200, 150, 0
