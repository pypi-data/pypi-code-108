import numpy as np

"""
Specialized functions for image binning.
"""


# 5 ms on 2048*2047 image (f32 or u16): 1.7 GB/s
# should be enough to be faster than reading a file from disk
# Can be accelerated well below 1ms with numba.njit(parallel=True)
def binning2(img, out_dtype=np.float32):
    """
    Perform a 2X2 binning on an image.
    """
    s = img.shape
    shp = (s[0] - (s[0] % 2), s[1] - (s[1] % 2))
    sub_img = img[:shp[0], :shp[1]]
    out_shp = (shp[0] // 2, shp[1] // 2)
    res = np.zeros(out_shp, dtype=out_dtype)
    # astype() prevents overflows for integer-like input arrays, at the expanse of 50% lower performance
    res[:] = sub_img[::2, ::2].astype(out_dtype) + sub_img[1::2, ::2] + sub_img[::2, 1::2] + sub_img[1::2, 1::2]
    res *= 0.25
    return res


def binning2_horiz(img, out_dtype=np.float32):
    """
    Perform a 2-binning horizontally on an image.
    """
    s = img.shape
    shp = (s[0], s[1] - (s[1] % 2))
    sub_img = img[:, :shp[1]]
    out_shp = (shp[0], shp[1] // 2)
    res = np.zeros(out_shp, dtype=out_dtype)
    # astype() prevents overflows for integer-like input arrays, at the expanse of 50% lower performance
    res[:] = sub_img[:, ::2].astype(out_dtype) + sub_img[:, 1::2]
    res *= 0.5
    return res


def binning2_vertic(img, out_dtype=np.float32):
    """
    Perform a 2-binning vertically on an image.
    """
    s = img.shape
    shp = (s[0] - (s[0] % 2), s[1])
    sub_img = img[:shp[0], :]
    out_shp = (shp[0] //2, shp[1])
    res = np.zeros(out_shp, dtype=out_dtype)
    # astype() prevents overflows for integer-like input arrays, at the expanse of 50% lower performance
    res[:] = sub_img[::2, :].astype(out_dtype) + sub_img[1::2, :]
    res *= 0.5
    return res


def binning3(img, out_dtype=np.float32):
    """
    Perform a 3X3 binning on an image.
    """
    s = img.shape
    shp = (s[0] - (s[0] % 3), s[1] - (s[1] % 3))
    sub_img = img[:shp[0], :shp[1]]
    out_shp = (shp[0] // 3, shp[1] // 3)
    res = np.zeros(out_shp, dtype=out_dtype)
    # astype() prevents overflows for integer-like input arrays, at the expanse of 50% lower performance
    res[:] = sub_img[::3, ::3].astype(out_dtype)  + sub_img[1::3, ::3]  + sub_img[2::3, ::3] \
           + sub_img[::3, 1::3] + sub_img[1::3, 1::3] + sub_img[2::3, 1::3] \
           + sub_img[::3, 2::3] + sub_img[1::3, 2::3] + sub_img[2::3, 2::3]
    res /= 9.
    return res



def binning3_horiz(img, out_dtype=np.float32):
    """
    Perform a 3-binning on an image horizontally
    """
    s = img.shape
    shp = (s[0], s[1] - (s[1] % 3))
    sub_img = img[:, :shp[1]]
    out_shp = (shp[0], shp[1] // 3)
    res = np.zeros(out_shp, dtype=out_dtype)
    # astype() prevents overflows for integer-like input arrays, at the expanse of 50% lower performance
    res[:] = sub_img[:, ::3].astype(out_dtype)  + sub_img[:, 1::3] + sub_img[:, 2::3]
    res /= 3.
    return res



def binning3_vertic(img, out_dtype=np.float32):
    """
    Perform a 3-binning on an image vertically.
    """
    s = img.shape
    shp = (s[0] - (s[0] % 3), s[1])
    sub_img = img[:shp[0], :]
    out_shp = (shp[0] // 3, shp[1])
    res = np.zeros(out_shp, dtype=out_dtype)
    # astype() prevents overflows for integer-like input arrays, at the expanse of 50% lower performance
    res[:] = sub_img[::3, :].astype(out_dtype)  + sub_img[1::3, :] + sub_img[2::3, :]
    res /= 3.
    return res





def get_binning_function(binning):
    """
    Determine the binning function to use.
    """
    binning_functions = {
        (2, 2): binning2,
        (2, 1): binning2_vertic,
        (1, 2): binning2_horiz,
        (3, 3): binning3,
        (3, 1): binning3_vertic,
        (1, 3): binning3_horiz,
        (2, 3): None, # current limitation
        (3, 2): None, # current limitation
    }
    if binning not in binning_functions:
        raise ValueError("Could not get a function for binning factor %s" % binning)
    return binning_functions[binning]
