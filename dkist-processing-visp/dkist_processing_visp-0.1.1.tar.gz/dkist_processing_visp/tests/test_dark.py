import json
from unittest.mock import PropertyMock

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.dark import DarkCalibration
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import generate_fits_frame
from dkist_processing_visp.tests.conftest import VispHeadersValidDarkFrames


@pytest.fixture(scope="function")
def dark_calibration_task(tmp_path, recipe_run_id, mocker):
    with DarkCalibration(
        recipe_run_id=recipe_run_id, workflow_name="dark_calibration", workflow_version="VX.Y"
    ) as task:
        num_beam = 2
        exp_times = [0.01, 1.0, 100.0]
        unused_time = 200.0
        num_exp_time = len(exp_times)
        num_frames_per = 3
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.correct_for_polarization",
            new_callable=PropertyMock,
            return_value=True,
        )
        task.constants.update(
            {
                VispBudName.lamp_exposure_times.value: [100.0],
                VispBudName.solar_exposure_times.value: [1.0],
                VispBudName.observe_exposure_times.value: [0.01],
                VispBudName.polcal_exposure_times.value: [],
            }
        )
        ds = VispHeadersValidDarkFrames(
            dataset_shape=(num_beam * (num_exp_time + 1) * num_frames_per, 10, 10),
            array_shape=(1, 10, 10),
            time_delta=10,
        )
        header_generator = (
            spec122_validator.validate_and_translate_to_214_l0(
                d.header(), return_type=fits.HDUList
            )[0].header
            for d in ds
        )
        for b in range(num_beam):
            for e in exp_times + [unused_time]:  # Make some darks we won't use
                for _ in range(num_frames_per):
                    hdul = generate_fits_frame(header_generator=header_generator)
                    hdul[0].data *= 0
                    hdul[0].data += (b + 1) * e
                    task.fits_data_write(
                        hdu_list=hdul,
                        tags=[
                            VispTag.input(),
                            VispTag.frame(),
                            VispTag.task("DARK"),
                            VispTag.beam(b + 1),
                            VispTag.exposure_time(e),
                        ],
                    )
        yield task, num_beam, exp_times, unused_time
        task.scratch.purge()
        task.constants.purge()


def test_dark_calibration_task(dark_calibration_task, mocker):
    """
    Given: A DarkCalibration task with multiple task exposure times
    When: Calling the task instance
    Then: Only one average intermediate dark frame exists for each exposure time and unused times are not made
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    # When
    task, num_beam, exp_times, unused_time = dark_calibration_task
    task()
    # Then
    for e in exp_times:
        for b in range(num_beam):
            files = list(
                task.read(
                    tags=[
                        VispTag.task("DARK"),
                        VispTag.intermediate(),
                        VispTag.frame(),
                        VispTag.beam(b + 1),
                        VispTag.exposure_time(e),
                    ]
                )
            )
            assert len(files) == 1
            expected = np.ones((10, 10)) * (b + 1) * e
            hdul = fits.open(files[0])
            np.testing.assert_equal(expected, hdul[0].data)
            hdul.close()

    unused_time_read = task.read(
        tags=[
            VispTag.task("DARK"),
            VispTag.intermediate(),
            VispTag.frame(),
            VispTag.exposure_time(unused_time),
        ]
    )
    assert len(list(unused_time_read)) == 0

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.count(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task("DARK")]
            )
