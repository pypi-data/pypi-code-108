from os import path
from tempfile import TemporaryDirectory
import pytest
import numpy as np
from tifffile import TiffReader
from silx.io.dictdump import h5todict, dicttoh5
from nabu.misc.utils import psnr
from nabu.io.writer import NXProcessWriter, TIFFWriter, JP2Writer, __have_jp2k__
from nabu.io.reader import import_h5_to_dict
from nabu.testutils import get_data
if __have_jp2k__:
    from glymur import Jp2k


@pytest.fixture(scope='class')
def bootstrap(request):
    cls = request.cls
    cls._tmpdir = TemporaryDirectory(prefix="nabu_")
    cls.tempdir = cls._tmpdir.name
    cls.sino_data = get_data("mri_sino500.npz")["data"].astype(np.uint16)
    cls.data = cls.sino_data
    yield
    # teardown
    cls._tmpdir.cleanup()



@pytest.mark.usefixtures('bootstrap')
class TestTiff:

    def _check_tif_file(self, fname, expected_data, n_expected_images):
        with TiffReader(fname) as tif:
            assert len(tif.pages) == n_expected_images
            for i in range(n_expected_images):
                data_read = tif.pages[i].asarray()
                if expected_data.ndim == 3:
                    expected_data_ = expected_data[i]
                else:
                    expected_data_ = expected_data
                assert np.allclose(data_read, expected_data_)

    def test_2D(self):
        fname = path.join(self.tempdir, "test_tiff2D.tif")
        data = np.arange(100*101, dtype="f").reshape((100, 101))
        nabu_tif = TIFFWriter(fname)
        nabu_tif.write(data)
        self._check_tif_file(fname, data, 1)


    def test_3D_data_split_in_multiple_files(self):
        fname = path.join(self.tempdir, "test_tiff3D_single.tif")
        data = np.arange(11*100*101, dtype="f").reshape((11, 100, 101))
        nabu_tif = TIFFWriter(fname, multiframe=False, start_index=500)
        nabu_tif.write(data)

        assert not(path.isfile(fname)), "found %s" % fname

        prefix, ext = path.splitext(fname)
        for i in range(data.shape[0]):
            curr_rel_fname = prefix + str("_%04d" % (i + nabu_tif.start_index)) + ext
            curr_fname = path.join(self.tempdir, curr_rel_fname)
            self._check_tif_file(curr_fname, data[i], 1)


    def test_3D_data_in_one_file(self):
        fname = path.join(self.tempdir, "test_tiff3D_multi.tif")
        data = np.arange(11*100*101, dtype="f").reshape((11, 100, 101))
        nabu_tif = TIFFWriter(fname, multiframe=True)
        nabu_tif.write(data)

        assert path.isfile(fname)
        self._check_tif_file(fname, data, data.shape[0])


@pytest.mark.skipif(not(__have_jp2k__), reason="Need openjpeg2000/glymur for this test")
@pytest.mark.usefixtures('bootstrap')
class TestJP2:

    def _check_jp2_file(self, fname, expected_data, expected_psnr=None):
        data = Jp2k(fname)[:]
        if expected_psnr is None:
            assert np.allclose(data, expected_data)
        else:
            computed_psnr = psnr(data, expected_data)
            assert np.abs(computed_psnr - expected_psnr) < 1


    def test_2D_lossless(self):
        data = get_data("mri_sino500.npz")["data"].astype(np.uint16)
        fname = path.join(self.tempdir, "sino500.j2k")
        nabu_jp2 = JP2Writer(fname, psnr=[0])
        nabu_jp2.write(data)
        self._check_jp2_file(fname, data)


    def test_2D_lossy(self):
        fname = path.join(self.tempdir, "sino500_lossy.j2k")
        nabu_jp2 = JP2Writer(fname, psnr=[80])
        nabu_jp2.write(self.sino_data)
        self._check_jp2_file(fname, self.sino_data, expected_psnr=80)


    def test_3D(self):
        fname = path.join(self.tempdir, "sino500_multi.j2k")
        n_images = 5
        data = np.tile(self.sino_data, (n_images, 1, 1))
        for i in range(n_images):
            data[i] += i

        nabu_jp2 = JP2Writer(fname, start_index=10)
        nabu_jp2.write(data)

        assert not(path.isfile(fname))

        prefix, ext = path.splitext(fname)
        for i in range(data.shape[0]):
            curr_rel_fname = prefix + str("_%04d" % (i + nabu_jp2.start_index)) + ext
            curr_fname = path.join(self.tempdir, curr_rel_fname)
            self._check_jp2_file(curr_fname, data[i])



@pytest.fixture(scope='class')
def bootstrap_h5(request):
    cls = request.cls
    cls._tmpdir = TemporaryDirectory(prefix="nabu_")
    cls.tempdir = cls._tmpdir.name
    cls.data = get_data("mri_sino500.npz")["data"].astype(np.uint16)
    cls.h5_config = {
            "key1": "value1",
            "some_int": 1,
            "some_float": 1.0,
            "some_dict": {
                "numpy_array": np.ones((5, 6), dtype="f"),
                "key2": "value2",
            }
        }
    yield
    # teardown
    cls._tmpdir.cleanup()



@pytest.mark.usefixtures('bootstrap_h5')
class TestNXWriter:

    def test_write_simple(self):
        fname = path.join(self.tempdir, "sino500.h5")
        writer = NXProcessWriter(fname, entry="entry0000")
        writer.write(self.data, "test_write_simple")


    def test_write_with_config(self):
        fname = path.join(self.tempdir, "sino500_cfg.h5")
        writer = NXProcessWriter(fname, entry="entry0000")
        writer.write(self.data, "test_write_with_config", config=self.h5_config)


    def test_overwrite(self):
        fname = path.join(self.tempdir, "sino500_overwrite.h5")
        writer = NXProcessWriter(fname, entry="entry0000", overwrite=True)
        writer.write(self.data, "test_overwrite", config=self.h5_config)

        writer2 = NXProcessWriter(fname, entry="entry0001", overwrite=True)
        writer2.write(self.data, "test_overwrite", config=self.h5_config)

        # overwrite entry0000
        writer3 = NXProcessWriter(fname, entry="entry0000", overwrite=True)
        new_data = self.data.copy()
        new_data += 1
        new_config = self.h5_config.copy()
        new_config["key1"] = "modified value"
        writer3.write(new_data, "test_overwrite", config=new_config)

        res = import_h5_to_dict(fname, "/")
        assert "entry0000" in res
        assert "entry0001" in res
        assert np.allclose(
            res["entry0000"]["test_overwrite"]["results"]["data"],
            self.data + 1
        )
        rec_cfg = res["entry0000"]["test_overwrite"]["configuration"]
        assert rec_cfg["key1"] == "modified value"


    def test_no_overwrite(self):
        fname = path.join(self.tempdir, "sino500_no_overwrite.h5")
        writer = NXProcessWriter(fname, entry="entry0000", overwrite=False)
        writer.write(self.data, "test_no_overwrite")

        writer2 = NXProcessWriter(fname, entry="entry0000", overwrite=False)
        with pytest.raises((RuntimeError, OSError)) as ex:
            writer2.write(self.data, "test_no_overwrite")

        message = "Error should have been raised for trying to overwrite, but got the following: %s" % str(
            ex.value
        )
