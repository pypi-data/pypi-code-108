import json
from datetime import datetime

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.science import ScienceCalibration
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import FakeVispConstants
from dkist_processing_visp.tests.conftest import generate_fits_frame
from dkist_processing_visp.tests.conftest import VispHeadersValidObserveFrames


@pytest.fixture(scope="function", params=["Full Stokes", "Stokes-I"])
def science_calibration_task(tmp_path, recipe_run_id, request, apply_mock_constants):
    num_dsps_repeats = 2
    num_beams = 2
    num_raster_steps = 2
    exposure_time = 0.02  # From VispHeadersValidObserveFrames fixture
    if request.param == "Full Stokes":
        num_modstates = 2
        correct_for_polarization = True
    else:
        num_modstates = 1
        correct_for_polarization = False
    mock_constants = FakeVispConstants(
        correct_for_polarization=correct_for_polarization,
        num_modstates=num_modstates,
        num_dsps_repeats=num_dsps_repeats,
        num_raster_steps=num_raster_steps,
        num_beams=num_beams,
        observe_exposure_times=(exposure_time,),
    )
    apply_mock_constants(mock_constants)

    with ScienceCalibration(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            all_zeros = np.zeros((10, 10))
            all_ones = np.ones((10, 10))
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )

            # Create fake demodulation matrices
            demod_matrices = np.zeros((1, 1, 4, num_modstates))
            for modstate in range(num_modstates):
                demod_matrices[0, 0, :, modstate] = [1, 2, 3, 4]
            for beam in range(num_beams):
                demod_hdul = fits.HDUList([fits.PrimaryHDU(data=demod_matrices)])
                task.fits_data_write(
                    hdu_list=demod_hdul,
                    tags=[
                        VispTag.intermediate(),
                        VispTag.task("DEMOD_MATRICES"),
                        VispTag.beam(beam + 1),
                    ],
                )

            # Create fake geometric objects
            angle = np.array([0.0])
            offset = np.array([0.0, 0.0])
            spec_shift = np.zeros(10)
            for beam in range(1, num_beams + 1):
                task.write_intermediate_arrays(arrays=angle, beam=beam, task="GEOMETRIC_ANGLE")
                task.write_intermediate_arrays(
                    arrays=spec_shift, beam=beam, task="GEOMETRIC_SPEC_SHIFTS"
                )
                for modstate in range(1, num_modstates + 1):
                    task.write_intermediate_arrays(
                        arrays=offset, beam=beam, modstate=modstate, task="GEOMETRIC_OFFSET"
                    )

            # Create fake dark intermediate arrays
            for beam in range(1, num_beams + 1):
                task.write_intermediate_arrays(
                    all_zeros, beam=beam, task="DARK", exposure_time=exposure_time
                )

            # Create fake solar_gain intermediate arrays
            for beam in range(1, num_beams + 1):
                for modstate in range(1, num_modstates + 1):
                    gain_hdul = fits.HDUList([fits.PrimaryHDU(data=all_ones)])
                    task.fits_data_write(
                        hdu_list=gain_hdul,
                        tags=[
                            VispTag.intermediate(),
                            VispTag.frame(),
                            VispTag.task("SOLAR_GAIN"),
                            VispTag.beam(beam),
                            VispTag.modstate(modstate),
                        ],
                    )

            # Create fake observe arrays
            start_time = datetime.now()
            for beam in range(1, num_beams + 1):
                for dsps_repeat in range(1, num_dsps_repeats + 1):
                    for raster_step in range(1, num_raster_steps + 1):
                        for modstate in range(1, num_modstates + 1):
                            ds = VispHeadersValidObserveFrames(
                                dataset_shape=(
                                    num_beams * num_dsps_repeats * num_raster_steps * num_modstates,
                                )
                                + (10, 10),
                                array_shape=(1, 10, 10),
                                time_delta=10,
                                num_dsps_repeats=num_dsps_repeats,
                                dsps_repeat=dsps_repeat,
                                num_raster_steps=num_raster_steps,
                                raster_step=raster_step,
                                num_modstates=num_modstates,
                                modstate=modstate,
                                start_time=start_time,
                            )
                            header_generator = (
                                spec122_validator.validate_and_translate_to_214_l0(
                                    d.header(), return_type=fits.HDUList
                                )[0].header
                                for d in ds
                            )

                            hdul = generate_fits_frame(header_generator=header_generator)
                            task.fits_data_write(
                                hdu_list=hdul,
                                tags=[
                                    VispTag.beam(beam),
                                    VispTag.task("OBSERVE"),
                                    VispTag.raster_step(raster_step),
                                    VispTag.dsps_repeat(dsps_repeat),
                                    VispTag.modstate(modstate),
                                    VispTag.input(),
                                    VispTag.frame(),
                                    VispTag.exposure_time(exposure_time),
                                ],
                            )

            yield task, request.param
        except:
            raise
        finally:
            task.scratch.purge()
            task._constants_db.purge()


def test_science_calibration_task(science_calibration_task, mocker):
    """
    Given: A ScienceCalibration task
    When: Calling the task instance
    Then: There are the expected number of science frames with the correct tags applied
    """

    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )

    # When
    task, polarization_mode = science_calibration_task
    task()

    # Then
    tags = [
        VispTag.calibrated(),
        VispTag.frame(),
    ]
    files = list(task.read(tags=tags))
    if polarization_mode == "Full Stokes":
        # 2 raster steps * 2 dsps repeats * 4 stokes params = 16 frames
        assert len(files) == 16
    elif polarization_mode == "Stokes-I":
        # 2 raster steps * 2 dsps repeats * 1 stokes param = 4 frames
        assert len(files) == 4
    for file in files:
        hdul = fits.open(file)
        assert hdul[0].data.shape == (1, 10, 10)  # 1 from re-dummification

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.count(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task("OBSERVE")]
            )
