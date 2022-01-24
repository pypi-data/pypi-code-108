import atexit
from math import ceil
import numpy as np
from ..resources.gpu import GPUDescription
try:
    import pycuda
    import pycuda.driver as cuda
    from pycuda import gpuarray as garray
    from pycuda.tools import make_default_context
    from pycuda.tools import clear_context_caches
    __has_pycuda__ = True
    __pycuda_error_msg__ = None
    if pycuda.VERSION[0] < 2020:
        print("Error: need pycuda >= 2020.1")
        __has_pycuda__ = False
except ImportError as err:
    __has_pycuda__ = False
    __pycuda_error_msg__ = str(err)
try:
    import skcuda
    __has_cufft__ = True
except ImportError:
    __has_cufft__ = False


def get_cuda_context(device_id=None, cleanup_at_exit=True):
    """
    Create or get a CUDA context.
    """
    current_ctx = cuda.Context.get_current()
    # If a context already exists, use this one
    # TODO what if the device used is different from device_id ?
    if current_ctx is not None:
        return current_ctx
    # Otherwise create a new context
    cuda.init()

    if device_id is None:
        device_id = 0
    # Use the Context obtained by retaining the device's primary context,
    # which is the one used by the CUDA runtime API (ex. scikit-cuda).
    # Unlike Context.make_context(), the newly-created context is not made current.
    context = cuda.Device(device_id).retain_primary_context()
    context.push()
    # Register a clean-up function at exit
    def _finish_up(context):
        if context is not None:
            context.pop()
            context = None
        clear_context_caches()
    if cleanup_at_exit:
        atexit.register(_finish_up, context)
    return context


def count_cuda_devices():
    if cuda.Context.get_current() is None:
        cuda.init()
    return cuda.Device.count()


def get_gpu_memory(device_id):
    """
    Return the total memory (in GigaBytes) of a device.
    """
    cuda.init()
    return cuda.Device(device_id).total_memory()/1e9


def is_gpu_usable():
    """
    Test whether at least one Nvidia GPU is available.
    """
    try:
        n_gpus = count_cuda_devices()
    except Exception as exc:
        # Fragile
        if exc.__str__() != "cuInit failed: no CUDA-capable device is detected":
            raise
        n_gpus = 0
    res = (n_gpus > 0)
    return res


def detect_cuda_gpus():
    """
    Detect the available Nvidia CUDA GPUs on the current host.

    Returns
    --------
    gpus: dict
        Dictionary where the key is the GPU ID, and the value is a `pycuda.driver.Device` object.
    error_msg: str
        In the case where there is an error, the message is returned in this item.
        Otherwise, it is a None object.
    """
    gpus = {}
    error_msg = None
    if not(__has_pycuda__):
        return {}, __pycuda_error_msg__
    try:
        cuda.init()
    except Exception as exc:
        error_msg = str(exc)
    if error_msg is not None:
        return {}, error_msg
    try:
        n_gpus = cuda.Device.count()
    except Exception as exc:
        error_msg = str(exc)
    if error_msg is not None:
        return {}, error_msg
    for i in range(n_gpus):
        gpus[i] = cuda.Device(i)
    return gpus, None


def collect_cuda_gpus():
    """
    Return a dictionary of GPU ids and brief description of each CUDA-compatible
    GPU with a few fields.
    """
    gpus, error_msg = detect_cuda_gpus()
    if error_msg is not None:
        return None
    cuda_gpus = {}
    for gpu_id, gpu in gpus.items():
        cuda_gpus[gpu_id] = GPUDescription(gpu).get_dict()
    return cuda_gpus


"""
pycuda/driver.py
    np.complex64: SIGNED_INT32, num_channels = 2
    np.float64:  SIGNED_INT32, num_channels = 2
    np.complex128: array_format.SIGNED_INT32, num_channels = 4

double precision: pycuda-helpers.hpp:
  typedef float fp_tex_float;   // --> float32
  typedef int2 fp_tex_double;   // --> float64
  typedef uint2 fp_tex_cfloat;  // --> complex64
  typedef int4 fp_tex_cdouble;  // --> complex128
"""
def cuarray_format_to_dtype(cuarr_fmt):
    # reverse of cuda.dtype_to_array_format
    fmt = cuda.array_format
    mapping = {
        fmt.UNSIGNED_INT8: np.uint8,
        fmt.UNSIGNED_INT16: np.uint16,
        fmt.UNSIGNED_INT32: np.uint32,
        fmt.SIGNED_INT8: np.int8,
        fmt.SIGNED_INT16: np.int16,
        fmt.SIGNED_INT32: np.int32,
        fmt.FLOAT: np.float32,
    }
    if cuarr_fmt not in mapping:
        raise TypeError("Unknown format %s" % cuarr_fmt)
    return mapping[cuarr_fmt]


def cuarray_shape_dtype(cuarray):
    desc = cuarray.get_descriptor_3d()
    shape = (desc.height, desc.width)
    if desc.depth > 0:
        shape = (desc.depth, ) + shape
    dtype = cuarray_format_to_dtype(desc.format)
    return shape, dtype


def get_shape_dtype(arr):
    if isinstance(arr, garray.GPUArray) or isinstance(arr, np.ndarray):
        return arr.shape, arr.dtype
    elif isinstance(arr, cuda.Array):
        return cuarray_shape_dtype(arr)
    else:
        raise ValueError("Unknown array type %s" % str(type(arr)))


def copy_array(dst, src, check=False, src_dtype=None):
    """
    Copy a source array to a destination array.
    Source and destination can be either numpy.ndarray, pycuda.Driver.Array,
    or pycuda.gpuarray.GPUArray.

    Parameters
    -----------
    dst: pycuda.driver.Array or pycuda.gpuarray.GPUArray or numpy.ndarray
        Destination array. Its content will be overwritten by copy.
    src: pycuda.driver.Array or pycuda.gpuarray.GPUArray or numpy.ndarray
        Source array.
    check: bool, optional
        Whether to check src and dst shape and data type.
    """

    shape_src, dtype_src = get_shape_dtype(src)
    shape_dst, dtype_dst = get_shape_dtype(dst)
    dtype_src = src_dtype or dtype_src
    if check:
        if shape_src != shape_dst:
            raise ValueError("shape_src != shape_dst : have %s and %s" % (str(shape_src), str(shape_dst)))
        if dtype_src != dtype_dst:
            raise ValueError("dtype_src != dtype_dst : have %s and %s" % (str(dtype_src), str(dtype_dst)))
    if len(shape_src) == 2:
        copy = cuda.Memcpy2D()
        h, w = shape_src
    elif len(shape_src) == 3:
        copy = cuda.Memcpy3D()
        d, h, w = shape_src
        copy.depth = d
    else:
        raise ValueError("Expected arrays with 2 or 3 dimensions")

    if isinstance(src, cuda.Array):
        copy.set_src_array(src)
    elif isinstance(src, garray.GPUArray):
        copy.set_src_device(src.gpudata)
    else: # numpy
        copy.set_src_host(src)

    if isinstance(dst, cuda.Array):
        copy.set_dst_array(dst)
    elif isinstance(dst, garray.GPUArray):
        copy.set_dst_device(dst.gpudata)
    else: # numpy
        copy.set_dst_host(dst)

    copy.width_in_bytes = copy.dst_pitch = w * np.dtype(dtype_src).itemsize
    copy.dst_height = copy.height = h
    # ??
    if len(shape_src) == 2:
        copy(True)
    else:
        copy()
    ###



def copy_big_gpuarray(dst, src, itemsize=4, checks=False):
    """
    Copy a big `pycuda.gpuarray.GPUArray` into another.
    Transactions of more than 2**32 -1 octets fail, so are doing several
    partial copies of smaller arrays.
    """
    d2h = isinstance(dst, np.ndarray)
    if checks:
        assert dst.dtype == src.dtype
        assert dst.shape == src.shape
    limit = 2**32 - 1
    if np.prod(dst.shape) * itemsize < limit:
        if d2h:
            src.get(ary=dst)
        else:
            dst[:] = src[:]
        return
    def get_shape2(shape):
        shape2 = list(shape)
        while np.prod(shape2)*4 > limit:
            shape2[0] //= 2
        return tuple(shape2)
    shape2 = get_shape2(dst.shape)
    nz0 = dst.shape[0]
    nz = shape2[0]
    n_transfers = ceil(nz0 / nz)
    for i in range(n_transfers):
        zmax = min((i+1)*nz, nz0)
        if d2h:
            src[i*nz:zmax].get(ary=dst[i*nz:zmax])
        else:
            dst[i*nz:zmax] = src[i*nz:zmax]


def replace_array_memory(arr, new_shape):
    """
    Replace the underlying buffer data of a  `pycuda.gpuarray.GPUArray`.
    This function is dangerous !
    It should merely be used to clear memory, the array should not be used afterwise.
    """
    arr.gpudata.free()
    arr.gpudata = arr.allocator(int(np.prod(new_shape) * arr.dtype.itemsize))
    arr.shape = new_shape
    # TODO re-compute strides
    return arr

