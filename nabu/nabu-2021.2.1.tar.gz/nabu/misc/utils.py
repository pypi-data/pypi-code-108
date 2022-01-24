import numpy as np


def rescale_data(data, new_min, new_max, data_min=None, data_max=None):
    if data_min is None:
        data_min = np.min(data)
    if data_max is None:
        data_max = np.max(data)
    return (new_max - new_min)/(data_max - data_min) * (data - data_min) + new_min


def get_dtype_range(dtype, normalize_floats=False):
    if np.dtype(dtype).kind in ["u", "i"]:
        dtype_range = (np.iinfo(dtype).min, np.iinfo(dtype).max)
    else:
        if normalize_floats:
            dtype_range = (-1., 1.)
        else:
            dtype_range = (np.finfo(dtype).min, np.finfo(dtype).max)
    return dtype_range


def psnr(img1, img2):
    if img1.dtype != img2.dtype:
        raise ValueError("both images should have the same data type")
    dtype_range = get_dtype_range(img1.dtype, normalize_floats=True)
    dtype_range = dtype_range[-1] - dtype_range[0]
    if np.dtype(img1.dtype).kind in ["f", "c"]:
        img1 = rescale_data(img1, -1., 1.)
        img2 = rescale_data(img2, -1., 1.)
    mse = np.mean((img1.astype(np.float64) - img2)**2)
    return 10 * np.log10((dtype_range ** 2) / mse)



#
# silx.opencl.utils.ConvolutionInfos cannot be used as long as
# silx.opencl instantiates the "ocl" singleton in __init__,
# leaving opencl contexts all over the place in some cases.
#
# so for now: copypasta
#

class ConvolutionInfos(object):
    allowed_axes = {
        "1D": [None],
        "separable_2D_1D_2D": [None, (0, 1), (1, 0)],
        "batched_1D_2D": [(0,), (1,)],
        "separable_3D_1D_3D": [
            None,
            (0, 1, 2),
            (1, 2, 0),
            (2, 0, 1),
            (2, 1, 0),
            (1, 0, 2),
            (0, 2, 1)
        ],
        "batched_1D_3D": [(0,), (1,), (2,)],
        "batched_separable_2D_1D_3D": [(0,), (1,), (2,)], # unsupported (?)
        "2D": [None],
        "batched_2D_3D": [(0,), (1,), (2,)],
        "separable_3D_2D_3D": [
            (1, 0),
            (0, 1),
            (2, 0),
            (0, 2),
            (1, 2),
            (2, 1),
        ],
        "3D": [None],
    }
    use_cases = {
        (1, 1): {
            "1D": {
                "name": "1D convolution on 1D data",
                "kernels": ["convol_1D_X"],
            },
        },
        (2, 2): {
            "2D": {
                "name": "2D convolution on 2D data",
                "kernels": ["convol_2D_XY"],
            },
        },
        (3, 3): {
            "3D": {
                "name": "3D convolution on 3D data",
                "kernels": ["convol_3D_XYZ"],
            },
        },
        (2, 1): {
            "separable_2D_1D_2D": {
                "name": "Separable (2D->1D) convolution on 2D data",
                "kernels": ["convol_1D_X", "convol_1D_Y"],
            },
            "batched_1D_2D": {
                "name": "Batched 1D convolution on 2D data",
                "kernels": ["convol_1D_X", "convol_1D_Y"],
            },
        },
        (3, 1): {
            "separable_3D_1D_3D": {
                "name": "Separable (3D->1D) convolution on 3D data",
                "kernels": ["convol_1D_X", "convol_1D_Y", "convol_1D_Z"],
            },
            "batched_1D_3D": {
                "name": "Batched 1D convolution on 3D data",
                "kernels": ["convol_1D_X", "convol_1D_Y", "convol_1D_Z"],
            },
            "batched_separable_2D_1D_3D": {
                "name": "Batched separable (2D->1D) convolution on 3D data",
                "kernels": ["convol_1D_X", "convol_1D_Y", "convol_1D_Z"],
            },
        },
        (3, 2): {
            "separable_3D_2D_3D": {
                "name": "Separable (3D->2D) convolution on 3D data",
                "kernels": ["convol_2D_XY", "convol_2D_XZ", "convol_2D_YZ"],
            },
            "batched_2D_3D": {
                "name": "Batched 2D convolution on 3D data",
                "kernels": ["convol_2D_XY", "convol_2D_XZ", "convol_2D_YZ"],
            },
        },
    }

