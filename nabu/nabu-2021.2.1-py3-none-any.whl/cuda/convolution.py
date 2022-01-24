import numpy as np
from os.path import dirname
from silx.image.utils import gaussian_kernel
from ..utils import updiv, get_cuda_srcfile
from ..cuda.utils import __has_pycuda__
from ..misc.utils import ConvolutionInfos
from .processing import CudaProcessing

if __has_pycuda__:
    import pycuda.gpuarray as garray
    from pycuda.compiler import SourceModule


class Convolution:
    """
    A class for performing convolution on GPU with CUDA, but without using
    textures (unlike for example in ``silx.opencl.convolution``)
    """

    def __init__(self, shape, kernel, axes=None, mode=None, extra_options=None,
                cuda_options=None):
        """
        Constructor of Cuda Convolution.

        Parameters
        -----------
        shape: tuple
            Shape of the array.
        kernel: array-like
            Convolution kernel (1D, 2D or 3D).
        axes: tuple, optional
            Axes along which the convolution is performed,
            for batched convolutions.
        mode: str, optional
            Boundary handling mode. Available modes are:
               - "reflect": cba|abcd|dcb
               - "nearest": aaa|abcd|ddd
               - "wrap": bcd|abcd|abc
               - "constant": 000|abcd|000

            Default is "reflect".
        extra_options: dict, optional
            Advanced options (dict). Current options are:
               - "allocate_input_array": True
               - "allocate_output_array": True
               - "allocate_tmp_array": True
               - "sourcemodule_kwargs": {}
               - "batch_along_flat_dims": True
        """
        self.cuda = CudaProcessing(**(cuda_options or {}))
        self._configure_extra_options(extra_options)
        self._determine_use_case(shape, kernel, axes)
        self._allocate_memory(mode)
        self._init_kernels()

    def _configure_extra_options(self, extra_options):
        self.extra_options = {
            "allocate_input_array": True,
            "allocate_output_array": True,
            "allocate_tmp_array": True,
            "sourcemodule_kwargs": {},
            "batch_along_flat_dims": True,
        }
        extra_opts = extra_options or {}
        self.extra_options.update(extra_opts)
        self.sourcemodule_kwargs = self.extra_options["sourcemodule_kwargs"]

    def _get_dimensions(self, shape, kernel):
        self.shape = shape
        self.data_ndim = self._check_dimensions(shape=shape, name="Data")
        self.kernel_ndim = self._check_dimensions(arr=kernel, name="Kernel")
        Nx = shape[-1]
        if self.data_ndim >= 2:
            Ny = shape[-2]
        else:
            Ny = 1
        if self.data_ndim >= 3:
            Nz = shape[-3]
        else:
            Nz = 1
        self.Nx = np.int32(Nx)
        self.Ny = np.int32(Ny)
        self.Nz = np.int32(Nz)

    def _determine_use_case(self, shape, kernel, axes):
        """
        Determine the convolution use case from the input/kernel shape, and axes.
        """
        self._get_dimensions(shape, kernel)
        if self.kernel_ndim > self.data_ndim:
            raise ValueError("Kernel dimensions cannot exceed data dimensions")
        data_ndim = self.data_ndim
        kernel_ndim = self.kernel_ndim
        self.kernel = kernel.astype("f")

        convol_infos = ConvolutionInfos()
        k = (data_ndim, kernel_ndim)
        if k not in convol_infos.use_cases:
            raise ValueError(
                "Cannot find a use case for data ndim = %d and kernel ndim = %d"
                % (data_ndim, kernel_ndim)
            )
        possible_use_cases = convol_infos.use_cases[k]

        # If some dimensions are "flat", make a batched convolution along them
        # Ex. data_dim = (1, Nx) -> batched 1D convolution
        if self.extra_options["batch_along_flat_dims"] and (1 in self.shape):
            axes = tuple(
                [curr_dim for numels, curr_dim in zip(self.shape, range(len(self.shape))) if numels != 1]
            )
        #
        self.use_case_name = None
        for uc_name, uc_params in possible_use_cases.items():
            if axes in convol_infos.allowed_axes[uc_name]:
                self.use_case_name = uc_name
                self.use_case_desc = uc_params["name"]
                self.use_case_kernels = uc_params["kernels"].copy()
        if self.use_case_name is None:
            raise ValueError(
                "Cannot find a use case for data ndim = %d, kernel ndim = %d and axes=%s"
                % (data_ndim, kernel_ndim, str(axes))
            )
        # TODO implement this use case
        if self.use_case_name == "batched_separable_2D_1D_3D":
            raise NotImplementedError(
                "The use case %s is not implemented"
                % self.use_case_name
            )
        #
        self.axes = axes
        # Replace "axes=None" with an actual value (except for ND-ND)
        allowed_axes = convol_infos.allowed_axes[self.use_case_name]
        if len(allowed_axes) > 1:
            # The default choice might impact perfs
            self.axes = allowed_axes[0] or allowed_axes[1]
        self.separable = self.use_case_name.startswith("separable")
        self.batched = self.use_case_name.startswith("batched")

    def _allocate_memory(self, mode):
        self.mode = mode or "reflect"
        # The current implementation does not support kernel size bigger than data size,
        # except for mode="nearest"
        for i, dim_size in enumerate(self.shape):
            if min(self.kernel.shape) > dim_size and i in self.axes:
                print(
                    "Warning: kernel support is too large for data dimension %d (%d). Forcing convolution mode to 'nearest'"
                    % (i, dim_size)
                )
                self.mode = "nearest"
        #
        option_array_names = {
            "allocate_input_array": "data_in",
            "allocate_output_array": "data_out",
            "allocate_tmp_array": "data_tmp",
        }
        # Nonseparable transforms do not need tmp array
        if not(self.separable):
            self.extra_options["allocate_tmp_array"] = False
        # Allocate arrays
        for option_name, array_name in option_array_names.items():
            if self.extra_options[option_name]:
                value = garray.zeros(self.shape, np.float32)
            else:
                value = None
            setattr(self, array_name, value)

        if isinstance(self.kernel, np.ndarray):
            self.d_kernel = garray.to_gpu(self.kernel)
        else:
            if not(isinstance(self.kernel, garray.GPUArray)):
                raise ValueError("kernel must be either numpy array or pycuda array")
            self.d_kernel = self.kernel
        self._old_input_ref = None
        self._old_output_ref = None
        self._c_modes_mapping = {
            "periodic": 2,
            "wrap": 2,
            "nearest": 1,
            "replicate": 1,
            "reflect": 0,
            "constant": 3,
        }
        mp = self._c_modes_mapping
        if self.mode.lower() not in mp:
            raise ValueError(
                """
                Mode %s is not available. Available modes are:
                %s
                """
                % (self.mode, str(mp.keys()))
            )
        if self.mode.lower() == "constant":
            raise NotImplementedError(
                "mode='constant' is not implemented yet"
            )
        self._c_conv_mode = mp[self.mode]

    def _init_kernels(self):
        if self.kernel_ndim > 1:
            if np.abs(np.diff(self.kernel.shape)).max() > 0:
                raise NotImplementedError(
                    "Non-separable convolution with non-square kernels is not implemented yet"
                )
        # Compile source module
        compile_options = [str("-DUSED_CONV_MODE=%d" % self._c_conv_mode)]
        fname = get_cuda_srcfile("convolution.cu")
        nabu_cuda_dir = dirname(fname)
        include_dirs = [nabu_cuda_dir]
        self.sourcemodule_kwargs["options"] = compile_options
        self.sourcemodule_kwargs["include_dirs"] = include_dirs
        with open(fname) as fid:
            cuda_src = fid.read()
        self._module = SourceModule(
            cuda_src,
            **self.sourcemodule_kwargs
        )
        # Blocks, grid
        self._block_size = {1: (32, 1, 1), 2: (32, 32, 1), 3: (16, 8, 8)}[self.data_ndim] # TODO tune
        self._n_blocks = tuple([int(updiv(a, b)) for a, b in zip(self.shape[::-1], self._block_size)])
        # Prepare cuda kernel calls
        self._cudakernel_signature = {
            1: "PPPiiii",
            2: "PPPiiiii",
            3: "PPPiiiiii",
        }[self.kernel_ndim]
        self.cuda_kernels = {}
        for axis, kern_name in enumerate(self.use_case_kernels):
            self.cuda_kernels[axis] = self._module.get_function(kern_name)
            self.cuda_kernels[axis].prepare(self._cudakernel_signature)

        # Cuda kernel arguments
        kernel_args = [
            self._n_blocks,
            self._block_size,
            None,
            None,
            self.d_kernel.gpudata,
            np.int32(self.kernel.shape[0]),
            self.Nx, self.Ny, self.Nz
        ]
        if self.kernel_ndim == 2:
            kernel_args.insert(5, np.int32(self.kernel.shape[1]))
        if self.kernel_ndim == 3:
            kernel_args.insert(5, np.int32(self.kernel.shape[2]))
            kernel_args.insert(6, np.int32(self.kernel.shape[1]))
        self.kernel_args = tuple(kernel_args)
        # If self.data_tmp is allocated, separable transforms can be performed
        # by a series of batched transforms, without any copy, by swapping refs.
        self.swap_pattern = None
        if self.separable:
            if self.data_tmp is not None:
                self.swap_pattern = {
                    2: [
                        ("data_in", "data_tmp"),
                        ("data_tmp", "data_out")
                    ],
                    3: [
                        ("data_in", "data_out"),
                        ("data_out", "data_tmp"),
                        ("data_tmp", "data_out"),
                    ],
                }
            else:
                raise NotImplementedError("For now, data_tmp has to be allocated")

    def _get_swapped_arrays(self, i):
        """
        Get the input and output arrays to use when using a "swap pattern".
        Swapping refs enables to avoid copies between temp. array and output.
        For example, a separable 2D->1D convolution on 2D data reads:
          data_tmp = convol(data_input, kernel, axis=1) # step i=0
          data_out = convol(data_tmp, kernel, axis=0) # step i=1

        :param i: current step number of the separable convolution
        """
        n_batchs = len(self.axes)
        in_ref, out_ref = self.swap_pattern[n_batchs][i]
        d_in = getattr(self, in_ref)
        d_out = getattr(self, out_ref)
        return d_in, d_out

    def _configure_kernel_args(self, cuda_kernel_args, input_ref, output_ref):
        # TODO more elegant
        if isinstance(input_ref, garray.GPUArray):
            input_ref = input_ref.gpudata
        if isinstance(output_ref, garray.GPUArray):
            output_ref = output_ref.gpudata
        if input_ref is not None or output_ref is not None:
            cuda_kernel_args = list(cuda_kernel_args)
            if input_ref is not None:
                cuda_kernel_args[2] = input_ref
            if output_ref is not None:
                cuda_kernel_args[3] = output_ref
            cuda_kernel_args = tuple(cuda_kernel_args)
        return cuda_kernel_args

    @staticmethod
    def _check_dimensions(arr=None, shape=None, name="", dim_min=1, dim_max=3):
        if shape is not None:
            ndim = len(shape)
        elif arr is not None:
            ndim = arr.ndim
        else:
            raise ValueError("Please provide either arr= or shape=")
        if ndim < dim_min or ndim > dim_max:
            raise ValueError("%s dimensions should be between %d and %d"
                % (name, dim_min, dim_max)
            )
        return ndim

    def _check_array(self, arr):
        if not(isinstance(arr, garray.GPUArray) or isinstance(arr, np.ndarray)):
            raise TypeError("Expected either pycuda.gpuarray or numpy.ndarray")
        if arr.dtype != np.float32:
            raise TypeError("Data must be float32")
        if arr.shape != self.shape:
            raise ValueError("Expected data shape = %s" % str(self.shape))

    def _set_arrays(self, array, output=None):
        # Either copy H->D or update references.
        if isinstance(array, np.ndarray):
            self.data_in[:] = array[:]
        else:
            self._old_input_ref = self.data_in
            self.data_in = array
        data_in_ref = self.data_in
        if output is not None:
            if not(isinstance(output, np.ndarray)):
                self._old_output_ref = self.data_out
                self.data_out = output
        # Update Cuda kernel arguments with new array references
        self.kernel_args = self._configure_kernel_args(
            self.kernel_args,
            data_in_ref,
            self.data_out
        )

    def _separable_convolution(self):
        assert len(self.axes) == len(self.use_case_kernels)
        # Separable: one kernel call per data dimension
        for i, axis in enumerate(self.axes):
            in_ref, out_ref = self._get_swapped_arrays(i)
            self._batched_convolution(axis, input_ref=in_ref, output_ref=out_ref)

    def _batched_convolution(self, axis, input_ref=None, output_ref=None):
        # Batched: one kernel call in total
        cuda_kernel = self.cuda_kernels[axis]
        cuda_kernel_args = self._configure_kernel_args(
            self.kernel_args,
            input_ref,
            output_ref
        )
        ev = cuda_kernel.prepared_call(*cuda_kernel_args)


    def _nd_convolution(self):
        assert len(self.use_case_kernels) == 1
        cuda_kernel = self._module.get_function(self.use_case_kernels[0])
        ev = cuda_kernel.prepared_call(*self.kernel_args)

    def _recover_arrays_references(self):
        if self._old_input_ref is not None:
            self.data_in = self._old_input_ref
            self._old_input_ref = None
        if self._old_output_ref is not None:
            self.data_out = self._old_output_ref
            self._old_output_ref = None
        self.kernel_args = self._configure_kernel_args(
            self.kernel_args,
            self.data_in,
            self.data_out
        )

    def _get_output(self, output):
        if output is None:
            res = self.data_out.get()
        else:
            res = output
            if isinstance(output, np.ndarray):
                output[:] = self.data_out[:]
        self._recover_arrays_references()
        return res

    def convolve(self, array, output=None):
        """
        Convolve an array with the class kernel.

        :param array: Input array. Can be numpy.ndarray or pycuda.gpuarray.GPUArray.
        :param output: Output array. Can be numpy.ndarray or pycuda.gpuarray.GPUArray.
        """
        self._check_array(array)
        self._set_arrays(array, output=output)
        if self.axes is not None:
            if self.separable:
                self._separable_convolution()
            elif self.batched:
                assert len(self.axes) == 1
                self._batched_convolution(self.axes[0])
            # else: ND-ND convol
        else:
            # ND-ND convol
            self._nd_convolution()

        res = self._get_output(output)
        return res

    __call__ = convolve
