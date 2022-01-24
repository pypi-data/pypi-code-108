import numpy as np
import pycuda.gpuarray as garray
from ..cuda.kernel import CudaKernel
from ..cuda.processing import CudaProcessing
from .fbp import Backprojector
from .reconstructor import Reconstructor


class CudaReconstructor(Reconstructor):

    def __init__(
        self,
        shape,
        indices,
        axis="z",
        vol_type="sinograms",
        slices_roi=None,
        **backprojector_options
    ):
        Reconstructor.__init__(
            self, shape, indices, axis=axis, vol_type=vol_type, slices_roi=slices_roi
        )
        self._init_backprojector(**backprojector_options)


    def _init_backprojector(self, **backprojector_options):
        self.backprojector = Backprojector(
            self.sinos_shape[1:],
            slice_roi=self.backprojector_roi,
            **backprojector_options
        )


    def reconstruct(self, data, output=None):
        """
        Reconstruct from sinograms or projections.
        """
        self._check_data(data)
        B = self.backprojector
        if output is None:
            output = np.zeros(self.output_shape, "f")
            new_output = True
        else:
            assert output.shape == output_shape, str("Expected output_shape = %s, got %s" % (str(output_shape), str(output.shape)))
            assert output.dtype == np.float32
            new_output = False

        def reconstruct_fbp(data, output, i, i0):
            if self.vol_type == "sinograms":
                current_sino = data[i]
            else:
                current_sino = data[:, i, :]
            if new_output:
                output[i0] = B.fbp(current_sino)
            else:
                B.fbp(current_sino, output=output[i0])

        for i0, i in enumerate(self._z_indices):
            reconstruct_fbp(data, output, i, i0)
        return output

