from datetime import datetime

import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.make_movie_frames import MakeVispMovieFrames
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import generate_fits_frame
from dkist_processing_visp.tests.conftest import VispHeadersValidObserveFrames


@pytest.fixture(scope="function")
def movie_frames_task(tmp_path, recipe_run_id):
    with MakeVispMovieFrames(
        recipe_run_id=recipe_run_id, workflow_name="make_movie_frames", workflow_version="VX.Y"
    ) as task:
        task.steps = 3
        task.dsps_repeats = 2
        task.axis_length = 3
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        start_time = datetime.now()
        for stokes_state in ["I", "Q", "U", "V"]:
            for dsps_repeat in range(1, task.dsps_repeats + 1):
                for step in range(1, task.steps + 1):
                    ds = VispHeadersValidObserveFrames(
                        dataset_shape=(2, task.axis_length, task.axis_length),
                        array_shape=(1, task.axis_length, task.axis_length),
                        time_delta=10,
                        num_dsps_repeats=task.dsps_repeats,
                        dsps_repeat=dsps_repeat,
                        num_raster_steps=task.steps,
                        raster_step=step,
                        num_modstates=1,
                        modstate=1,
                        start_time=start_time,
                    )
                    header_generator = (
                        spec122_validator.validate_and_translate_to_214_l0(
                            d.header(), return_type=fits.HDUList
                        )[0].header
                        for d in ds
                    )
                    hdul = generate_fits_frame(header_generator=header_generator, shape=(1, 3, 3))
                    task.fits_data_write(
                        hdu_list=hdul,
                        tags=[
                            VispTag.output(),
                            VispTag.frame(),
                            VispTag.dsps_repeat(dsps_repeat),
                            VispTag.raster_step(step),
                            VispTag.stokes(stokes_state),
                        ],
                    )
        task.constants[BudName.num_dsps_repeats.value] = task.dsps_repeats
        task.constants[VispBudName.num_raster_steps.value] = task.steps
        yield task
        task.scratch.purge()
        task.constants.purge()


def test_make_movie_frames(movie_frames_task, mocker):
    """
    Given: A MakeVispMovieFrames task
    When: Calling the task instance
    Then: a fits file is made for each raster scan containing the movie frame for that scan
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    task = movie_frames_task
    task()
    assert len(list(task.read(tags=[VispTag.movie_frame()]))) == task.dsps_repeats
    for filepath in task.read(tags=[VispTag.movie_frame()]):
        assert filepath.exists()
        hdul = fits.open(filepath)
        assert hdul[0].header["INSTRUME"] == "VISP"
        # Multiple by 2 because a single map is (axis_length, steps) but there are 4 stokes in a 2x2 array
        assert hdul[0].data.shape == (task.axis_length * 2, task.steps * 2)
