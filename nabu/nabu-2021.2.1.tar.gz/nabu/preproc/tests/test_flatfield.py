from tempfile import mkdtemp
import os
import numpy as np
import pytest
from silx.io.url import DataUrl
from silx.third_party.EdfFile import EdfFile
from silx.io.dictdump import dicttoh5
from nabu.cuda.utils import get_cuda_context, __has_pycuda__
from nabu.preproc.flatfield import FlatFieldDataUrls

if __has_pycuda__:
    import pycuda.gpuarray as garray
    from nabu.preproc.flatfield_cuda import CudaFlatFieldDataUrls



@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls.n_radios = 10
    cls.n_z = 100
    cls.n_x = 512
    cls.create_radios()
    cls.create_flats_and_dark()
    cls.create_multiple_flats()
    if __has_pycuda__:
        cls.ctx = get_cuda_context()
    yield
    # tear-down
    for fname in ["flat.edf", "dark.edf", "flat00.edf", "flat09.edf"]:
        os.remove(os.path.join(cls.tempdir, fname))
    os.rmdir(cls.tempdir)


@pytest.mark.usefixtures('bootstrap')
class TestFlatField:

    @classmethod
    def create_radios(cls):
        cls.radio_shape = (cls.n_z, cls.n_x)
        cls.radios_stack = np.ones(
            (cls.n_radios, cls.n_z, cls.n_x),
            dtype=np.float32
        )
        for i in range(cls.n_radios):
            cls.radios_stack[i] += i

    @classmethod
    def create_flats_and_dark(cls):
        cls.tempdir = mkdtemp(prefix="nabu_")
        cls.dark = np.ones(cls.radio_shape, dtype=np.float32)
        cls.flat = np.zeros(cls.radio_shape, dtype=np.float32) + 0.5
        # TODO use hdf5 once an official convention is validated
        flat_fname = os.path.join(cls.tempdir, "flat.edf")
        dark_fname = os.path.join(cls.tempdir, "dark.edf")
        edf_flat = EdfFile(flat_fname, "w")
        edf_dark = EdfFile(dark_fname, "w")
        edf_flat.WriteImage({}, cls.flat)
        edf_dark.WriteImage({}, cls.dark)
        cls.flat_url = {0: DataUrl(
            file_path=flat_fname,
            data_path=None, data_slice=[0],
            scheme='fabio'
        )}
        cls.dark_url = {0: DataUrl(
            file_path=dark_fname,
            data_path=None, data_slice=[0],
            scheme='fabio'
        )}

    @classmethod
    def create_multiple_flats(cls):
        flat00 = np.zeros(cls.radio_shape, dtype=np.float32) + 2.
        flat09 = np.zeros_like(flat00) + 11.
        fnames = []
        for fname, arr in zip(["flat00.edf", "flat09.edf"], [flat00, flat09]):
            full_fname = os.path.join(cls.tempdir, fname)
            fnames.append(full_fname)
            edf = EdfFile(full_fname)
            edf.WriteImage({}, arr)
        cls.flats_urls = {
            0: DataUrl(file_path=fnames[0], data_path=None, data_slice=[0], scheme='fabio'),
            9: DataUrl(file_path=fnames[1], data_path=None, data_slice=[0], scheme='fabio')
        }


    def _check_corrected_radios(self, radios_corr, expected_values):
        # must be the same value everywhere in the radio
        std = np.std(np.std(radios_corr, axis=-1), axis=-1)
        assert np.max(np.abs(std)) < 1e-7
        # radios values must be 0, -2, -4, ...
        assert np.allclose(radios_corr[:, 0, 0], expected_values)


    def test_flatfield_simple(self):
        """
        Test the flat-field normalization on a radios stack with 1 dark and 1 flat.

        (I - D)/(F - D)   where I = (1, 2, ...), D = 1, F = 0.5
        = (0, -2, -4, -6, ...)
        """
        flatfield = FlatFieldDataUrls(self.radios_stack.shape, self.flat_url, self.dark_url)
        radios_corr = flatfield.normalize_radios(np.copy(self.radios_stack))
        self._check_corrected_radios(radios_corr, np.arange(0, -2*self.n_radios, -2))


    def test_flatfield_simple_subregion(self):
        """
        Same as test_flatfield_simple, but in a vertical subregion of the radios.
        """
        end_z = 51
        radios_chunk = np.copy(self.radios_stack[:, :end_z, :])
        # we only have a chunk in memory. Instantiate the class with the
        # corresponding subregion to only load the relevant part of dark/flat
        flatfield = FlatFieldDataUrls(
            radios_chunk.shape, self.flat_url, self.dark_url,
            sub_region=(None, None, None, end_z) # start_x, end_x, start_z, end_z
        )
        radios_corr = flatfield.normalize_radios(radios_chunk)
        self._check_corrected_radios(radios_corr, np.arange(0, -2*self.n_radios, -2))


    def test_flatfield_linear_interp(self):
        """
        Test flat-field normalization with 1 dark and 2 flats, with linear
        interpolation between flats.
        I   = 1   2   3   4   5   6   7   8   9   10
        D   = 1                                         (one dark)
        F   = 2                                   11    (two flats)
        F_i = 2   3   4   5   6   7   8   9   10  11   (interpolated flats)
        R   = 0  .5  .66 .75 .8  .83  .86
            = (I-D)/(F-D)
            = (I-1)/I
        """
        flatfield = FlatFieldDataUrls(self.radios_stack.shape, self.flats_urls, self.dark_url)
        radios_corr = flatfield.normalize_radios(np.copy(self.radios_stack))
        I = np.arange(1, self.n_radios+1)
        self._check_corrected_radios(radios_corr, (I-1)/I)

        # Test 2: one of the flats is not at the beginning/end
        # I   = 1    2    3    4    5    6    7    8    9    10
        # F   = 2                       11
        # F_i = 2   3.8  5.6 7.4  9.2   11   11   11   11    11
        # R   = 0   .357  .435 .469 .488 .5  .6   .7  .8     .9
        flats_urls = self.flats_urls.copy()
        flats_urls[5] = flats_urls[9]
        flats_urls.pop(9)
        flatfield = FlatFieldDataUrls(self.radios_stack.shape, flats_urls, self.dark_url)
        radios_corr = flatfield.normalize_radios(np.copy(self.radios_stack))
        I = np.arange(1, self.n_radios+1)
        D = 1
        F = np.array([2, 3.8, 5.6, 7.4, 9.2, 11, 11, 11, 11, 11])
        self._check_corrected_radios(radios_corr, (I-D)/(F-D))


    @pytest.mark.skipif(not(__has_pycuda__), reason="Need cuda/pycuda for this test")
    def test_cuda_flatfield(self):
        """
        Test the flat-field with cuda back-end.
        """
        d_radios = garray.to_gpu(self.radios_stack.astype("f"))
        cuda_flatfield = CudaFlatFieldDataUrls(
            d_radios.shape,
            self.flats_urls,
            self.dark_url,
            # ~ cuda_options={"ctx": self.ctx}
        )
        cuda_flatfield.normalize_radios(d_radios)
        radios_corr = d_radios.get()
        I = np.arange(1, self.n_radios+1)
        self._check_corrected_radios(radios_corr, (I-1)/I)


# This test should be closer to the ESRF standard setting.
# There are 2 flats, one dark, 4000 radios.
#  dark :  indice=0     value=10
#  flat1 : indice=1     value=4202
#  flat2 : indice=2102  value=2101
#
# The projections have the following indices:
#  j:    0     1        1998  1999  2000  2001                   3999
# idx:  [102, 103, ..., 2100, 2101, 2203, 2204, ..., 4200, 4201, 4202]
#  Notice the gap in the middle.
#
# The linear interpolation is
#    flat_i = (n2 - i)/(n2 - n1)*flat_1  + (i - n1)/(n2 - n1)*flat_2
#  where n1 and n2 are the indices of flat_1 and flat_2 respectively.
# With the above values, we have flat_i = 4203 - i.
#
# The projections values are dark + i*(flat_i - dark),
# so that the normalization norm_i = (proj_i - dark)/(flat_i - dark) gives
#
#   idx     102    103    104    ...
#   flat    4101   4102   4103   ...
#   norm    102    103    104    ...
#


class FlatFieldTestDataset:
    # Parameters
    shp = (27, 32)
    n1 = 1 # flat indice 1
    n2 = 2102 # flat indice 2
    dark_val = 10
    darks = {0: np.zeros(shp, "f") + dark_val}
    flats = {
        n1: np.zeros(shp, "f") + (n2-1)*2,
        n2: np.zeros(shp, "f") + n2-1
    }
    projs_idx = list(range(102, 2102)) + list(range(2203, 4203)) # gap in the middle


    def __init__(self):
        self._generate_projections()
        self._dump_to_h5()
        self._generate_dataurls()


    def get_flat_idx(self, proj_idx):
        flats_idx = sorted(list(self.flats.keys()))
        if proj_idx <= flats_idx[0]:
            return (flats_idx[0], )
        elif proj_idx > flats_idx[0] and proj_idx < flats_idx[1]:
            return flats_idx
        else:
            return (flats_idx[1], )

    def get_flat(self, idx):
        flatidx = self.get_flat_idx(idx)
        if len(flatidx) == 1:
            flat = self.flats[flatidx[0]]
        else:
            nf1, nf2 = flatidx
            w1 = (nf2 - idx)/(nf2 - nf1)
            flat = w1 * self.flats[nf1] + (1 - w1) * self.flats[nf2]
        return flat


    def _generate_projections(self):
        self.projs_data = np.zeros((len(self.projs_idx), ) + self.shp, "f")
        self.projs = {}
        for i, proj_idx in enumerate(self.projs_idx):

            flat = self.get_flat(proj_idx)

            proj_val = self.dark_val + proj_idx * (flat[0,0] - self.dark_val)
            self.projs[str(proj_idx)] = np.zeros(self.shp, "f") + proj_val
            self.projs_data[i] = self.projs[str(proj_idx)]


    def _dump_to_h5(self):
        self.tempdir = mkdtemp(prefix="nabu_")
        self.fname = os.path.join(self.tempdir, "projs_flats.h5")
        dicttoh5(
            {
                "projs": self.projs,
                "flats": {str(k): v for k, v in self.flats.items()},
                "darks": {str(k): v for k, v in self.darks.items()}
            },
            h5file=self.fname
        )


    def _generate_dataurls(self):
        self.flats_urls = {}
        for idx in self.flats.keys():
            self.flats_urls[int(idx)] = DataUrl(
                file_path=self.fname, data_path="/flats/%d" % idx
            )
        self.darks_urls = {}
        for idx in self.darks.keys():
            self.darks_urls[int(idx)] = DataUrl(
                file_path=self.fname, data_path="/darks/0"
            )


@pytest.fixture(scope='class')
def bootstraph5(request):
    cls = request.cls

    cls.dataset = FlatFieldTestDataset()
    n1, n2 = cls.dataset.n1, cls.dataset.n2

    # Interpolation function
    cls._weight1 = lambda i: (n2 - i)/(n2 - n1)

    cls.tol = 5e-4
    cls.tol_std = 1e-3

    yield
    # tear-down
    os.remove(cls.dataset.fname)
    os.rmdir(cls.dataset.tempdir)

@pytest.mark.usefixtures('bootstraph5')
class TestFlatFieldH5:

    def check_normalization(self, projs):
        # Check that each projection is filled with the same values
        std_projs = np.std(projs, axis=(-2, -1))
        assert np.max(np.abs(std_projs)) < self.tol_std
        # Check that the normalized radios are equal to 102, 103, 104, ...
        errs = projs[:, 0, 0] - self.dataset.projs_idx
        assert np.max(np.abs(errs)) < self.tol, "Something wrong with flat-field normalization"


    def test_flatfield(self):
        flatfield = FlatFieldDataUrls(
            self.dataset.projs_data.shape,
            self.dataset.flats_urls,
            self.dataset.darks_urls,
            radios_indices=self.dataset.projs_idx,
            interpolation="linear"
        )
        projs = np.copy(self.dataset.projs_data)
        flatfield.normalize_radios(projs)
        self.check_normalization(projs)


    @pytest.mark.skipif(not(__has_pycuda__), reason="Need cuda/pycuda for this test")
    def test_cuda_flatfield(self):
        d_projs = garray.to_gpu(self.dataset.projs_data)
        cuda_flatfield = CudaFlatFieldDataUrls(
            self.dataset.projs_data.shape,
            self.dataset.flats_urls,
            self.dataset.darks_urls,
            radios_indices=self.dataset.projs_idx
        )
        cuda_flatfield.normalize_radios(d_projs)
        projs = d_projs.get()
        self.check_normalization(projs)




#
# Another test with more than two flats.
#
# Here we have
#
#   F_i = i + 2
#   R_i = i*(F_i - 1) + 1
#   N_i = (R_i - D)/(F_i - D) = i*(F_i - 1)/( F_i - 1) = i
#


def generate_test_flatfield(n_radios, radio_shape, flat_interval, h5_fname):
    radios = np.zeros((n_radios, ) + radio_shape, "f")
    dark_data = np.ones(radios.shape[1:], "f")
    tempdir = mkdtemp(prefix="nabu_")
    testffname = os.path.join(tempdir, h5_fname)
    flats = {}
    flats_urls = {}
    # F_i = i + 2
    # R_i = i*(F_i - 1) + 1
    # N_i = (R_i - D)/(F_i - D) = i*(F_i - 1)/( F_i - 1) = i
    for i in range(n_radios):
        f_i = i + 2
        if (i % flat_interval) == 0:
            flats["flats_%04d" % i] = np.zeros(radio_shape, "f") + f_i
            flats_urls[i] = DataUrl(file_path=testffname, data_path=str("/flats/flats_%04d" % i), scheme="silx")
        radios[i] = i * (f_i - 1) + 1
    dark = {"dark_0000": dark_data}
    dicttoh5(flats, testffname, h5path="/flats", mode="w")
    dicttoh5(dark, testffname, h5path="/dark", mode="a")
    dark_url = {0: DataUrl(file_path=testffname, data_path="/dark/dark_0000", scheme="silx")}
    return radios, flats_urls, dark_url


@pytest.fixture(scope='class')
def bootstrap_multiflats(request):
    cls = request.cls

    n_radios = 50
    radio_shape = (20, 21)
    cls.flat_interval = 11
    h5_fname = "testff.h5"

    radios, flats, dark = generate_test_flatfield(
        n_radios, radio_shape, cls.flat_interval, h5_fname
    )
    cls.radios = radios
    cls.flats_urls = flats
    cls.darks_urls = dark
    cls.expected_results = np.arange(n_radios)

    cls.tol = 5e-4
    cls.tol_std = 1e-4


@pytest.mark.usefixtures('bootstrap_multiflats')
class TestFlatFieldMultiFlat:

    def check_normalization(self, projs):
        # Check that each projection is filled with the same values
        std_projs = np.std(projs, axis=(-2, -1))
        assert np.max(np.abs(std_projs)) < self.tol_std
        # Check that the normalized radios are equal to 0, 1, 2, ...
        stop = (projs.shape[0] // self.flat_interval) * self.flat_interval
        errs = projs[:stop, 0, 0] - self.expected_results[:stop]
        assert np.max(np.abs(errs)) < self.tol, "Something wrong with flat-field normalization"


    def test_flatfield(self):
        flatfield = FlatFieldDataUrls(
            self.radios.shape,
            self.flats_urls,
            self.darks_urls,
            interpolation="linear"
        )
        projs = np.copy(self.radios)
        flatfield.normalize_radios(projs)
        print(projs[:, 0, 0])
        self.check_normalization(projs)

    @pytest.mark.skipif(not(__has_pycuda__), reason="Need cuda/pycuda for this test")
    def test_cuda_flatfield(self):
        d_projs = garray.to_gpu(self.radios)
        cuda_flatfield = CudaFlatFieldDataUrls(
            self.radios.shape,
            self.flats_urls,
            self.darks_urls,
        )
        cuda_flatfield.normalize_radios(d_projs)
        projs = d_projs.get()
        self.check_normalization(projs)
