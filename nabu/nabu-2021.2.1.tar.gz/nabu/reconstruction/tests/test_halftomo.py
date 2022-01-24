import os
import numpy as np
import pytest
import h5py
try:
    from algotom.prep.conversion import convert_sinogram_360_to_180
    __has_algotom__ = True
except ImportError:
    __has_algotom__ = False
from nabu.testutils import compare_arrays, utilstest
from nabu.reconstruction.sinogram import SinoBuilder
from nabu.cuda.utils import __has_pycuda__

if __has_pycuda__:
    from nabu.cuda.utils import get_cuda_context
    import pycuda.gpuarray as garray
    from nabu.reconstruction.sinogram_cuda import CudaSinoBuilder


@pytest.fixture(scope="class")
def bootstrap(request):
    cls = request.cls
    sino, sino_ref, cor = get_data_h5("halftomo_new.h5")
    cls.sino = sino
    cls.radios = convert_sino_to_radios_stack(sino)
    cls.sino_ref = sino_ref
    cls.rot_center = cor
    cls.tol = 5e-3
    if __has_pycuda__:
        cls.ctx = get_cuda_context()


def convert_sino_to_radios_stack(sino):
    return np.moveaxis(np.tile(sino, (1, 1, 1)), 1, 0)


def get_data_h5(*dataset_path):
    dataset_relpath = os.path.join(*dataset_path)
    dataset_path = utilstest.getfile(dataset_relpath)
    with h5py.File(dataset_path, "r") as hf:
        sino = hf["entry/radio/results/data"][()]
        sino_extended_ref = hf["entry/sino/results/data"][()]
        cor = hf["entry/sino/configuration/configuration/rotation_axis_position"][()]
    return sino, sino_extended_ref, cor


def generate_halftomo_sinogram_algotom(sino, cor):
    """
    Generate the 180 degrees sinogram with algotom.
    """
    n_angles, dwidth = sino.shape
    # If the sinogram has an even number of projections n_a that are exactly matched,
    # then the resulting sinogram should have n_a//2 angles.
    #
    #   0                                   0       180
    #   1                                   1       181
    #   2                                   2       182
    #   ...             -- convert -->      ...     ...
    #   180                                 179     360-1
    #   181
    #   ...
    #   360-1
    #
    # Yet for some reason algotom yields n_a//2 + 1 angles, because the "180 degrees"
    # radio is used in both "sino_top" and "sino_bottom".
    # Thus we have to cheat a little bit and use an odd number of projections.
    if n_angles % 2 == 0:
        sino = np.vstack([sino, sino[-1]]) # could even be zeros for the last line
    # In nabu we use the following overlap width.
    # algotom default is 2 * (dwidth - cor - 1), which yields 2 extra pixels
    overlap_width = 2*(dwidth - int(cor))
    sino_halftomo, new_cor = convert_sinogram_360_to_180(
        sino,
        (overlap_width, 1), # 1 means that CoR is on the right
        norm=False
    )
    if n_angles % 2 == 0:
        sino_halftomo = sino_halftomo[:-1, :]
    return sino_halftomo



@pytest.mark.usefixtures("bootstrap")
class TestHalftomo:

    def _build_sinos(self, radios, output=None, backend="python"):
        sinobuilder_cls = CudaSinoBuilder if backend == "cuda" else SinoBuilder
        sino_builder = sinobuilder_cls(
            radios_shape=radios.shape, rot_center=self.rot_center, halftomo=True
        )
        sinos_halftomo = sino_builder.radios_to_sinos(radios, output=output)
        return sinos_halftomo


    def _check_result(self, sino, test_description):
        _, err = compare_arrays(
            sino, self.sino_ref, self.tol, return_residual=True
        )
        assert err < self.tol, "Something wrong with %s" % test_description


    def test_halftomo(self):
        sinos_halftomo = self._build_sinos(self.radios, backend="python")
        self._check_result(sinos_halftomo[0], "SinoBuilder.radios_to_sino, halftomo=True")


    @pytest.mark.skipif(not (__has_pycuda__), reason="Need pycuda for this test")
    def test_cuda_halftomo(self):
        d_radios = garray.to_gpu(self.radios)
        d_sinos = garray.zeros((1,) + self.sino_ref.shape, "f")
        self._build_sinos(d_radios, output=d_sinos, backend="cuda")
        self._check_result(d_sinos.get()[0], "CudaSinoBuilder.radios_to_sino, halftomo=True")


    def _get_sino_with_odd_nprojs(self):
        n_a = self.sino.shape[0]
        # dummy line inserted in the middle,
        # so that result should match reference sinogram with an even number of angles
        sino_odd = np.vstack([
            self.sino[:n_a//2],
            self.sino[-1],  # dummy line
            self.sino[n_a//2:]
        ])
        return sino_odd

    def test_halftomo_odd(self):
        sino_odd = self._get_sino_with_odd_nprojs()
        radios = convert_sino_to_radios_stack(sino_odd)
        assert radios.shape[0] & 1, "Radios must have a odd number of angles"
        sinos = self._build_sinos(radios, backend="python")
        sino_halftomo = sinos[0][:-1, :]
        self._check_result(sino_halftomo, "SinoBuilder.radios_to_sino, halftomo=True, odd number of projs")


    @pytest.mark.skipif(not (__has_pycuda__), reason="Need pycuda for this test")
    def test_cuda_halftomo_odd(self):
        sino_odd = self._get_sino_with_odd_nprojs()
        radios = convert_sino_to_radios_stack(sino_odd)
        assert radios.shape[0] & 1, "Radios must have a odd number of angles"
        d_radios = garray.to_gpu(radios)
        d_out = garray.zeros((1, self.sino_ref.shape[0]+1, self.sino_ref.shape[1]), "f")
        self._build_sinos(d_radios, output=d_out, backend="cuda")
        sino_halftomo = d_out.get()[0][:-1, :]
        self._check_result(sino_halftomo, "CudaSinoBuilder.radios_to_sino, halftomo=True, odd number of projs")


    @staticmethod
    def _flip_array(arr):
        if arr.ndim == 2:
            return np.fliplr(arr)
        res = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            res[i] = np.fliplr(arr[i])
        return res

    def test_halftomo_left(self):
        na, nz, nx = self.radios.shape
        left_cor = nx - 1 - self.rot_center
        radios = self._flip_array(self.radios)
        sino_builder = SinoBuilder(
            radios_shape=radios.shape, rot_center=left_cor, halftomo=True
        )
        sinos_halftomo = sino_builder.radios_to_sinos(radios)
        _, err = compare_arrays(
            sinos_halftomo[0],
            self._flip_array(self.sino_ref),
            self.tol,
            return_residual=True,
        )
        assert (
            err < self.tol
        ), "Something wrong with SinoBuilder.radios_to_sino, halftomo=True"

    @pytest.mark.skipif(not (__has_pycuda__), reason="Need pycuda for this test")
    def test_cuda_halftomo_left(self):
        na, nz, nx = self.radios.shape
        left_cor = nx - 1 - self.rot_center
        radios = self._flip_array(self.radios)
        sino_processing = CudaSinoBuilder(
            radios_shape=radios.shape, rot_center=left_cor, halftomo=True
        )
        d_radios = garray.to_gpu(radios)
        d_sinos = garray.zeros(sino_processing.sinos_halftomo_shape, "f")
        sino_processing.radios_to_sinos(d_radios, output=d_sinos)
        sino_halftomo = d_sinos.get()[0]
        _, err = compare_arrays(
            sino_halftomo, self._flip_array(self.sino_ref),
            self.tol, return_residual=True
        )
        assert (
            err < self.tol
        ), "Something wrong with SinoBuilder.radios_to_sino, halftomo=True"
