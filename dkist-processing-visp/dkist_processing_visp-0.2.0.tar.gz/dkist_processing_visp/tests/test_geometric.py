import json

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_math import transform

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.geometric import GeometricCalibration
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import FakeVispConstants
from dkist_processing_visp.tests.conftest import generate_214_l0_fits_frame
from dkist_processing_visp.tests.conftest import VispHeadersValidSolarGainFrames


@pytest.fixture(scope="function")
def geometric_calibration_task_that_completes(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, apply_mock_constants
):
    # This fixture makes data that look enough like real data that all of the feature detection stuff at least runs
    # through (mostly this is an issue for the angle calculation). It would be great to contrive data that
    # produce a geometric calibration with real numbers that can be checked, but for now we'll rely on the grogu
    # tests for that. In other words, this fixture just tests if the machinery of the task completes and some object
    # (ANY object) is written correctly.
    number_of_modstates = 3
    number_of_beams = 2
    exposure_time = 20.0  # From VispHeadersValidSolarGainFrames fixture
    mock_constants = FakeVispConstants(
        num_modstates=number_of_modstates, solar_exposure_times=(exposure_time,)
    )
    apply_mock_constants(mock_constants)
    with GeometricCalibration(
        recipe_run_id=recipe_run_id, workflow_name="geometric_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            assign_input_dataset_doc_to_task(task)
            task.angles = np.array([0.0, 0.0])
            task.offsets = np.zeros((number_of_beams, number_of_modstates, 2))
            task.shifts = np.zeros(30)
            for beam in range(1, number_of_beams + 1):

                dark_cal = np.ones((30, 30)) * 3.0
                task.write_intermediate_arrays(
                    arrays=dark_cal, beam=beam, task="DARK", exposure_time=exposure_time
                )

                for modstate in range(1, number_of_modstates + 1):
                    lamp_cal = np.ones((30, 30)) * 10 * modstate * beam
                    task.write_intermediate_arrays(
                        arrays=lamp_cal, beam=beam, modstate=modstate, task="LAMP_GAIN"
                    )

                    ds = VispHeadersValidSolarGainFrames(
                        dataset_shape=(1, 30, 30),
                        array_shape=(1, 30, 30),
                        time_delta=10,
                        num_modstates=number_of_modstates,
                        modstate=modstate,
                    )
                    header = ds.header()
                    true_solar = 10 * (np.ones((30, 30)) + modstate + beam)
                    translated = next(
                        transform.translate_arrays(
                            arrays=true_solar, translation=task.offsets[beam - 1][modstate - 1]
                        )
                    )
                    translated[translated == 0] = 10 * (modstate + beam + 1)
                    translated[:, 10] = 5.0
                    distorted_solar = next(
                        transform.rotate_arrays_about_point(
                            arrays=translated, angle=task.angles[beam - 1]
                        )
                    )
                    raw_solar = (distorted_solar * lamp_cal) + dark_cal
                    solar_hdul = generate_214_l0_fits_frame(data=raw_solar, s122_header=header)
                    task.fits_data_write(
                        hdu_list=solar_hdul,
                        tags=[
                            VispTag.input(),
                            VispTag.task("SOLAR_GAIN"),
                            VispTag.modstate(modstate),
                            VispTag.frame(),
                            VispTag.beam(beam),
                            VispTag.exposure_time(exposure_time),
                        ],
                    )

            yield task
        except:
            raise
        finally:
            task.scratch.purge()
            task._constants_db.purge()


@pytest.fixture(scope="function")
def geometric_calibration_task_with_simple_raw_data(tmp_path, recipe_run_id, apply_mock_constants):
    number_of_modstates = 3
    number_of_beams = 2
    exposure_time = 20.0  # From VispHeadersValidSolarGainFrames fixture
    data_shape = (10, 10)
    mock_constants = FakeVispConstants(
        num_modstates=number_of_modstates, solar_exposure_times=(exposure_time,)
    )
    apply_mock_constants(mock_constants)
    with GeometricCalibration(
        recipe_run_id=recipe_run_id, workflow_name="geometric_calibration", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        for beam in range(1, number_of_beams + 1):

            dark_cal = np.ones(data_shape) * 3.0
            task.write_intermediate_arrays(
                arrays=dark_cal, beam=beam, task="DARK", exposure_time=exposure_time
            )

            # Let's write a dark with the wrong exposure time, just to make sure it doesn't get used
            task.write_intermediate_arrays(
                arrays=np.ones(data_shape) * 1e6,
                beam=beam,
                task="DARK",
                exposure_time=exposure_time ** 2,
            )

            for modstate in range(1, number_of_modstates + 1):
                lamp_cal = np.ones(data_shape) * 10 * modstate * beam
                task.write_intermediate_arrays(
                    arrays=lamp_cal, beam=beam, modstate=modstate, task="LAMP_GAIN"
                )

                ds = VispHeadersValidSolarGainFrames(
                    dataset_shape=(1,) + data_shape,
                    array_shape=(1,) + data_shape,
                    time_delta=10,
                    num_modstates=number_of_modstates,
                    modstate=modstate,
                )
                header = ds.header()
                true_solar = np.ones(data_shape) + modstate + beam
                raw_solar = (true_solar * lamp_cal) + dark_cal
                solar_hdul = generate_214_l0_fits_frame(data=raw_solar, s122_header=header)
                task.fits_data_write(
                    hdu_list=solar_hdul,
                    tags=[
                        VispTag.input(),
                        VispTag.task("SOLAR_GAIN"),
                        VispTag.modstate(modstate),
                        VispTag.frame(),
                        VispTag.beam(beam),
                        VispTag.exposure_time(exposure_time),
                    ],
                )

        yield task
        task.scratch.purge()
        task._constants_db.purge()


def test_geometric_task(geometric_calibration_task_that_completes, mocker):
    """
    Given: A set of raw solar gain images and necessary intermediate calibrations
    When: Running the geometric task
    Then: The damn thing runs and makes outputs that at least are the right type
    """
    # See the note in the fixture above: this test does NOT test for accuracy of the calibration
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    task = geometric_calibration_task_that_completes
    task()
    for beam in range(1, task.constants.num_beams + 1):
        assert type(task.get_angle(beam=beam)) is np.float64
        assert task.get_spec_shift(beam=beam).shape == (30,)
        for modstate in range(1, task.constants.num_modstates + 1):
            assert task.get_state_offset(beam=beam, modstate=modstate).shape == (2,)

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.count(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task("SOLAR_GAIN")]
            )


def test_basic_corrections(geometric_calibration_task_with_simple_raw_data):
    """
    Given: A set of raw solar gain images and necessary intermediate calibrations
    When: Doing basic dark and lamp gain corrections
    Then: The corrections are applied correctly
    """
    task = geometric_calibration_task_with_simple_raw_data
    task.do_basic_corrections()
    for beam in range(1, task.constants.num_beams + 1):
        for modstate in range(1, task.constants.num_modstates + 1):
            expected = np.ones((10, 10)) + modstate + beam
            array = task.basic_corrected_data(beam=beam, modstate=modstate)
            np.testing.assert_equal(expected, array)
