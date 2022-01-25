import os
import numpy as np
from time import time
from itertools import product

_warnings = {}


def nextpow2(N):
    p = 1
    while p < N:
        p *= 2
    return p


def updiv(a, b):
    return (a + (b - 1)) // b


def get_folder_path(foldername=""):
    _file_dir = os.path.dirname(os.path.realpath(__file__))
    package_dir = _file_dir
    return os.path.join(package_dir, foldername)


def get_cuda_srcfile(filename):
    src_relpath = os.path.join("cuda", "src")
    cuda_src_folder = get_folder_path(foldername=src_relpath)
    return os.path.join(cuda_src_folder, filename)


def _sizeof(Type):
    """
    return the size (in bytes) of a scalar type, like the C behavior
    """
    return np.dtype(Type).itemsize


class FFTShift(object):
    def __init__(self, N):
        self._init_shape(N)

    def _init_shape(self, N):
        self.N = N
        self.N2 = N // 2
        self.N2b = N - self.N2  # N = N2 + N2b

    def fftshift_coord(self, i):
        if i < self.N2:
            return i + self.N2b
        else:
            return i - self.N2

    def fftshift_coords(self, coords):
        N2 = self.N2
        N2b = self.N2b
        res = np.zeros_like(coords)
        mask = coords < N2
        res[:N2] = coords[mask] + N2b
        res[N2:] = coords[np.logical_not(mask)] - N2
        return res


def generate_powers():
    """
    Generate a list of powers of [2, 3, 5, 7],
    up to (2**15)*(3**9)*(5**6)*(7**5).
    """
    primes = [2, 3, 5, 7]
    maxpow = {2: 15, 3: 9, 5: 6, 7: 5}
    valuations = []
    for prime in primes:
        # disallow any odd number (for R2C transform), and any number
        # not multiple of 4 (Ram-Lak filter behaves strangely when
        # dwidth_padded/2 is not even)
        minval = 2 if prime == 2 else 0
        valuations.append(range(minval, maxpow[prime] + 1))
    powers = product(*valuations)
    res = []
    for pw in powers:
        res.append(np.prod(list(map(lambda x: x[0] ** x[1], zip(primes, pw)))))
    return np.unique(res)


def calc_padding_lengths1D(length, length_padded):
    """
    Compute the padding lengths at both side along one dimension.

    Parameters
    ----------
    length: int
        Number of elements along one dimension of the original array
    length_padded: tuple
        Number of elements along one dimension of the padded array

    Returns
    -------
    pad_lengths: tuple
        A tuple under the form (padding_left, padding_right). These are the
        lengths needed to pad the original array.
    """
    pad_left = (length_padded - length) // 2
    pad_right = length_padded - length - pad_left
    return (pad_left, pad_right)


def calc_padding_lengths(shape, shape_padded):
    """
    Multi-dimensional version of calc_padding_lengths1D.
    Please refer to the documentation of calc_padding_lengths1D.
    """
    assert len(shape) == len(shape_padded)
    padding_lengths = []
    for dim_len, dim_len_padded in zip(shape, shape_padded):
        pad0, pad1 = calc_padding_lengths1D(dim_len, dim_len_padded)
        padding_lengths.append((pad0, pad1))
    return tuple(padding_lengths)


# ------------------------------------------------------------------------------
# ------------------------ Image (move elsewhere ?) ----------------------------
# ------------------------------------------------------------------------------


def generate_coords(img_shp, center=None):
    l_r, l_c = float(img_shp[0]), float(img_shp[1])
    R, C = np.mgrid[:l_r, :l_c]  # np.indices is faster
    if center is None:
        center0, center1 = l_r / 2.0, l_c / 2.0
    else:
        center0, center1 = center
    R += 0.5 - center0
    C += 0.5 - center1
    return R, C


def clip_circle(img, center=None, radius=None):
    R, C = generate_coords(img.shape, center)
    M = R ** 2 + C ** 2
    res = np.zeros_like(img)
    res[M < radius ** 2] = img[M < radius ** 2]
    return res


def apply_along_z(vol, func, res):
    for i in range(vol.shape[0]):
        res[i] = func(vol[i])
    return res


# ------------------------------------------------------------------------------
# ---------------------------- Decorators --------------------------------------
# ------------------------------------------------------------------------------


def measure_time(func):
    def wrapper(*args, **kwargs):
        t0 = time()
        res = func(*args, **kwargs)
        el = time() - t0
        return el, res

    return wrapper


def wip(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        if func_name not in _warnings:
            _warnings[func_name] = 1
            print(
                "Warning: function %s is a work in progress, it is likely to change in the future"
            )
        return func(*args, **kwargs)

    return wrapper


def warning(msg):
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            if func_name not in _warnings:
                _warnings[func_name] = 1
                print(msg)
                res = func(*args, **kwargs)
                return res

        return wrapper

    return decorator


def log_work(func):
    def wrapper(*args, **kwargs):
        print("[%d] Executing %s ..." % (os.getpid(), func.__name__))  #  TODO in file ?
        res = func(*args, **kwargs)
        print("[%d] ... done" % os.getpid())
        return res

    return wrapper
