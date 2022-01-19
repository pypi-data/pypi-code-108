import json
from unittest.mock import PropertyMock

import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.quality_metrics import VispQualityMetrics
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import generate_214_l1_fits_frame
from dkist_processing_visp.tests.conftest import Visp122ObserveFrames


@pytest.fixture(scope="function")
def visp_quality_task(tmp_path, recipe_run_id, mocker):
    with VispQualityMetrics(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        num_dsps_repeats = 3
        num_raster_steps = 2
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path)

        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.correct_for_polarization",
            new_callable=PropertyMock,
            return_value=True,
        )

        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.num_dsps_repeats",
            new_callable=PropertyMock,
            return_value=num_dsps_repeats,
        )
        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.num_raster_steps",
            new_callable=PropertyMock,
            return_value=num_raster_steps,
        )

        # Create fake stokes frames
        for dsps_repeat in range(1, num_dsps_repeats + 1):
            for raster_step in range(1, num_raster_steps + 1):
                for stokes_param, index in zip(("I", "Q", "U", "V"), (1, 2, 3, 4)):
                    ds = Visp122ObserveFrames(
                        array_shape=(1, 10, 10),
                        num_steps=num_raster_steps,
                        num_dsps_repeats=num_dsps_repeats,
                    )
                    header_generator = (
                        spec122_validator.validate_and_translate_to_214_l0(
                            d.header(), return_type=fits.HDUList
                        )[0].header
                        for d in ds
                    )

                    hdul = generate_214_l1_fits_frame(s122_header=next(header_generator))
                    hdul[1].header["DINDEX5"] = index
                    task.fits_data_write(
                        hdu_list=hdul,
                        tags=[
                            VispTag.output(),
                            VispTag.frame(),
                            VispTag.stokes(stokes_param),
                            VispTag.raster_step(raster_step),
                            VispTag.dsps_repeat(dsps_repeat),
                        ],
                    )

        yield task
        task.scratch.purge()
        task.constants.purge()


def test_quality_task(visp_quality_task, mocker):
    """
    Given: A VISPQualityMetrics task
    When: Calling the task instance
    Then: A single polarimetric noise measurement and datetime is recorded for each dsps repeat for each Stokes Q, U, and V,
            and a single polarimetric sensitivity measurement and datetime is recorded for each dsps repeat for each Stokes Q, U, and V
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    # When
    task = visp_quality_task
    task()
    # Then
    num_dsps_repeats = task.num_dsps_repeats
    polarimetric_noise_files = list(task.read(tags=[Tag.quality("POLARIMETRIC_NOISE")]))
    assert len(polarimetric_noise_files) == 3
    for file in polarimetric_noise_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            for time in range(len(data["x_values"])):
                assert type(data["x_values"][time]) == str
            for noise in range(len(data["y_values"])):
                assert type(data["y_values"][noise]) == float
            assert len(data["x_values"]) == len(data["y_values"]) == num_dsps_repeats

    polarimetric_sens_files = list(task.read(tags=[Tag.quality("POLARIMETRIC_SENSITIVITY")]))
    assert len(polarimetric_sens_files) == 1
    with polarimetric_sens_files[0].open() as f:
        data = json.load(f)
        assert isinstance(data, dict)
        for time in range(len(data["x_values"])):
            assert type(data["x_values"][time]) == str
        for noise in range(len(data["y_values"])):
            assert type(data["y_values"][noise]) == float
        assert len(data["x_values"]) == len(data["y_values"]) == num_dsps_repeats
