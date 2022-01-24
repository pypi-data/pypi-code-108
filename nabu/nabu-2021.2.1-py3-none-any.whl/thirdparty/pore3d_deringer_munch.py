"""
The following de-striping method is adapted from the pore3d software.

:Organization: Elettra - Sincrotrone Trieste S.C.p.A.

:Version: 2013.05.01

References
----------
[1] F. Brun, A. Accardo, G. Kourousias, D. Dreossi, R. Pugliese. Effective implementation
of ring artifacts removal filters for synchrotron radiation microtomographic images. Proc.
of the 8th International Symposium on Image and Signal Processing (ISPA), pp. 672-676, Sept. 4-6,
Trieste (Italy), 2013.

The license follows.
"""
# Copyright (c) 2013, Elettra - Sincrotrone Trieste S.C.p.A.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holders nor the names of any
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np
try:
    import pywt
    __has_pywt__ = True
except ImportError:
    __has_pywt__ = False


def munchetal_filter(im, wlevel, sigma, wname='db15'):
    """Process a sinogram image with the Munch et al. de-striping algorithm.

    Parameters
    ----------
    im : array_like
        Image data as numpy array.
    wname : {'haar', 'db1'-'db20', 'sym2'-'sym20', 'coif1'-'coif5', 'dmey'}
        The wavelet transform to use.
    wlevel : int
        Levels of the wavelet decomposition.
    sigma : float
        Cutoff frequency of the Butterworth low-pass filtering.

    Example (using tiffile.py)
    --------------------------
    >>> im = imread('original.tif')
    >>> im = munchetal_filter(im, 'db15', 4, 1.0)
    >>> imsave('filtered.tif', im)

    References
    ----------
    B. Munch, P. Trtik, F. Marone, M. Stampanoni, Stripe and ring artifact removal with
    combined wavelet-Fourier filtering, Optics Express 17(10):8567-8591, 2009.
    """
    # Wavelet decomposition:
    coeffs = pywt.wavedec2(im.astype(np.float32), wname, level=wlevel, mode="periodization")
    coeffsFlt = [coeffs[0]]
    # FFT transform of horizontal frequency bands:
    for i in range(1, wlevel + 1):
        # FFT:
        fcV = np.fft.fftshift(np.fft.fft(coeffs[i][1], axis=0))
        my, mx = fcV.shape
        # Damping of vertical stripes:
        damp = 1 - np.exp(-(np.arange(-np.floor(my / 2.), -np.floor(my / 2.) + my) ** 2) / (2 * (sigma ** 2)))
        dampprime = np.kron(np.ones((1, mx)), damp.reshape((damp.shape[0], 1))) # np.tile(damp[:, np.newaxis], (1, mx))
        fcV = fcV * dampprime
        # Inverse FFT:
        fcVflt = np.real(np.fft.ifft(np.fft.ifftshift(fcV), axis=0))
        cVHDtup = (coeffs[i][0], fcVflt, coeffs[i][2])
        coeffsFlt.append(cVHDtup)

    # Get wavelet reconstruction:
    im_f = np.real(pywt.waverec2(coeffsFlt, wname, mode="periodization"))
    # Return image according to input type:
    if (im.dtype == 'uint16'):
        # Check extrema for uint16 images:
        im_f[im_f < np.iinfo(np.uint16).min] = np.iinfo(np.uint16).min
        im_f[im_f > np.iinfo(np.uint16).max] = np.iinfo(np.uint16).max
        # Return filtered image (an additional row and/or column might be present):
        return im_f[0:im.shape[0], 0:im.shape[1]].astype(np.uint16)
    else:
        return im_f[0:im.shape[0], 0:im.shape[1]]


if not(__has_pywt__):
    munchetal_filter = None
