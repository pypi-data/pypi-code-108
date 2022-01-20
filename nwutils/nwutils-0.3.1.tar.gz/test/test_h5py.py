import h5py
import tempfile
import numpy as np
from nwutils.h5py import h5ExportToFile, h5StoreDict

class TestH5Utils:
    def test_h5ExportToFile_1(self):
        path = tempfile.NamedTemporaryFile(suffix=".h5").name
        file = h5ExportToFile(path, {})
        assert not file is None

    def test_h5ExportToFile_1(self):
        path = tempfile.NamedTemporaryFile(suffix=".h5").name
        data = np.random.randn(5, )
        others = {"1":1, "2":2}
        file = h5ExportToFile(path, {"data":data, "others":others})
        assert not file is None
        assert "data" in file and "others" in file
        assert np.allclose(file["data"][:], data)
        assert list(file["others"].keys()) == list(others.keys())
        for k in file["others"].keys():
            assert file["others"][k][()] == others[k]
        file2 = h5py.File(path, "r")
        assert "data" in file2 and "others" in file2
        assert list(file2["others"].keys()) == list(others.keys())
        for k in file2["others"].keys():
            assert file2["others"][k][()] == others[k]
        file2.close()

    def test_h5StoreDict_1(self):
        path = tempfile.NamedTemporaryFile(suffix=".h5").name
        file = h5py.File(path, "w")
        others = {"1":1, "2":2}
        data = np.random.randn(5, )
        h5StoreDict(file, {"data":data, "others":others})
        assert not file is None
        assert "data" in file and "others" in file
        assert np.allclose(file["data"][:], data)
        assert list(file["others"].keys()) == list(others.keys())
        for k in file["others"].keys():
            assert file["others"][k][()] == others[k]
        file.close()
