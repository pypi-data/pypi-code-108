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

"""
This module was adapted from the module defining the function ``match_template`` of Scikit-Image.
Function documentation:
https://scikit-image.org/docs/dev/api/skimage.feature.html?highlight=match#skimage.feature.match_template
Module Code:
https://github.com/scikit-image/scikit-image/blob/main/skimage/feature/template.py

The original function ``match_template`` was adapted to the 1-D case, and the parameter ``normalized`` was added. Let us
remind that the Pearson correlation coefficient involves a normalization by the product of the standard deviations. See
for example:
https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
The parameter ``normalized`` can take the following values:
    - None: no normalization is performed; the response is the local covariance; it is unbounded;
    - "max": the response is the local covariance C normalized by the maximum of C;
    - "max_abs": the response is the local covariance C normalized by the maximum of C in absolute value;
    - "stddev": corresponds to the original normalization, so that the response is the Pearson correlation
    coefficient.
    - "template": normalizes by numpy.sum((template - numpy.mean(template)) ** 2) so that the response to itself is 1.
"""

import warnings as wrng
from typing import Optional, Sequence, Union

import numpy as nmpy
from scipy.signal import fftconvolve


array_t = nmpy.ndarray


def _window_sum_1d(signal: array_t, window_length: int, /) -> array_t:
    """"""
    window_sum = nmpy.cumsum(signal)
    window_sum = window_sum[window_length:-1] - window_sum[: -window_length - 1]

    return window_sum


def match_template(
    signal: Union[array_t, Sequence[float]],
    template: Union[array_t, Sequence[float]],
    /,
    *,
    normalized: Optional[str] = None,
    pad_input: bool = False,
    mode: str = "constant",
    constant_values: float = 0.0,
) -> Optional[array_t]:
    """"""
    signal = nmpy.array(signal, dtype=nmpy.float64, copy=False)
    template = nmpy.array(template, dtype=nmpy.float64, copy=False)

    if (signal.ndim != template.ndim) or (signal.ndim != 1):
        raise ValueError(
            "Dimensionality of template must be "
            "equal to the dimensionality of signal. "
            "Both must be equal to one."
        )
    if signal.size < template.size:
        wrng.warn(
            f"{match_template.__name__}: Signal (length={signal.size}) "
            f"must be larger than template (length={template.size})"
        )
        return None

    signal_length = signal.size
    pad_length = template.size
    if mode == "constant":
        signal = nmpy.pad(
            signal, pad_width=pad_length, mode=mode, constant_values=constant_values
        )
    else:
        signal = nmpy.pad(signal, pad_width=pad_length, mode=mode)

    image_window_sum = _window_sum_1d(signal, template.size)

    template_mean = template.mean()
    template_length = template.size
    template_ssd = nmpy.sum((template - template_mean) ** 2)

    xcorr = fftconvolve(signal, template[::-1], mode="valid")[1:-1]

    numerator = xcorr - image_window_sum * template_mean

    if normalized is None:
        response = numerator
    elif normalized in ("max", "max_abs"):
        if normalized == "max":
            denominator = nmpy.amax(numerator)
        else:
            denominator = nmpy.amax(nmpy.fabs(numerator))
        if denominator > nmpy.finfo(numerator.dtype).eps:
            response = numerator / denominator
        else:
            response = numerator
    elif normalized == "stddev":
        image_window_sum2 = _window_sum_1d(signal ** 2, template.size)

        denominator = image_window_sum2
        nmpy.multiply(image_window_sum, image_window_sum, out=image_window_sum)
        nmpy.divide(image_window_sum, template_length, out=image_window_sum)
        denominator -= image_window_sum
        denominator *= template_ssd
        # sqrt of negative number not allowed
        nmpy.maximum(denominator, 0, out=denominator)
        nmpy.sqrt(denominator, out=denominator)

        response = nmpy.zeros_like(xcorr)

        # avoid zero-division
        mask = denominator > nmpy.finfo(response.dtype).eps

        response[mask] = numerator[mask] / denominator[mask]
    elif normalized == "template":
        response = numerator / template_ssd
    else:
        raise ValueError(f"{normalized}: Invalid normalization method")

    if pad_input:
        d0 = (template_length - 1) // 2
        d1 = d0 + signal_length
    else:
        d0 = template_length - 1
        d1 = d0 + signal_length - template_length + 1

    return response[slice(d0, d1)]
