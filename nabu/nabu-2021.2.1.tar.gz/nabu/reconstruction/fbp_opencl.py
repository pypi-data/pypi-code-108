import numpy as np
from silx.opencl.backprojection import Backprojection
from ..utils import deprecation_warning

# Compatibility layer Nabu/silx
class Backprojector:
    def __init__(
        self,
        sino_shape,
        slice_shape=None,
        angles=None,
        rot_center=None,
        filter_name=None,
        padding_mode=None,
        slice_roi=None,
        scale_factor=None,
        ctx=None,
        devicetype="all",
        platformid=None,
        deviceid=None,
        profile=False,
        extra_options=None,
    ):
        if slice_roi:
            raise ValueError("Not implemented yet in the OpenCL back-end")

        self._configure_extra_options(extra_options, padding_mode)
        self._get_scale_factor(scale_factor)

        self.backprojector = Backprojection(
            sino_shape,
            slice_shape=slice_shape,
            axis_position=rot_center, #
            angles=angles,
            filter_name=filter_name,
            ctx=ctx,
            devicetype=devicetype,
            platformid=platformid,
            deviceid=deviceid,
            profile=profile,
            extra_options=self._silx_fbp_extra_options,
        )


    def _configure_extra_options(self, extra_options, padding_mode):
        self.extra_options = extra_options or {}
        self._silx_fbp_extra_options = None
        if "padding_mode" in self.extra_options:
            deprecation_warning(
                "Please use 'padding_mode' directly in Backprojector arguments, not in 'extra_options'",
                do_print=True,
                func_name="ocl_fbp_padding_mode"
            )
        if "clip_outer_circle" in self.extra_options or "center_slice" in self.extra_options:
            raise NotImplementedError()
        if padding_mode is not None:
            self._silx_fbp_extra_options = self._silx_fbp_extra_options or {}
            self._silx_fbp_extra_options["padding_mode"] = padding_mode


    def _get_scale_factor(self, scale_factor):
        if scale_factor is not None:
            deprecation_warning(
                "Please use the 'scale_factor' parameter in extra_options",
                func_name="ocl_fbp_scale_factor"
            )
        self.scale_factor = scale_factor or self.extra_options.get("scale_factor", None)


    # scale_factor is not implemented in the opencl code
    def _fbp_with_scale_factor(self, sino, output=None):
        return self.backprojector.filtered_backprojection(sino * self.scale_factor, output=output)

    def _fbp(self, sino, output=None):
        return self.backprojector.filtered_backprojection(sino, output=output)

    def filtered_backprojection(self, sino, output=None):
        input_sino = sino
        # TODO scale_factor is not implemented in the silx opencl code
        # This makes a copy of the input array
        if self.scale_factor is not None:
            input_sino = sino * self.scale_factor
        #
        if output is None or isinstance(output, np.ndarray):
            res = self.backprojector.filtered_backprojection(input_sino)
            if output is not None:
                output[:] = res[:]
                return output
            return res
        else: # assuming pyopencl array
            return self.backprojector.filtered_backprojection(input_sino, output=output)

    fbp = filtered_backprojection


