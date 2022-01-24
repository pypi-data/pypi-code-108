from os import path
from tempfile import mkdtemp
import pytest
import numpy as np
from silx.io.url import DataUrl
from nabu.testutils import NXDatasetMock
from nabu.resources.nxflatfield import NXFlatField, val_to_nxkey


tempdir = mkdtemp(prefix="nabu_")


test_nxflatfield_scenarios = [
    {
        "name": "simple",
        "flats_pos": [slice(1, 6)],
        "darks_pos": [slice(0, 1)],
        "flats_reduction": "mean",
        "darks_reduction": "mean",
        "results_file": None
    },
    {
        "name": "simple_with_save",
        "flats_pos": [slice(1, 6)],
        "darks_pos": [slice(0, 1)],
        "flats_reduction": "mean",
        "darks_reduction": "mean",
        "results_file": path.join(tempdir, "ff_simple_with_save.h5"),
    },
    {
        "name": "multiple_with_save",
        "flats_pos": [slice(0, 10), slice(30, 40)],
        "darks_pos": [slice(95, 100)],
        "flats_reduction": "median",
        "darks_reduction": "mean",
        "results_file": path.join(tempdir, "ff_multiple_with_save.h5"),
    },

]

def generate_nx_dataset(fname, n_projs, flats_pos, darks_pos, h5path=None):
    image_keys = np.zeros(n_projs, dtype=np.int64)
    data_volume = np.random.randint(0, high=65535, size=(n_projs, 3, 4)).astype(np.uint16)
    # Flats have values 1, 2, 3, ...
    for i, slice_ in enumerate(flats_pos):
        for j in range(slice_.start, slice_.stop):
            data_volume[j] = j + i + 1
            image_keys[j] = val_to_nxkey["flats"]
    # Darks have values 1000, 1001, 1002, ...
    for i, slice_ in enumerate(darks_pos):
        for j in range(slice_.start, slice_.stop):
            data_volume[j] = j + i + 1000
            image_keys[j] = val_to_nxkey["darks"]
    nx_dataset_mock = NXDatasetMock(
        data_volume, image_keys
    )
    nx_dataset_mock.generate_hdf5_file(fname, h5path=h5path)
    return nx_dataset_mock


# parametrize with fixture and "params=" will launch a new class for each scenario.
# the attributes set to "cls" will remain for all the tests done in this class
# with the current scenario.
@pytest.fixture(scope='class', params=test_nxflatfield_scenarios)
def bootstrap(request):
    cls = request.cls
    cls.n_projs = 100
    cls.params = request.param


@pytest.mark.usefixtures('bootstrap')
class TestNXFlatField:

    def get_h5_filename(self):
        return path.join(tempdir, "dataset_" + self.params["name"] + ".h5")

    def _get_expected_results_imgtype(self, data_volume, what):
        slices_pos = self.params[what + "_pos"]
        reduction_func = getattr(np, self.params[what + "_reduction"])
        ref = {}
        for slice_ in slices_pos:
            ref[slice_.start] = reduction_func(
                data_volume[slice_], axis=0
            )
        return ref

    def get_expected_results(self, dataset_mock):
        data_volume = dataset_mock.dataset_dict["instrument"]["detector"]["data"]
        ref = {}
        ref["flats"] = self._get_expected_results_imgtype(data_volume, "flats")
        ref["darks"] = self._get_expected_results_imgtype(data_volume, "darks")
        return ref

    def compare_results(self, res, ref):
        assert res.keys() == ref.keys()
        for what in ref.keys():
            assert res[what].keys() == ref[what].keys()
            for idx, arr in res[what].items():
                assert np.allclose(arr, ref[what][idx])


    def test_nxflatfield(self):
        dataset_fname = self.get_h5_filename()
        nx_dataset = generate_nx_dataset(
            dataset_fname,
            self.n_projs,
            self.params["flats_pos"],
            self.params["darks_pos"],
            h5path="/entry"
        )

        results_url = None
        if self.params["results_file"] is not None:
            results_url = DataUrl(
                file_path=self.params["results_file"],
                data_path="/entry0000/flat_field_images"
            )
        nxff = NXFlatField(
            nx_dataset,
            results_url=results_url,
            flats_reduction=self.params["flats_reduction"],
            darks_reduction=self.params["darks_reduction"]
        )
        if results_url is not None:
            res_url = nxff.get_final_urls()
            res = nxff.load_data(res_url)
        else:
            res = nxff.compute_final_images()
        ref = self.get_expected_results(nx_dataset)
        self.compare_results(res, ref)
        if results_url is not None:
            nxff2 = NXFlatField(
                nx_dataset,
                lookup_files=[results_url],
                flats_reduction=self.params["flats_reduction"],
                darks_reduction=self.params["darks_reduction"]
            )
            res2_url = nxff2.get_final_urls()
            res2 = nxff.load_data(res2_url)
            self.compare_results(res2, ref)

