from random import randint

import numpy as np
import pytest
from astropy.io import fits
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec214_validator
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tests.conftest import FakeGQLClient

from dkist_processing_visp.tasks.write_l1 import VispWriteL1Frame
from dkist_processing_visp.tests.conftest import FakeVispConstants


@pytest.fixture(scope="function", params=[1, 4])
def write_l1_task(visp_dataset, request, apply_mock_constants):
    num_of_stokes_params = request.param
    mock_constants = FakeVispConstants(
        instrument="VISP",
        average_cadence=10,
        minimum_cadence=10,
        maximum_cadence=10,
        variance_cadence=0,
        num_dsps_repeats=1,
        num_raster_steps=2,
        spectral_line="VISP Ca II H",
        correct_for_polarization=True if num_of_stokes_params == 4 else False,
    )
    apply_mock_constants(mock_constants)
    with VispWriteL1Frame(
        recipe_run_id=randint(0, 99999),
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            stokes_params = ["I", "Q", "U", "V"]
            used_stokes_params = []
            hdu = fits.PrimaryHDU(data=np.ones(shape=(128, 128, 1)), header=visp_dataset)
            hdul = fits.HDUList([hdu])
            for i in range(num_of_stokes_params):
                task.fits_data_write(
                    hdu_list=hdul,
                    tags=[Tag.calibrated(), Tag.frame(), Tag.stokes(stokes_params[i])],
                )
                used_stokes_params.append(stokes_params[i])
            yield task, used_stokes_params
        except:
            raise
        finally:
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
    task, stokes_params = write_l1_task
    task()
    for stokes_param in stokes_params:
        files = list(task.read(tags=[Tag.frame(), Tag.output(), Tag.stokes(stokes_param)]))
        assert len(files) == 1
        for file in files:
            assert file.exists
            assert spec214_validator.validate(file, extra=False)
            hdu_list = fits.open(file)
            assert len(hdu_list) == 2  # Primary, CompImage
            assert type(hdu_list[0]) is fits.PrimaryHDU
            assert type(hdu_list[1]) is fits.CompImageHDU
            assert hdu_list[1].header["DAAXES"] == 2
            if len(stokes_params) == 1:
                assert "DNAXIS5" not in hdu_list[1].header
                assert hdu_list[1].header["DNAXIS"] == 4
                assert hdu_list[1].header["DEAXES"] == 2
            else:
                assert hdu_list[1].header["DNAXIS5"] == 4
                assert hdu_list[1].header["DNAXIS"] == 5
                assert hdu_list[1].header["DEAXES"] == 3
            assert hdu_list[1].header["INFO_URL"] == task.docs_base_url
            assert hdu_list[1].header["HEADVERS"] == spec_version
            assert (
                hdu_list[1].header["HEAD_URL"]
                == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
            )
            calvers = task._get_version_from_module_name()
            assert hdu_list[1].header["CALVERS"] == calvers
            assert (
                hdu_list[1].header["CAL_URL"]
                == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}"
            )
