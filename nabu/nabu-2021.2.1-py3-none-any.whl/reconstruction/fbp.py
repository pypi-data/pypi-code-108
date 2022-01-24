import numpy as np
from math import sqrt, pi

from ..utils import updiv, get_cuda_srcfile, _sizeof, nextpow2, convert_index, deprecation_warning
from ..cuda.utils import copy_array
from ..cuda.processing import CudaProcessing
from ..cuda.kernel import CudaKernel
from .filtering import SinoFilter
import pycuda.driver as cuda
from pycuda import gpuarray as garray


class Backprojector:
    """
    Cuda Backprojector.
    """

    default_padding_mode = "zeros"
    cuda_fname = "backproj.cu"
    cuda_kernel_name = "backproj"

    def __init__(
        self,
        sino_shape,
        slice_shape=None,
        angles=None,
        rot_center=None,
        padding_mode=None,
        filter_name=None,
        slice_roi=None,
        scale_factor=None,
        extra_options=None,
        cuda_options=None,
    ):
        """
        Initialize a Cuda Backprojector.

        Parameters
        -----------
        sino_shape: tuple
            Shape of the sinogram, in the form `(n_angles, detector_width)`
            (for backprojecting one sinogram) or `(n_sinos, n_angles, detector_width)`.
        slice_shape: int or tuple, optional
            Shape of the slice. By default, the slice shape is (n_x, n_x) where
            `n_x = detector_width`
        angles: array-like, optional
            Rotation anles in radians.
            By default, angles are equispaced between [0, pi[.
        rot_center: float, optional
            Rotation axis position. Default is `(detector_width - 1)/2.0`
        padding_mode: str, optional
            Padding mode when filtering the sinogram. Can be "zeros" (default) or "edges".
        filter_name: str, optional
            Name of the filter for filtered-backprojection.
        slice_roi: tuple, optional.
            Whether to backproject in a restricted area.
            If set, it must be in the form (start_x, end_x, start_y, end_y).
            `end_x` and `end_y` are non inclusive ! For example if the detector has
            2048 pixels horizontally, then you can choose `start_x=0` and `end_x=2048`.
            If one of the value is set to None, it is replaced with a default value
            (0 for start, n_x and n_y for end)
        scale_factor: float, optional
            Scaling factor for backprojection.
            For example, to get the linear absorption coefficient in 1/cm,
            this factor has to be set as the pixel size in cm.
            DEPRECATED - please use this parameter in "extra_options"
        extra_options: dict, optional
            Advanced extra options.
             See the "Extra options" section for more information.
        cuda_options: dict, optional
            Cuda options passed to the CudaProcessing class.

        Other parameters
        -----------------
        extra_options: dict, optional
            Dictionary with a set of advanced options. The default are the following:
                - "padding_mode": "zeros"
                   Padding mode when filtering the sinogram. Can be "zeros" or "edges".
                   DEPRECATED - please use "padding_mode" directly in parameters.
                - "axis_correction": None
                    Whether to set a correction for the rotation axis.
                    If set, this should be an array with as many elements as the number
                    of angles. This is useful when there is an horizontal displacement
                    of the rotation axis.
                - centered_axis: bool, optional
                    Whether to "center" the slice on the rotation axis position.
                    If set to True, then the reconstructed region is centered on the rotation axis.
                - scale_factor: float, optional
                    Scaling factor for backprojection.
                    For example, to get the linear absorption coefficient in 1/cm,
                    this factor has to be set as the pixel size in cm.
                - clip_outer_circle: False
                    Whether to set to zero the pixels outside the reconstruction mask
        """
        self.cuda_processing = CudaProcessing(**(cuda_options or {}))
        self._configure_extra_options(scale_factor, padding_mode, extra_options=extra_options)
        self._init_geometry(sino_shape, slice_shape, angles, rot_center, slice_roi)
        self._init_filter(filter_name)
        self._allocate_memory()
        self._compute_angles()
        self._compile_kernels()
        self._bind_textures()


    def _configure_extra_options(self, scale_factor, padding_mode, extra_options=None):
        extra_options = extra_options or {}
        if scale_factor is not None:
            deprecation_warning(
                "Please use the parameter 'scale_factor' in the 'extra_options' dict",
                do_print=True,
                func_name="fbp_scale_factor"
            )
        else:
            scale_factor = 1.
        if "padding_mode" in extra_options:
            deprecation_warning(
                "Please use 'padding_mode' directly in Backprojector arguments, not in 'extra_options'",
                do_print=True,
                func_name="fbp_padding_mode"
            )
        self._backproj_scale_factor = scale_factor
        self._axis_array = None
        self.extra_options = {
            "padding_mode": None,
            "axis_correction": None,
            "centered_axis": False,
            "clip_outer_circle": False,
        }
        self.extra_options.update(extra_options)
        self.padding_mode = padding_mode or self.extra_options["padding_mode"] or self.default_padding_mode
        self._axis_array = self.extra_options["axis_correction"]


    def _init_geometry(self, sino_shape, slice_shape, angles, rot_center, slice_roi):
        if slice_shape is not None and slice_roi is not None:
            raise ValueError("slice_shape and slice_roi cannot be used together")
        self.sino_shape = sino_shape
        if len(sino_shape) == 2:
            n_angles, dwidth = sino_shape
        else:
            raise ValueError("Expected 2D sinogram")
        self.dwidth = dwidth
        self._set_slice_shape(slice_shape)
        self.rot_center = rot_center or (self.dwidth - 1)/2.
        self.axis_pos = self.rot_center
        self._set_angles(angles, n_angles)
        self._set_slice_roi(slice_roi)
        #
        # offset = start - move
        # move = 0 if not(centered_axis) else start + (n-1)/2. - c
        if self.extra_options["centered_axis"]:
            self.offsets = {
                "x": round(self.rot_center - (self.n_x - 1)/2.),
                "y": round(self.rot_center - (self.n_y - 1)/2.)
            }
        #
        self._set_axis_corr()


    def _set_slice_shape(self, slice_shape):
        n_y = self.dwidth
        n_x = self.dwidth
        if slice_shape is not None:
            if np.isscalar(slice_shape):
                slice_shape = (slice_shape, slice_shape)
            n_y, n_x = slice_shape
        self.n_x = n_x
        self.n_y = n_y
        self.slice_shape = (n_y, n_x)


    def _set_angles(self, angles, n_angles):
        self.n_angles = n_angles
        if angles is None:
            angles = n_angles
        if np.isscalar(angles):
            angles = np.linspace(0, np.pi, angles, False)
        else:
            assert len(angles) == self.n_angles
        self.angles = angles


    def _set_slice_roi(self, slice_roi):
        self.offsets = {"x": 0, "y": 0}
        self.slice_roi = slice_roi
        if slice_roi is None:
            return
        start_x, end_x, start_y, end_y = slice_roi
        # convert negative indices
        dwidth = self.dwidth
        start_x = convert_index(start_x, dwidth, 0)
        start_y = convert_index(start_y, dwidth, 0)
        end_x = convert_index(end_x, dwidth, dwidth)
        end_y = convert_index(end_y, dwidth, dwidth)
        self.slice_shape = (end_y - start_y, end_x - start_x)
        self.n_x = self.slice_shape[-1]
        self.n_y = self.slice_shape[-2]
        self.offsets = {"x": start_x, "y": start_y}


    def _allocate_memory(self):
        self._d_sino_cua = cuda.np_to_array(np.zeros(self.sino_shape, "f"), "C")
        # 1D textures are not supported in pycuda
        self.h_msin = np.zeros((1, self.n_angles), "f")
        self.h_cos = np.zeros((1, self.n_angles), "f")
        self._d_sino = garray.zeros(self.sino_shape, "f")
        self.cuda_processing.init_arrays_to_none(["_d_slice"])


    def _compute_angles(self):
        self.h_cos[0] = np.cos(self.angles).astype("f")
        self.h_msin[0] = (-np.sin(self.angles)).astype("f")
        self._d_msin = garray.to_gpu(self.h_msin[0])
        self._d_cos = garray.to_gpu(self.h_cos[0])
        if self._axis_correction is not None:
            self._d_axcorr = garray.to_gpu(self._axis_correction)


    def _set_axis_corr(self):
        axcorr = self.extra_options["axis_correction"]
        self._axis_correction = axcorr
        if axcorr is None:
            return
        assert len(axcorr) == self.n_angles
        self._axis_correction = np.zeros((1, self.n_angles), dtype=np.float32)
        self._axis_correction[0, :] = axcorr[:]


    def _init_filter(self, filter_name):
        self.filter_name = filter_name
        self.sino_filter = SinoFilter(
            self.sino_shape,
            filter_name=self.filter_name,
            padding_mode=self.padding_mode,
            cuda_options={"ctx": self.cuda_processing.ctx},
        )


    def _get_kernel_signature(self):
        kern_full_sig = list("PiifiiiiPPPf")
        if self._axis_correction is None:
            kern_full_sig[10] = ""
        return "".join(kern_full_sig)


    def _get_kernel_options(self):
        tex_name = "tex_projections"
        sourcemodule_options = []
        # We use blocks of 16*16 (see why in kernel doc), and one thread
        # handles 2 pixels per dimension.
        block = (16, 16, 1)
        # The Cuda kernel is optimized for 16x16 threads blocks
        # If one of the dimensions is smaller than 16, it has to be addapted
        if self.n_x < 16 or self.n_y < 16:
            tpb_x = min(int(nextpow2(self.n_x)), 16)
            tpb_y = min(int(nextpow2(self.n_y)), 16)
            block = (tpb_x, tpb_y, 1)
            sourcemodule_options.append("-DSHARED_SIZE=%d" % (tpb_x * tpb_y))
        grid = (
            updiv(updiv(self.n_x, block[0]), 2),
            updiv(updiv(self.n_y, block[1]), 2)
        )
        if self.extra_options["clip_outer_circle"]:
            sourcemodule_options.append("-DCLIP_OUTER_CIRCLE")
        shared_size = int(np.prod(block)) * 2
        if self._axis_correction is not None:
            sourcemodule_options.append("-DDO_AXIS_CORRECTION")
            shared_size += int(np.prod(block))
        shared_size *= 4 # sizeof(float32)
        self._kernel_options = {
            "file_name": get_cuda_srcfile(self.cuda_fname),
            "kernel_name": self.cuda_kernel_name,
            "kernel_signature": self._get_kernel_signature(),
            "texture_name": tex_name,
            "sourcemodule_options": sourcemodule_options,
            "grid": grid,
            "block": block,
            "shared_size": shared_size
        }


    def _compile_kernels(self):
        self._get_kernel_options()
        kern_opts = self._kernel_options
        # Configure backprojector
        self.gpu_projector = CudaKernel(
            kern_opts["kernel_name"],
            filename=kern_opts["file_name"],
            options=kern_opts["sourcemodule_options"]
        )
        self.texref_proj = self.gpu_projector.module.get_texref(
            kern_opts["texture_name"]
        )
        self.texref_proj.set_filter_mode(cuda.filter_mode.LINEAR)
        self.gpu_projector.prepare(kern_opts["kernel_signature"], [self.texref_proj])
        # Prepare kernel arguments
        self.kern_proj_args = [
            None, # output d_slice holder
            self.n_angles,
            self.dwidth,
            self.axis_pos,
            self.n_x,
            self.n_y,
            self.offsets["x"],
            self.offsets["y"],
            self._d_cos,
            self._d_msin,
            self._backproj_scale_factor
        ]
        if self._axis_correction is not None:
            self.kern_proj_args.insert(-1, self._d_axcorr)
        self.kern_proj_kwargs = {
            "grid": kern_opts["grid"],
            "block": kern_opts["block"],
            "shared_size": kern_opts["shared_size"],
        }


    def _bind_textures(self):
        self.texref_proj.set_array(self._d_sino_cua)


    def _set_output(self, output, check=False):
        if output is None:
            self.cuda_processing.allocate_array("_d_slice", self.slice_shape, dtype=np.float32)
            return self.cuda_processing._d_slice
        if check:
            assert output.dtype == np.float32
            assert output.shape == self.slice_shape, "Expected output shape %s but got %s" % (self.slice_shape, output.shape)
        if isinstance(output, garray.GPUArray):
            return output.gpudata
        else: # pycuda.driver.DeviceAllocation ?
            return output


    def backproj(self, sino, output=None, do_checks=True):
        copy_array(self._d_sino_cua, sino, check=do_checks)
        d_slice = self._set_output(output, check=do_checks)
        self.kern_proj_args[0] = d_slice
        self.gpu_projector(
            *self.kern_proj_args,
            **self.kern_proj_kwargs
        )
        if output is not None:
            return output
        else:
            return self.cuda_processing._d_slice.get()


    def filtered_backprojection(self, sino, output=None):
        self.sino_filter(sino, output=self._d_sino)
        return self.backproj(self._d_sino, output=output)


    fbp = filtered_backprojection # shorthand


class PolarBackprojector(Backprojector):
    """
    Cuda Backprojector with output in polar coordinates.
    """

    cuda_fname = "backproj_polar.cu"
    cuda_kernel_name = "backproj_polar"


    # patch parent method: force slice_shape to (n_angles, n_x)
    def _set_angles(self, angles, n_angles):
        Backprojector._set_angles(self, angles, n_angles)
        self.slice_shape = (self.n_angles, self.n_x)

    # patch parent method:
    def _set_slice_roi(self, slice_roi):
        if slice_roi is not None:
            raise ValueError("slice_roi is not supported with this class")
        Backprojector._set_slice_roi(self, slice_roi)

    # patch parent method: don't do the 4X compute-workload optimization for this kernel
    def _get_kernel_options(self):
        Backprojector._get_kernel_options(self)
        block = self._kernel_options["block"]
        self._kernel_options["grid"] = (
            updiv(self.n_x, block[0]),
            updiv(self.n_y, block[1])
        )

    # patch parent method: update kernel args
    def _compile_kernels(self):
        n_y = self.n_y
        self.n_y = self.n_angles
        Backprojector._compile_kernels(self)
        self.n_y = n_y
