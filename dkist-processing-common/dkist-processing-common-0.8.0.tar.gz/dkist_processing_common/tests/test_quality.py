import json
import random
from typing import List

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_data_simulator.spec214 import Spec214Dataset

from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.quality_metrics import QualityL0Metrics
from dkist_processing_common.tasks.quality_metrics import QualityL1Metrics


class BaseSpec214l0Dataset(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        super().__init__(
            dataset_shape=(10, 10, 10),
            array_shape=(1, 10, 10),
            time_delta=1,
            instrument=instrument,
            file_schema="level0_spec214",
        )

    @property
    def data(self):
        return np.ones(shape=self.array_shape)


class BaseSpec214Dataset(Spec214Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )

    @property
    def fits_wcs(self):
        w = WCS(naxis=2)
        w.wcs.crpix = self.array_shape[1] / 2, self.array_shape[0] / 2
        w.wcs.crval = 0, 0
        w.wcs.cdelt = 1, 1
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


@pytest.fixture(scope="session")
def task_type_options() -> List[str]:
    # note that the length of this list and the dataset size affect how many occurrences there are
    return ["observe", "focus", "dark", "gain", "telcal"]


@pytest.fixture(params=["dark", "gain"])
def quality_task_type(request) -> List[str]:
    # note that the length of this list and the dataset size affect how many occurrences there are
    return request.param


@pytest.fixture
def base_spec_214_l0_dataset_factory():
    def factory(task_types) -> List[fits.HDUList]:
        hduls = []
        for ds in BaseSpec214l0Dataset():
            hdu = ds.hdu()
            # overwritten here because you can't add an IPTASK @key_function to the dataset
            task_type_index = ds.index % len(task_types)
            hdu.header["IPTASK"] = task_types[task_type_index]
            hduls.append(fits.HDUList([hdu]))
        return hduls

    return factory


@pytest.fixture
def quality_l0_task(recipe_run_id):
    with QualityL0Metrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        yield task
        task.scratch.purge()
        task._constants_db.purge()


@pytest.fixture
def quality_l0_task_with_quality_task_types(
    quality_l0_task, task_type_options, base_spec_214_l0_dataset_factory
):
    hduls = base_spec_214_l0_dataset_factory(task_type_options)
    [
        quality_l0_task.fits_data_write(hdu_list=hdul, tags=[Tag.input(), Tag.task(t)])
        for hdul in hduls
        for t in task_type_options
    ]
    return quality_l0_task


@pytest.fixture
def quality_l0_task_without_quality_task_types(
    quality_l0_task,
    request,
    recipe_run_id,
    task_type_options,
    base_spec_214_l0_dataset_factory,
    quality_task_type,
):
    task_types = [t for t in task_type_options if t != quality_task_type]
    hduls = base_spec_214_l0_dataset_factory(task_types)
    [
        quality_l0_task.fits_data_write(hdu_list=hdul, tags=[Tag.input(), Tag.task(t)])
        for hdul in hduls
        for t in task_types
    ]
    return quality_l0_task


@pytest.mark.parametrize("metric_name", ["FRAME_RMS", "FRAME_AVERAGE"])
def test_l0_quality_metrics(
    quality_l0_task_with_quality_task_types, metric_name, quality_task_type
):
    """
    Given: a task with the QualityL0Metrics class
    When: checking that the task metric combination was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the
      expected schema
    """
    # call task and assert that things were created (tagged files on disk with quality metric info in them)
    task = quality_l0_task_with_quality_task_types
    task()
    files = list(task.read(tags=[Tag.quality(metric_name), Tag.quality_task(quality_task_type)]))
    assert files  # there are some
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["x_values"]
            assert data["y_values"]
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
            assert len(data["x_values"]) == len(data["y_values"])


@pytest.mark.parametrize("metric_name", ["FRAME_RMS", "FRAME_AVERAGE"])
def test_l0_quality_metrics_missing_quality_task_types(
    quality_l0_task_without_quality_task_types, metric_name, quality_task_type
):
    """
    Given: a task with the QualityL0Metrics class
    When: checking that the task metric combination was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the
      expected schema
    """
    task = quality_l0_task_without_quality_task_types
    task()
    files = list(task.read(tags=[Tag.quality(metric_name), Tag.quality_task(quality_task_type)]))
    assert not files  # there are none


@pytest.fixture
def quality_L1_task(tmp_path, recipe_run_id):
    with QualityL1Metrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        for i in range(10):
            header_dict = [
                d.header(required_only=False, expected_only=False) for d in BaseSpec214Dataset()
            ][0]
            data = np.ones(shape=BaseSpec214Dataset().array_shape)
            hdu = fits.PrimaryHDU(data=data, header=fits.Header(header_dict))
            hdul = fits.HDUList([hdu])
            task.fits_data_write(hdu_list=hdul, tags=[Tag.output(), Tag.frame()])
        yield task
    task.scratch.purge()
    task._constants_db.purge()


def test_fried_parameter(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the fried parameter metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("FRIED_PARAMETER")))
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
            # assert data["task_type"] == "observe"


def test_light_level(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the light level metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("LIGHT_LEVEL")))
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
            # assert data["task_type"] == "observe"


def test_health_status(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the health status metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("HEALTH_STATUS")))
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, list)


def test_ao_status(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the AO status metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("AO_STATUS")))
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, list)


def test_noise(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the nosie metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("NOISE")))
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
