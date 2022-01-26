from itertools import chain

import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tests.conftest import FakeGQLClient
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame
from dkist_processing_vbi.tests.conftest import Vbi122DarkFrames
from dkist_processing_vbi.tests.conftest import Vbi122GainFrames
from dkist_processing_vbi.tests.conftest import Vbi122ObserveFrames


@pytest.fixture(scope="function")
def parse_inputs_task(tmp_path, recipe_run_id):
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_program_types = 3
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.test_num_dsps_repeats = 2
        ds1 = Vbi122DarkFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
        )
        ds2 = Vbi122GainFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
        )
        ds3 = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_dsps_repeats,
        )
        ds = chain(ds1, ds2, ds3)
        header_generator = (d.header() for d in ds)
        for header in header_generator:
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.fits_data_write(hdu_list=hdul, tags=[VbiTag.input(), VbiTag.frame()])
        yield task
        task.scratch.purge()
        task.constants.purge()


@pytest.fixture(scope="function")
def parse_inputs_task_with_only_observe(tmp_path, recipe_run_id):
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path)
        task.num_program_types = 3
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.test_num_dsps_repeats = 2
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_dsps_repeats,
        )
        header_generator = (d.header() for d in ds)
        for header in header_generator:
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.fits_data_write(hdu_list=hdul, tags=[VbiTag.input(), VbiTag.frame()])
        yield task
        task.scratch.purge()
        task.constants.purge()


def test_parse_l0_input_data_spatial_pos(parse_inputs_task, mocker):
    """
    Given: a set of raw inputs of multiple task types and a ParseL0VbiInputData task
    When: the task is run
    Then: the input frames are correctly tagged by spatial position
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_task()

    for step in range(1, parse_inputs_task.num_steps + 1):
        translated_files = list(
            parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.frame(), VbiTag.spatial_step(step)])
        )
        assert (
            len(translated_files)
            == parse_inputs_task.num_exp_per_step
            * (parse_inputs_task.num_program_types - 1)  # for non observe frames
            + parse_inputs_task.num_exp_per_step
            * parse_inputs_task.num_dsps_repeats  # for observe frames
        )
        for filepath in translated_files:
            assert filepath.exists()


def test_parse_l0_input_constants(parse_inputs_task, mocker):
    """
    Given: a set of raw inputs of multiple task types and a ParseL0VbiInputData task
    When: the task is run
    Then: pipeline constants are correctly updated from the input headers
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_task()

    assert (
        parse_inputs_task.constants[VbiBudName.num_spatial_steps.value]
        == parse_inputs_task.num_steps
    )
    assert (
        parse_inputs_task.constants[BudName.num_dsps_repeats.value]
        == parse_inputs_task.num_dsps_repeats
    )
    assert parse_inputs_task.constants[BudName.spectral_line.value] == "VBI-Red H-alpha"


def test_parse_l0_input_frames_found(parse_inputs_task, mocker):
    """
    Given: a set of raw inputs of multiple task types and a ParseL0VbiInputData task
    When: the task is run
    Then: the frames from each task type are correctly identified and tagged
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_task()
    assert (
        len(list(parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.task("DARK")])))
        == parse_inputs_task.num_steps * parse_inputs_task.num_exp_per_step
    )
    assert (
        len(list(parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.task("GAIN")])))
        == parse_inputs_task.num_steps * parse_inputs_task.num_exp_per_step
    )

    assert (
        len(list(parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.task("OBSERVE")])))
        == parse_inputs_task.num_steps
        * parse_inputs_task.num_exp_per_step
        * parse_inputs_task.test_num_dsps_repeats
    )


def test_parse_l0_input_with_only_observe(parse_inputs_task, mocker):
    """
    Given: a set of raw inputs of a single task type and a ParseL0VbiInputData task
    When: the task is run
    Then: the observe frames are correctly identified and tagged
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_task()
    assert (
        len(list(parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.task("OBSERVE")])))
        == parse_inputs_task.num_steps
        * parse_inputs_task.num_exp_per_step
        * parse_inputs_task.test_num_dsps_repeats
    )
