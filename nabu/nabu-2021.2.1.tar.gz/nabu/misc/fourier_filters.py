# -*- coding: utf-8 -*-
"""
Fourier filters.
"""
import numpy as np
import scipy.special as spspe

def get_lowpass_filter(img_shape, cutoff_par=None, use_rfft=False, data_type=np.float64):
    """Computes a low pass filter using the erfc function.

    Parameters
    ----------
    img_shape: tuple
        Shape of the image
    cutoff_par: float or sequence of two floats
        Position of the cut off in pixels, if a sequence is given the second float expresses the
        width of the transition region which is given as a fraction of the cutoff frequency.
        When only one float is given for this argument a gaussian is applied whose sigma is the
        parameter.
        When a sequence of two numbers is given then the filter is 1 ( no filtering) till the cutoff
        frequency while a smooth erfc transition to zero is done
    use_rfft: boolean, optional
        Creates a filter to be used with the result of a rfft type of Fourier transform. Defaults to False.
    data_type: `numpy.dtype`, optional
        Specifies the data type of the computed filter. It defaults to `numpy.float64`

    Raises
    ------
    ValueError
        In case of malformed cutoff_par

    Returns
    -------
    numpy.array_like
        The computed filter
    """
    if cutoff_par is None:
        return 1
    elif isinstance(cutoff_par, (int, float)):
        cutoff_pix = cutoff_par
        cutoff_trans_fact = None
    else:
        try:
            cutoff_pix, cutoff_trans_fact = cutoff_par
        except ValueError:
            raise ValueError(
                "Argument cutoff_par  (which specifies the pass filter shape) must be either a scalar or a"
                " sequence of two scalars"
            )
        if (not isinstance(cutoff_pix, (int, float))) or (not isinstance(cutoff_trans_fact, (int, float))):
            raise ValueError(
                "Argument cutoff_par  (which specifies the pass filter shape) must be  one number or a sequence"
                "of two numbers"
            )

    coords = [np.fft.fftfreq(s, 1) for s in img_shape]
    coords = np.meshgrid(*coords, indexing="ij")

    r = np.sqrt(np.sum(np.array(coords, dtype=data_type) ** 2, axis=0))

    if cutoff_trans_fact is not None:
        k_cut = 0.5 / cutoff_pix
        k_cut_width = k_cut * cutoff_trans_fact
        k_pos_rescaled = (r - k_cut) / k_cut_width
        res = spspe.erfc(k_pos_rescaled) / 2
    else:
        res = np.exp(-(np.pi ** 2) * (r ** 2) * (cutoff_pix ** 2) * 2)

    # Making sure to force result to chosen data type
    res = res.astype(data_type)

    if use_rfft:
        slicelist = [slice(None)] * (len(res.shape) - 1) + [slice(0, res.shape[-1] // 2 + 1)]
        return res[tuple(slicelist)]
    else:
        return res


def get_highpass_filter(img_shape, cutoff_par=None, use_rfft=False, data_type=np.float64):
    """Computes a high pass filter using the erfc function.

    Parameters
    ----------
    img_shape: tuple
        Shape of the image
    cutoff_par: float or sequence of two floats
        Position of the cut off in pixels, if a sequence is given the second float expresses the
        width of the transition region which is given as a fraction of the cutoff frequency.
        When only one float is given for this argument a gaussian is applied whose sigma is the
        parameter, and the result is subtracted from 1 to obtain the high pass filter
        When a sequence of two numbers is given then the filter is 1 ( no filtering) above the cutoff
        frequency and then a smooth  transition to zero is done for smaller frequency
    use_rfft: boolean, optional
        Creates a filter to be used with the result of a rfft type of Fourier transform. Defaults to False.
    data_type: `numpy.dtype`, optional
        Specifies the data type of the computed filter. It defaults to `numpy.float64`

    Raises
    ------
    ValueError
        In case of malformed cutoff_par

    Returns
    -------
    numpy.array_like
        The computed filter
    """
    if cutoff_par is None:
        return 1
    else:
        return 1 - get_lowpass_filter(img_shape, cutoff_par, use_rfft=use_rfft, data_type=data_type)


def get_bandpass_filter(img_shape, cutoff_lowpass=None, cutoff_highpass=None, use_rfft=False, data_type=np.float64):
    """Computes a band pass filter using the erfc function.

    The cutoff structures should be formed as follows:

    - tuple of two floats: the first indicates the cutoff frequency, the second \
        determines the width of the transition region, as fraction of the cutoff frequency.

    - one float -> it represents the sigma of a gaussian which acts as a filter or anti-filter (1 - filter).

    Parameters
    ----------
    img_shape: tuple
        Shape of the image
    cutoff_lowpass: float or sequence of two floats
        Cutoff parameters for the low-pass filter
    cutoff_highpass: float or sequence of two floats
        Cutoff parameters for the high-pass filter
    use_rfft: boolean, optional
        Creates a filter to be used with the result of a rfft type of Fourier transform. Defaults to False.
    data_type: `numpy.dtype`, optional
        Specifies the data type of the computed filter. It defaults to `numpy.float64`

    Raises
    ------
    ValueError
        In case of malformed cutoff_par

    Returns
    -------
    numpy.array_like
        The computed filter
    """
    return get_lowpass_filter(
        img_shape, cutoff_par=cutoff_lowpass, use_rfft=use_rfft, data_type=data_type
    ) * get_highpass_filter(img_shape, cutoff_par=cutoff_highpass, use_rfft=use_rfft, data_type=data_type)
