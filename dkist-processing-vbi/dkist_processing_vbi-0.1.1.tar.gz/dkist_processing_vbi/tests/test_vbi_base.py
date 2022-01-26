import pytest
from dkist_processing_common.models.constants import BudName

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.vbi_base import VbiScienceTask


@pytest.fixture(scope="function")
def vbi_science_task(recipe_run_id):
    class DummyTask(VbiScienceTask):
        def run(self):
            pass

    with DummyTask(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_dummy_task",
        workflow_version="VX.Y",
    ) as task:

        task.constants[VbiBudName.num_spatial_steps.value] = 9
        task.constants[BudName.num_dsps_repeats.value] = 4

        yield task
        task.scratch.purge()
        task.constants.purge()


def test_num_spatial_steps(vbi_science_task):
    """
    Given: A VbiScienceTask with populated constants
    When: Accessing the number of spatial steps property
    Then: The correct number is returned
    """
    assert vbi_science_task.num_spatial_steps == 9


def test_num_dsps_repeats(vbi_science_task):
    """
    Given: A VbiScienceTask with populated constants
    When: Accessing the number of dsps repeats property
    Then: The correct number is returned
    """
    assert vbi_science_task.num_dsps_repeats == 4
