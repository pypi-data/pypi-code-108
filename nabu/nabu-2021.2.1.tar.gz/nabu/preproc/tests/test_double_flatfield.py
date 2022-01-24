import os.path as path
from math import exp
import tempfile
import numpy as np
import pytest
from silx.io.url import DataUrl
from tomoscan.esrf.mock import MockHDF5
from nabu.io.reader import HDF5Reader
from nabu.preproc.double_flatfield import DoubleFlatField
from nabu.preproc.double_flatfield_cuda import CudaDoubleFlatField, __has_pycuda__

if __has_pycuda__:
    import pycuda.gpuarray as garray

@pytest.fixture(scope="class")
def bootstrap(request):
    cls = request.cls
    cls.tmpdir = tempfile.TemporaryDirectory()
    dname = cls.tmpdir.name
    cls.dname = dname
    radios = MockHDF5(
        path.join(dname, "tmp"),
        10,
        n_ini_proj=10,
        dim=100,
        n_refs=1,
        scene="increasing value",
    ).scan.projections
    reader = HDF5Reader()
    cls.radios = []
    Rkeys = list(radios.keys())
    for k in Rkeys:
        dataurl = radios[k]
        data = reader.get_data(dataurl)
        cls.radios.append(data)
    cls.radios = np.array(cls.radios)
    cls.ff_dump_url = DataUrl(
        file_path=path.join(cls.dname, "dff.h5"),
        data_path="/entry/double_flatfield/results/data"
    )
    cls.ff_cuda_dump_url = DataUrl(
        file_path=path.join(cls.dname, "dff_cuda.h5"),
        data_path="/entry/double_flatfield/results/data"
    )
    golden = 0
    for i in range(10):
        golden += exp(-i)
    cls.golden = golden / 10
    cls.tol = 1e-4


@pytest.mark.usefixtures("bootstrap")
class TestDoubleFlatField:

    def test_dff_numpy(self):
        dff = DoubleFlatField(
            self.radios.shape,
            result_url=self.ff_dump_url
        )
        mydf = dff.get_double_flatfield(radios=self.radios)

        assert path.isfile(dff.result_url.file_path())

        dff2 = DoubleFlatField(
            self.radios.shape,
            result_url=self.ff_dump_url
        )
        mydf2 = dff2.get_double_flatfield(radios=self.radios)

        assert np.max(np.abs(mydf2 - mydf)) < self.tol
        assert np.max(np.abs(mydf - self.golden)) < self.tol


    @pytest.mark.skipif(not(__has_pycuda__), reason="Need pycuda for double flatfield with cuda backend")
    def test_dff_cuda(self):
        dff = CudaDoubleFlatField(
            self.radios.shape,
            result_url=self.ff_cuda_dump_url
        )
        d_radios = garray.to_gpu(self.radios)
        mydf = dff.get_double_flatfield(radios=d_radios).get()


        assert path.isfile(dff.result_url.file_path())

        dff2 = CudaDoubleFlatField(
            self.radios.shape,
            result_url=self.ff_cuda_dump_url
        )
        mydf2 = dff2.get_double_flatfield(radios=d_radios).get()

        assert np.max(np.abs(mydf2 - mydf)) < self.tol
        assert np.max(np.abs(mydf - self.golden)) < self.tol
