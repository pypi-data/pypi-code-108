import os
import warnings
from time import time
import posixpath
from itertools import product
from functools import lru_cache
from multiprocessing import cpu_count
import numpy as np

def nextpow2(N, dtype=np.int32):
    return 2 ** np.ceil(np.log2(N)).astype(dtype)


def previouspow2(N, dtype=np.int32):
    return 2 ** np.floor(np.log2(N)).astype(dtype)


def updiv(a, b):
    return (a + (b - 1)) // b


def convert_index(idx, idx_max, default_val):
    """
    Convert an index (possibly negative or None) to a non-negative integer.

    Parameters
    ----------
    idx: int or None
        Index
    idx_max: int
        Maximum value (upper bound) for the index.
    default_val: int
        Default value if idx is None

    Examples
    ---------
    Given an integer `M`, `J = convert_index(i, M, XX)` returns an integer in the
    mathematical range [0, M] (or Python `range(0, M)`). `J` can then be used
    to define an upper bound of a range.
    """
    if idx is None:
        return default_val
    if idx > idx_max:
        return idx_max
    if idx < 0:
        return idx % idx_max
    return idx


def get_folder_path(foldername=""):
    _file_dir = os.path.dirname(os.path.realpath(__file__))
    package_dir = _file_dir
    return os.path.join(package_dir, foldername)


def get_cuda_srcfile(filename):
    src_relpath = os.path.join("cuda", "src")
    cuda_src_folder = get_folder_path(foldername=src_relpath)
    return os.path.join(cuda_src_folder, filename)


def get_resource_file(filename, subfolder=None):
    subfolder = subfolder or []
    relpath = os.path.join("resources", *subfolder)
    abspath = get_folder_path(foldername=relpath)
    return os.path.join(abspath, filename)


def get_available_threads():
    return len(os.sched_getaffinity(0))


def is_writeable(location):
    """
    Return True if a file/location is writeable.
    """
    return os.access(location, os.W_OK)

def is_int(num, eps=1e-7):
    return abs(num - int(num)) < eps

def _sizeof(Type):
    """
    return the size (in bytes) of a scalar type, like the C behavior
    """
    return np.dtype(Type).itemsize


def get_ftype(url):
    """
    return supposed filetype of an url
    """
    if hasattr(url, "file_path"):
        return os.path.splitext(url.file_path())[-1].replace(".", "")
    else:
        return os.path.splitext(url)[-1].replace(".", "")


def get_2D_3D_shape(shape):
    if len(shape) == 2:
        return (1, ) + shape
    return shape

def get_subregion(sub_region):
    ymin, ymax = None, None
    if sub_region is None:
        xmin, xmax, ymin, ymax = None, None, None, None
    elif len(sub_region) == 2:
        first_part, second_part = sub_region
        if np.iterable(first_part) and np.iterable(second_part):
            xmin, xmax = first_part
            ymin, ymax = second_part
        else:
            xmin, xmax = sub_region
    elif len(sub_region) == 4:
        xmin, xmax, ymin, ymax = sub_region
    else:
        raise ValueError("Expected parameter in the form (a, b, c, d) or ((a, b), (c, d))")
    return xmin, xmax, ymin, ymax


def get_3D_subregion(sub_region):
    if sub_region is None:
        xmin, xmax, ymin, ymax, zmin, zmax = None, None, None, None, None, None
    elif len(sub_region) == 3:
        first_part, second_part, third_part = sub_region
        xmin, xmax = first_part
        ymin, ymax = second_part
        zmin, zmax = third_part
    elif len(sub_region) == 6:
        xmin, xmax, ymin, ymax, zmin, zmax = sub_region
    else:
        raise ValueError(
            "Expected parameter in the form (xmin, xmax, ymin, ymax, zmin, zmax) or ((xmin, xmax), (ymin, ymax), (zmin, zmax))"
        )
    return xmin, xmax, ymin, ymax, zmin, zmax


def to_3D_array(arr):
    """
    Turn an array to a (C-Contiguous) 3D array with the layout (n_arrays, n_y, n_x).
    """
    if arr.ndim == 3:
        return arr
    return np.tile(arr, (1, 1, 1))


def view_as_images_stack(img):
    """
    View an image (2D array) as a stack of one image (3D array).
    No data is duplicated.
    """
    return img.reshape((1, ) + img.shape)



def merged_shape(shapes, axis=0):
    n_img = sum(shape[axis] for shape in shapes)
    if axis == 0:
        return (n_img, ) + shapes[0][1:]
    elif axis == 1:
        return (shapes[0][0], n_img, shapes[0][2])
    elif axis == 2:
        return shapes[0][:2] + (n_img, )


def is_device_backend(backend):
    return backend.lower() in ["cuda", "opencl"]


def get_decay(curve, cutoff=1e3, vmax=None):
    """
    Assuming a decreasing curve, get the first point below a certain threshold.

    Parameters
    ----------
    curve: numpy.ndarray
        A 1D array
    cutoff: float, optional
        Threshold. Default is 1000.
    vmax: float, optional
        Curve maximum value
    """
    if vmax is None:
        vmax = curve.max()
    return np.argmax(np.abs(curve) < vmax / cutoff)


@lru_cache(maxsize=1)
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
        valuations.append(range(minval, maxpow[prime]+1))
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
    pad_left = (length_padded - length)//2
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


def partition_dict(dict_, n_partitions):
    keys = np.sort(list(dict_.keys()))
    res = []
    for keys_arr in np.array_split(keys, n_partitions):
        d = {}
        for key in keys_arr:
            d[key] = dict_[key]
        res.append(d)
    return res


def subsample_dict(dic, subsampling_factor):
    """
    Subsample a dict where keys are integers.
    """
    res = {}
    indices = sorted(dic.keys())
    for i in indices[::subsampling_factor]:
        res[i] = dic[i]
    return res

def compare_dicts(dic1, dic2):
    """
    Compare two dictionaries. Return None if and only iff the dictionaries are the same.

    Parameters
    ----------
    dic1: dict
        First dictionary
    dic2: dict
        Second dictionary

    Returns
    -------
    res: result which can be the following:

       - None: it means that dictionaries are the same
       - empty string (""): the dictionaries do not have the same keys
       - nonempty string: path to the first differing items
    """
    if set(dic1.keys()) != set(dic2.keys()):
        return ""
    for key, val1 in dic1.items():
        val2 = dic2[key]
        if isinstance(val1, dict):
            res = compare_dicts(val1, val2)
            if res is not None:
                return posixpath.join(key, res)
        # Scalars and str
        elif np.isscalar(val1):
            if val1 != val2:
                return key
        # NoneType
        elif val1 is None:
            if val2 is not None:
                return key
        # Array-like
        elif np.iterable(val1):
            arr1 = np.array(val1)
            arr2 = np.array(val2)
            if arr1.ndim != arr2.ndim or arr1.dtype != arr2.dtype or not np.allclose(arr1, arr2):
                return key
        else:
            raise ValueError("Don't know what to do with type %s" % str(type(val1)))
    return None

def remove_items_from_list(list_, items_to_remove):
    """
    Remove items from a list and return the removed elements.

    Parameters
    ----------
    list_: list
        List containing items to remove
    items_to_remove: list
        List of items to remove

    Returns
    --------
    reduced_list: list
        List with removed items
    removed_items: dict
        Dictionary where the keys are the indices of removed items, and values are the items
    """
    removed_items = {}
    res = []
    for i, val in enumerate(list_):
        if val in items_to_remove:
            removed_items[i] = val
        else:
            res.append(val)
    return res, removed_items


def restore_items_in_list(list_, removed_items):
    """
    Undo the effect of the function `remove_items_from_list`

    Parameters
    ----------
    list_: list
        List where items were removed
    removed_items: dict
        Dictionary where the keys are the indices of removed items, and values are the items
    """
    for idx, val in removed_items.items():
        list_.insert(idx, val)


def check_supported(param_value, available, param_desc):
    if param_value not in available:
        raise ValueError("Unsupported %s '%s'. Available are: %s" % (param_desc, param_value, str(available)))


def check_supported_enum(param_value, enum_cls, param_desc):
    available = enum_cls.values()
    return check_supported(param_value, available, param_desc)


def check_shape(shape, expected_shape, name):
    if shape != expected_shape:
        raise ValueError(
            "Expected %s shape %s but got %s"
            % (name, str(expected_shape), str(shape))
        )


def copy_dict_items(dict_, keys):
    """
    Perform a shallow copy of a subset of a dictionary.
    The subset if done by a list of keys.
    """
    res = {
        key: dict_[key]
        for key in keys
    }
    return res


def recursive_copy_dict(dict_):
    """
    Perform a shallow copy of a dictionary of dictionaries.
    This is NOT a deep copy ! Only reference to objects are kept.
    """
    if not(isinstance(dict_, dict)):
        res = dict_
    else:
        res = {
            k: recursive_copy_dict(v)
            for k, v in dict_.items()
        }
    return res



def get_num_threads(n=None):
    """
    Get a number of threads (ex. to be used by fftw). If the argument is None, returns the total number of CPU threads.
    If the argument is negative, the total number of available threads plus this number is returned.

    """
    n_slurm_cores = os.environ.get("SLURM_CPUS_PER_TASK", None)
    if n_slurm_cores is not None:
        n_cores = int(n_slurm_cores)
    else:
        n_cores = cpu_count()
    if n is None:
        return n_cores
    if n < 0:
        return n_cores + n
    else:
        return min(n_cores, n)



class ArrayPlaceHolder:
    """
    Placeholder for array-like objects
    """

    def __init__(self, shape, dtype, name=None):
        self.shape = shape
        self.dtype = np.dtype(dtype)
        self.data = None
        self.name = name

    @property
    def size(self):
        return np.prod(self.shape)

    @property
    def nbytes(self):
        return self.size * self.dtype.itemsize

    def __repr__(self):
        return "ArrayPlaceHolder(shape=%s, dtype=%s)" % (self.shape, self.dtype)



# ------------------------------------------------------------------------------
# ------------------------ Image (move elsewhere ?) ----------------------------
# ------------------------------------------------------------------------------


def generate_coords(img_shp, center=None):
    l_r, l_c = float(img_shp[0]), float(img_shp[1])
    R, C = np.mgrid[:l_r, :l_c]  # np.indices is faster
    if center is None:
        center0, center1 = l_r / 2., l_c / 2.
    else:
        center0, center1 = center
    R += 0.5 - center0
    C += 0.5 - center1
    return R, C


def clip_circle(img, center=None, radius=None):
    R, C = generate_coords(img.shape, center)
    M = R**2+C**2
    res = np.zeros_like(img)
    res[M < radius ** 2] = img[M < radius ** 2]
    return res


def extend_image_onepixel(img):
    # extend of one pixel
    img2 = np.zeros((img.shape[0]+2, img.shape[1]+2), dtype=img.dtype)
    img2[0, 1:-1] = img[0]
    img2[-1, 1:-1] = img[-1]
    img2[1:-1, 0] = img[:, 0]
    img2[1:-1, -1] = img[:, -1]
    # middle
    img2[1: -1, 1:-1] = img
    # corners
    img2[0, 0] = img[0, 0]
    img2[-1, 0] = img[-1, 0]
    img2[0, -1] = img[0, -1]
    img2[-1, -1] = img[-1, -1]
    return img2


def median2(img):
    """
    3x3 median filter for 2D arrays, with "reflect" boundary mode.
    Roughly same speed as scipy median filter, but more memory demanding.
    """
    img2 = extend_image_onepixel(img)
    I = np.array([
        img2[0:-2, 0:-2],
        img2[0:-2, 1:-1],
        img2[0:-2, 2:],
        img2[1:-1, 0:-2],
        img2[1:-1, 1:-1],
        img2[1:-1, 2:],
        img2[2:, 0:-2],
        img2[2:, 1:-1],
        img2[2:, 2:]
    ])
    return np.median(I, axis=0)


# ------------------------------------------------------------------------------
# ---------------------------- Decorators --------------------------------------
# ------------------------------------------------------------------------------

_warnings = {}


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
            print("Warning: function %s is a work in progress, it is likely to change in the future")
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


def deprecated(msg, do_print=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            deprecation_warning(msg, do_print=do_print, func_name=func.__name__)
            res = func(*args, **kwargs)
            return res
        return wrapper
    return decorator


def deprecated_class(msg, do_print=False):
    def decorator(cls):
        class wrapper:
            def __init__(self, *args, **kwargs):
                deprecation_warning(msg, do_print=do_print, func_name=cls.__name__)
                self.wrapped = cls(*args, **kwargs)
            # This is so ugly :-(
            def __getattr__(self, name):
                return getattr(self.wrapped, name)
        return wrapper
    return decorator


def deprecation_warning(message, do_print=True, func_name=None):
    func_name = func_name or "None"
    if _warnings.get(func_name, False):
        return
    warnings.warn(message, DeprecationWarning)
    if do_print:
        print("Deprecation warning:", message)
    _warnings[func_name] = 1
