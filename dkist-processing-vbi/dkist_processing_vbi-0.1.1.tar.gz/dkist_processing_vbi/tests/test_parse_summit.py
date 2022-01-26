"""
This might be a totally redundant test. Leave it in for now.
"""
from itertools import chain

import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tests.conftest import FakeGQLClient
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame
from dkist_processing_vbi.tests.conftest import Vbi122DarkFrames
from dkist_processing_vbi.tests.conftest import Vbi122SummitObserveFrames


@pytest.fixture(scope="function")
def parse_summit_processed_task(tmp_path, recipe_run_id):
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_summit_processed",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.test_num_dsps_repeats = 1
        ds0 = Vbi122SummitObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_dsps_repeats,
        )
        ds1 = Vbi122DarkFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
        )
        ds = chain(ds0, ds1)
        header_generator = (d.header() for d in ds)
        for header in header_generator:
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.fits_data_write(hdu_list=hdul, tags=[VbiTag.input(), VbiTag.frame()])
        yield task
        task.scratch.purge()
        task.constants.purge()


def test_parse_summit_proccessed_data(parse_summit_processed_task, mocker):
    """
    Given: a set of raw inputs of summit-processed data and a ParseL0VbiInputData task
    When: the task is run
    Then: the observe frames are correctly identified and tagged
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_summit_processed_task()

    for step in range(1, parse_summit_processed_task.num_steps + 1):
        translated_files = list(
            parse_summit_processed_task.read(
                tags=[
                    VbiTag.input(),
                    VbiTag.frame(),
                    VbiTag.task("OBSERVE"),
                    VbiTag.spatial_step(step),
                ]
            )
        )
        assert len(translated_files) == parse_summit_processed_task.num_exp_per_step
        for filepath in translated_files:
            assert filepath.exists()
