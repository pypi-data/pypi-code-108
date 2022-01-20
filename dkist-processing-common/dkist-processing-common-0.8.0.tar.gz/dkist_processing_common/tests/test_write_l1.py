from dataclasses import dataclass
from random import randint
from typing import Literal
from unittest.mock import Mock
from unittest.mock import PropertyMock

import numpy as np
import pytest
from astropy.io import fits
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec214_validator

from dkist_processing_common import __version__ as common_version
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.write_l1 import WriteL1Frame
from dkist_processing_common.tests.conftest import FakeGQLClient


class CompleteWriteL1Frame(WriteL1Frame):
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        header["DAAXES"] = 2
        header["DEAXES"] = 3
        header["DNAXIS"] = 5
        header["FRAMEWAV"] = 123.45
        header["LEVEL"] = 1
        header["WAVEMAX"] = 124
        header["WAVEMIN"] = 123
        header["WAVEREF"] = "Air"
        header["WAVEUNIT"] = -9
        header["DINDEX3"] = 3
        header["DINDEX4"] = 2
        header["DINDEX5"] = 1
        header["DNAXIS1"] = header["NAXIS1"]
        header["DNAXIS2"] = header["NAXIS2"]
        header["DNAXIS3"] = 10
        header["DNAXIS4"] = 1
        header["DNAXIS5"] = 4
        header["DPNAME1"] = ""
        header["DPNAME2"] = ""
        header["DPNAME3"] = ""
        header["DPNAME4"] = ""
        header["DPNAME5"] = ""
        header["DTYPE1"] = "SPATIAL"
        header["DTYPE2"] = "SPATIAL"
        header["DTYPE3"] = "TEMPORAL"
        header["DTYPE4"] = "SPECTRAL"
        header["DTYPE5"] = "STOKES"
        header["DUNIT1"] = ""
        header["DUNIT2"] = ""
        header["DUNIT3"] = ""
        header["DUNIT4"] = ""
        header["DUNIT5"] = ""
        header["DWNAME1"] = ""
        header["DWNAME2"] = ""
        header["DWNAME3"] = ""
        header["DWNAME4"] = ""
        header["DWNAME5"] = ""
        header["NBIN"] = 1
        for i in range(1, header["NAXIS"] + 1):
            header[f"NBIN{i}"] = 1

        return header


@dataclass
class FakeConstants:
    instrument: str = "TEST"
    average_cadence: float = 10.0
    minimum_cadence: float = 10.0
    maximum_cadence: float = 10.0
    variance_cadence: float = 0.0
    stokes_params: tuple = ("I", "Q", "U", "V")


@pytest.fixture(scope="function", params=[1, 4])
def write_l1_task(complete_common_header, request):
    with CompleteWriteL1Frame(
        recipe_run_id=randint(0, 99999),
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        num_of_stokes_params = request.param
        stokes_params = ["I", "Q", "U", "V"]
        used_stokes_params = []
        hdu = fits.PrimaryHDU(data=np.ones(shape=(1, 128, 128)), header=complete_common_header)
        hdul = fits.HDUList([hdu])
        for i in range(num_of_stokes_params):
            task.fits_data_write(
                hdu_list=hdul,
                tags=[
                    Tag.calibrated(),
                    Tag.frame(),
                    Tag.stokes(stokes_params[i]),
                    Tag.dsps_repeat(i),
                ],
            )
            used_stokes_params.append(stokes_params[i])
        task.constants = FakeConstants()
        yield task, used_stokes_params
        task._constants_db.purge()
        task.scratch.purge()


def test_write_l1_frame(write_l1_task, mocker):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame._get_version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, used_stokes_params = write_l1_task
    task()
    for stokes_param in used_stokes_params:
        files = list(task.read(tags=[Tag.frame(), Tag.output(), Tag.stokes(stokes_param)]))
        assert len(files) == 1
        for file in files:
            assert file.exists
            spec214_validator.validate(file, extra=False)


def test_tags_preserved(write_l1_task, mocker):
    """
    :Given: an input header
    :When: converting that header to L1 and writing it to disk
    :Then: all tags that are not CALIBRATED are copied over to the new file
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame._get_version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, used_stokes_params = write_l1_task
    task()
    for i, s in enumerate(used_stokes_params):
        files = list(task.read(tags=[Tag.output(), Tag.frame(), Tag.stokes(s)]))
        assert len(files) == 1
        # We use dsps_repeat just as a stand-in for another tag
        assert Tag.dsps_repeat(i) in task.tags(files[0])


def test_replace_header_values(write_l1_task, complete_common_header):
    """
    :Given: an input header
    :When: replacing specific header values
    :Then: the header values have changed
    """
    task, _ = write_l1_task
    original_file_id = complete_common_header["FILE_ID"]
    original_date = complete_common_header["DATE"]
    data = np.ones(shape=(1, 1))
    header = task._replace_header_values(header=complete_common_header, data=data)
    assert header["FILE_ID"] != original_file_id
    assert header["DATE"] != original_date
    assert header["NAXIS"] == len(data.shape)


def test_l1_filename(write_l1_task, complete_common_header):
    """
    :Given: an input header
    :When: asking for the corresponding L1 filename
    :Then: the filename is formatted as expected
    """
    task, _ = write_l1_task
    assert (
        task.l1_filename(header=complete_common_header, stokes="Q")
        == "VISP_L1_01080000_2020_01_02T00_00_00_000_Q.fits"
    )


def test_calculate_date_avg(write_l1_task, complete_common_header):
    """
    :Given: an input header
    :When: finding the average date
    :Then: the correct datetime string is returned
    """
    task, _ = write_l1_task
    assert task._calculate_date_avg(header=complete_common_header) == "2020-01-02T12:00:00.000"


def test_calculate_telapse(write_l1_task, complete_common_header):
    """
    :Given: an input header
    :When: finding the time elapsed in an observation
    :Then: the correct time value is returned
    """
    task, _ = write_l1_task
    assert task._calculate_telapse(header=complete_common_header) == 86400


def test_solarnet_keys(write_l1_task, mocker):
    """
    :Given: files with headers converted to SPEC 214 L1
    :When: checking the solarnet extra headers
    :Then: the correct values are found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame._get_version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        header = fits.open(file)[1].header
        assert header["DATEREF"] == header["DATE-BEG"]
        assert round(header["OBSGEO-X"]) == -5466045
        assert round(header["OBSGEO-Y"]) == -2404389
        assert round(header["OBSGEO-Z"]) == 2242134
        assert header["SPECSYS"] == "TOPOCENT"
        assert header["VELOSYS"] is False


def test_documentation_keys(write_l1_task, mocker):
    """
    :Given: files with headers converted to SPEC 214 L1
    :When: checking the documentation header URLs
    :Then: the correct values are found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame._get_version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        header = fits.open(file)[1].header
        assert header["INFO_URL"] == task.docs_base_url
        assert header["HEADVERS"] == spec_version
        assert (
            header["HEAD_URL"] == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
        )
        calvers = task._get_version_from_module_name()
        assert header["CALVERS"] == calvers
        assert (
            header["CAL_URL"]
            == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}"
        )


def test_get_version_from_module(write_l1_task):
    task, _ = write_l1_task
    assert task._get_version_from_module_name() == common_version
