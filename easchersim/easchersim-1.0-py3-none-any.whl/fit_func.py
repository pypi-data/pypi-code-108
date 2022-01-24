# BSD 3-Clause License
#
# Copyright (c) 2021, Austin Cummings
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy as np

################################################################
#Fitting Cherenkov Spatial Profile

#Exponential Profile
def custom_fit(x, x0, Nmax, scale):
	y = np.piecewise(x, [np.abs(x) < x0, np.abs(x) >= x0],
					 [lambda x: Nmax, lambda x: Nmax*np.exp(-(np.abs(x)-np.abs(x0))/scale)])
	return y

#Gaussian Profile
def gaussian_fit(x, x0, Nmax):
	y = np.piecewise(x, [np.abs(x) < x0, np.abs(x) >= x0],
					 [lambda x: Nmax, lambda x: Nmax*np.exp(-((np.abs(x)-x0)**2)/(2*x0**2))])
	return y

def mod_gauss_fit(x, x0, x1, Nmax, scale):
	y = np.piecewise(x, [np.abs(x) < x0, np.abs(x) >= x0],
					 [lambda x: np.log(Nmax), lambda x: np.log(Nmax*np.exp(-((np.abs(x)-x0)/x1)**scale))])
	return y

#Polynomial Profile (edges go down as 1/x^n)
def log_fit(x, x0, Nmax, scale):
	y = np.piecewise(x, [np.abs(x) < x0, np.abs(x) >= x0],
					 [lambda x: Nmax, lambda x: Nmax*(x0/np.abs(x))**scale])
	return y

def better_fit(x, x0, x1, x2, A, scale):
	y = np.piecewise(x, [np.abs(x) < x0, (np.abs(x) >= x0)&(np.abs(x) <= x1), np.abs(x)>x1],
					 [lambda x: A, lambda x: A+scale*np.log((x0/x)), lambda x: A+scale*np.log(x0/x1)-(x-x1)/x2])
	return y

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

#Gets the weighted percentiles of data
def weighted_percentile(data, percents, weights=None):
	''' percents in units of 1%
		weights specifies the frequency (count) of data.
	'''
	if weights is None:
		return np.percentile(data, percents)
	ind=np.argsort(data)
	d=data[ind]
	w=weights[ind]
	p=1.*w.cumsum()/w.sum()*100
	y=np.interp(percents, p, d)
	return y