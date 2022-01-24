import math
import numpy as np

def pad_interpolate(im, padded_img_shape_vh, translation_vh=None, padding_mode="reflect"):
    """
    This function produces a centered padded image and , optionally if translation_vh is set,
    performs a Fourier shift of the whole image. In case of translation, the image is first padded to
    a larger extent, that encompasses the final padded with plus a translation margin, and then translated,
    and final recut to the required padded width.
    The values are translated: if a feature appear at x in the original image it will appear at pad+translation+x
    in the final image.

    Parameters
    ------------
    im: np.ndaray
       the input image
    translation_vh: a sequence of two float
       the vertical and horizontal shifts
    """

    if translation_vh is not None:
        pad_extra = 2 ** (1 + np.ceil(np.log2(np.maximum(1, np.ceil(abs(np.array(translation_vh)))))).astype(np.int32))
    else:
        pad_extra = [0, 0]

    origy, origx = im.shape
    rety = padded_img_shape_vh[0] + pad_extra[0]
    retx = padded_img_shape_vh[1] + pad_extra[1]

    xpad = [0, 0]
    xpad[0] = math.ceil((retx - origx) / 2)
    xpad[1] = retx - origx - xpad[0]

    ypad = [0, 0]
    ypad[0] = math.ceil((rety - origy) / 2)
    ypad[1] = rety - origy - ypad[0]

    y2 = origy - ypad[1]
    x2 = origx - xpad[1]

    if ypad[0] + 1 > origy or xpad[0] + 1 > origx or y2 < 1 or x2 < 1:
        raise ValueError("Too large padding for this reflect padding type")

    padded_im = np.pad(im, pad_width=((ypad[0], ypad[1]), (xpad[0], xpad[1])), mode=padding_mode)

    if translation_vh is not None:
        freqs_list = list(map(np.fft.fftfreq, padded_im.shape))
        shifts_list = [np.exp(-2.0j * np.pi * freqs * trans) for (freqs, trans) in zip(freqs_list, translation_vh)]
        shifts_2D = shifts_list[0][:, None] * shifts_list[1][None, :]
        padded_im = np.fft.ifft2(np.fft.fft2(padded_im) * shifts_2D).real
        padded_im = recut(padded_im, padded_img_shape_vh)

    return padded_im


def recut(im, new_shape_vh):
    """
    This method implements a centered cut which reverts the centered padding
    applied in the present class.

    Parameters
    -----------
    im: np.ndarray
        A 2D image.
    new_shape_vh:  tuple
        The shape of the cutted image.

    Returns
    --------
        The image cutted to new_shape_vh.
    """

    new_shape_vh = np.array(new_shape_vh)

    old_shape_vh = np.array(im.shape)

    center_vh = (old_shape_vh - 1) / 2

    start_vh = np.round(0.5 + center_vh - new_shape_vh / 2).astype(np.int32)
    end_vh = start_vh + new_shape_vh

    return im[start_vh[0] : end_vh[0], start_vh[1] : end_vh[1]]
