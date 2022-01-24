import numpy as np
from .utils import get_cuda_context, __has_pycuda__

if __has_pycuda__:
    import pycuda.driver as cuda
    import pycuda.gpuarray as garray
    dev_attrs = cuda.device_attribute

# NB: we must detach from a context before creating another context
class CudaProcessing:
    def __init__(self, device_id=None, ctx=None, stream=None, cleanup_at_exit=True):
        """
        Initialie a CudaProcessing instance.

        CudaProcessing is a base class for all CUDA-based processings.
        This class provides utilities for context/device management, and
        arrays allocation.

        Parameters
        ----------
        device_id: int, optional
            ID of the cuda device to use (those of the `nvidia-smi` command).
            Ignored if ctx is not None.
        ctx: pycuda.driver.Context, optional
            Existing context to use. If provided, do not create a new context.
        stream: pycudacuda.driver.Stream, optional
            Cuda stream. If not provided, will use the default stream
        cleanup_at_exit: bool, optional
            Whether to clean-up the context at exit.
            Ignored if ctx is not None.
        """
        if ctx is None:
            self.ctx = get_cuda_context(
                device_id=device_id,
                cleanup_at_exit=cleanup_at_exit
            )
        else:
            self.ctx = ctx
        self.stream = stream
        self.device = self.ctx.get_device()
        self.device_name = self.device.name()
        self.device_id = self.device.get_attribute(dev_attrs.MULTI_GPU_BOARD_GROUP_ID)
        self._allocated = {}


    def push_context(self):
        self.ctx.push()
        return self.ctx


    def pop_context(self):
        self.ctx.pop()


    def init_arrays_to_none(self, arrays_names):
        """
        Initialize arrays to None. After calling this method, the current instance will
        have self.array_name = None, and self._old_array_name = None.

        Parameters
        ----------
        arrays_names: list of str
            List of arrays names.
        """
        for array_name in arrays_names:
            setattr(self, array_name, None)
            setattr(self, "_old_" + array_name, None)
            self._allocated[array_name] = False


    def recover_arrays_references(self, arrays_names):
        """
        Performs self._array_name = self._old_array_name,
        for each array_name in arrays_names.

        Parameters
        ----------
        arrays_names: list of str
            List of array names
        """
        for array_name in arrays_names:
            old_arr = getattr(self, "_old_" + array_name)
            if old_arr is not None:
                setattr(self, array_name, old_arr)


    def allocate_array(self, array_name, shape, dtype=np.float32):
        """
        Allocate a GPU array on the current context/stream/device,
        and set 'self.array_name' to this array.

        Parameters
        ----------
        array_name: str
            Name of the array (for book-keeping)
        shape: tuple of int
            Array shape
        dtype: numpy.dtype, optional
            Data type. Default is float32.
        """
        if not self._allocated.get(array_name, False):
            new_gpuarr = garray.zeros(shape, dtype=dtype)
            setattr(self, array_name, new_gpuarr)
            self._allocated[array_name] = True
        return getattr(self, array_name)


    def set_array(self, array_name, array_ref, shape, dtype=np.float32):
        """
        Set the content of a device array.

        Parameters
        ----------
        array_name: str
            Array name. This method will look for self.array_name.
        array_ref: array (numpy or GPU array)
            Array containing the data to copy to 'array_name'.
        shape: tuple of int
            Array shape
        dtype: numpy.dtype, optional
            Data type. Default is float32.
        """
        if isinstance(array_ref, garray.GPUArray):
            current_arr = getattr(self, array_name)
            setattr(self, "_old_" + array_name, current_arr)
            setattr(self, array_name, array_ref)
        elif isinstance(array_ref, np.ndarray):
            self._allocate_array(array_name, shape, dtype=dtype)
            getattr(self, array_name).set(array_ref)
        else:
            raise ValueError("Expected numpy array or pycuda array")

    # COMPAT.
    _init_arrays_to_none = init_arrays_to_none
    _recover_arrays_references = recover_arrays_references
    _allocate_array = allocate_array
    _set_array = set_array
