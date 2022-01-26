from random import randint

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.tasks import ScienceTaskL0ToL1Base

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.mixin.intermediate_loaders import IntermediateLoaderMixin


@pytest.fixture(scope="module")
def science_task_with_intermediates(tmp_path_factory):
    class DummyTask(ScienceTaskL0ToL1Base, IntermediateLoaderMixin):
        def run(self):
            pass

    recipe_run_id = randint(0, 99999)
    with DummyTask(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_dummy_task",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(
            scratch_base_path=tmp_path_factory.mktemp("scratch"), recipe_run_id=recipe_run_id
        )
        task.num_steps = 4
        exp_times = [1.0, 10.0]
        for s in range(1, task.num_steps + 1):
            for e in exp_times:
                dark_cal = np.zeros((10, 10)) + (s * 10) * e
                dark_hdul = fits.HDUList([fits.PrimaryHDU(data=dark_cal)])
                task.fits_data_write(
                    hdu_list=dark_hdul,
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.frame(),
                        VbiTag.task("DARK"),
                        VbiTag.spatial_step(s),
                        VbiTag.exposure_time(e),
                    ],
                )

            gain_cal = np.zeros((10, 10)) + (s + 1)
            gain_hdul = fits.HDUList([fits.PrimaryHDU(data=gain_cal)])
            task.fits_data_write(
                hdu_list=gain_hdul,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.frame(),
                    VbiTag.task("GAIN"),
                    VbiTag.spatial_step(s),
                ],
            )

        yield task
        task.scratch.purge()
        task.constants.purge()


@pytest.mark.parametrize(
    "step, exp_time",
    [
        pytest.param(1, 1, id="step 1 exp 1"),
        pytest.param(2, 1, id="step 2 exp 1"),
        pytest.param(3, 1, id="step 3 exp 1"),
        pytest.param(4, 1, id="step 4 exp 1"),
        pytest.param(1, 10, id="step 1 exp 10"),
        pytest.param(2, 10, id="step 2 exp 10"),
        pytest.param(3, 10, id="step 3 exp 10"),
        pytest.param(4, 10, id="step 4 exp 10"),
    ],
)
def test_intermediate_dark(science_task_with_intermediates, step, exp_time):
    """
    Given: A task with some intermediate frames and an IntermediateLoaderMixin
    When: Asking for the intermediate dark calibration for a single step
    Then: The correct array is returned
    """
    truth = np.zeros((10, 10)) + (step * 10) * exp_time
    np.testing.assert_equal(
        truth,
        science_task_with_intermediates.intermediate_dark_array(
            spatial_step=step, exposure_time=exp_time
        ),
    )


@pytest.mark.parametrize(
    "step",
    [
        pytest.param(1, id="step 1"),
        pytest.param(2, id="step 2"),
        pytest.param(3, id="step 3"),
        pytest.param(4, id="step 4"),
    ],
)
def test_intermediate_gain(science_task_with_intermediates, step):
    """
    Given: A task with some intermediate frames and an IntermediateLoaderMixin
    When: Asking for the intermediate gain calibration for a single step
    Then: The correct array is returned
    """
    truth = np.zeros((10, 10)) + (step + 1)
    np.testing.assert_equal(truth, science_task_with_intermediates.intermediate_gain_array(step))
