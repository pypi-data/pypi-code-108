from ..utils import updiv
import pycuda.gpuarray as garray
from pycuda.compiler import SourceModule

class CudaKernel(object):
    """
    Helper class that wraps CUDA kernel through pycuda SourceModule.

    Parameters
    -----------
    kernel_name: str
        Name of the CUDA kernel.
    filename: str, optional
        Path to the file name containing kernels definitions
    src: str, optional
        Source code of kernels definitions
    signature: str, optional
        Signature of kernel function. If provided, pycuda will not guess the types
        of kernel arguments, making the calls slightly faster.
        For example, a function acting on two pointers, an integer and a float32
        has the signature "PPif".
    texrefs: list, optional
        List of texture references, if any
    automation_params: dict, optional
        Automation parameters, see below
    sourcemodule_kwargs: optional
        Extra arguments to provide to pycuda.compiler.SourceModule(),

    Automation parameters
    ----------------------
    automation_params is a dictionary with the following keys and default values.
        guess_block: bool (True)
            If block is not specified during calls, choose a block size based on
            the size/dimensions of the first array.
            Mind that it is unlikely to be the optimal choice.
        guess_grid: bool (True):
            If the grid size is not specified during calls, choose a grid size
            based on the size of the first array.
        follow_gpuarr_ptr: bool (True)
            specify gpuarray.gpudata for all GPUArrays. Otherwise, raise an error.
    """
    def __init__(
        self,
        kernel_name,
        filename=None,
        src=None,
        signature=None,
        texrefs=[],
        automation_params=None,
        **sourcemodule_kwargs
    ):
        self.check_filename_src(filename, src)
        self.set_automation_params(automation_params)
        self.compile_kernel_source(kernel_name, sourcemodule_kwargs)
        self.prepare(signature, texrefs)


    def check_filename_src(self, filename, src):
        err_msg = "Please provide either filename or src"
        if filename is None and src is None:
            raise ValueError(err_msg)
        if filename is not None and src is not None:
            raise ValueError(err_msg)
        if filename is not None:
            with open(filename) as fid:
                src = fid.read()
        self.filename = filename
        self.src = src


    def set_automation_params(self, automation_params):
        self.automation_params = {
            "guess_block": True,
            "guess_grid": True,
            "follow_gpuarr_ptr": True,
        }
        automation_params = automation_params or {}
        self.automation_params.update(automation_params)


    def compile_kernel_source(self, kernel_name, sourcemodule_kwargs):
        self.sourcemodule_kwargs = sourcemodule_kwargs
        self.kernel_name = kernel_name
        self.module = SourceModule(self.src, **self.sourcemodule_kwargs)
        self.func = self.module.get_function(kernel_name)


    def prepare(self, kernel_signature, texrefs):
        self.prepared = False
        self.kernel_signature = kernel_signature
        self.texrefs = texrefs
        if kernel_signature is not None:
            self.func.prepare(self.kernel_signature, texrefs=texrefs)
            self.prepared = True


    @staticmethod
    def guess_grid_size(shape, block_size):
        # python: (z, y, x) -> cuda: (x, y, z)
        res = tuple(map(lambda x : updiv(x[0], x[1]), zip(shape[::-1], block_size)))
        if len(res) == 2:
            res += (1,)
        return res


    @staticmethod
    def guess_block_size(shape):
        """
        Guess a block size based on the shape of an array.
        """
        ndim = len(shape)
        if ndim == 1:
            return (128, 1, 1)
        if ndim == 2:
            return (32, 32, 1)
        else:
            return (16, 8, 8)


    def get_block_grid(self, *args, **kwargs):
        block = None
        grid = None
        if ("block" not in kwargs) or (kwargs["block"] is None):
            if self.automation_params["guess_block"]:
                block = self.guess_block_size(args[0].shape)
            else:
                raise ValueError("Please provide block size")
        else:
            block = kwargs["block"]
        if ("grid" not in kwargs) or (kwargs["grid"] is None):
            if self.automation_params["guess_grid"]:
                grid = self.guess_grid_size(args[0].shape, block)
            else:
                raise ValueError("Please provide block grid")
        else:
            grid = kwargs["grid"]
        self.last_block_size = block
        self.last_grid_size = grid
        return block, grid


    def follow_gpu_arr(self, args):
        args = list(args)
        # Replace GPUArray with GPUArray.gpudata
        for i, arg in enumerate(args):
            if isinstance(arg, garray.GPUArray):
                args[i] = arg.gpudata
        return tuple(args)


    def get_last_kernel_time(self):
        """
        Return the execution time (in seconds) of the last called kernel.
        The last called kernel should have been called with time_kernel=True.
        """
        if self.last_kernel_time is not None:
            return self.last_kernel_time()
        else:
            return None


    def call(self, *args, **kwargs):
        block, grid = self.get_block_grid(*args, **kwargs)
        # pycuda crashes when any element of block/grid is not a python int (ex. numpy.int64).
        # A weird behavior once observed is "data.shape" returning (np.int64, int, int) (!).
        # Ensure that everything is a python integer.
        block = tuple(int(x) for x in block)
        grid = tuple(int(x) for x in grid)
        #
        args = self.follow_gpu_arr(args)

        if self.prepared:
            func_call = self.func.prepared_call
            if "time_kernel" in kwargs:
                func_call = self.func.prepared_timed_call
                kwargs.pop("time_kernel")
            if "block" in kwargs:
                kwargs.pop("block")
            if "grid" in kwargs:
                kwargs.pop("grid")
            t = func_call(grid, block, *args, **kwargs)
        else:
            kwargs["block"] = block
            kwargs["grid"] = grid
            t = self.func(*args, **kwargs)
        #~ return t
        # TODO return event like in OpenCL ?
        self.last_kernel_time = t # list ?




    __call__ = call
