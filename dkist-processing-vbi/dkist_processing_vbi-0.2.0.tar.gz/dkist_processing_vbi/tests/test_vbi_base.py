from unittest.mock import PropertyMock

import pytest

from dkist_processing_vbi.tasks.vbi_base import VbiScienceTask


@pytest.fixture
def expected_constants_dict():
    # Just make up a super simple db with a single constant that vbi uses
    return {"NUM_SPATIAL_STEPS": 4}


@pytest.fixture(scope="function")
def vbi_science_task(recipe_run_id, mocker, expected_constants_dict):
    class DummyTask(VbiScienceTask):
        def run(self):
            pass

    mocker.patch(
        "dkist_processing_common.tasks.base.ConstantsDb",
        new_callable=PropertyMock,
        return_value=expected_constants_dict,
    )
    task = DummyTask(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_dummy_task",
        workflow_version="VX.Y",
    )

    yield task
    task.scratch.purge()
    # No need to purge the _constants_db because we mocked it to just a dict


def test_constants_init(vbi_science_task, expected_constants_dict):
    """
    Given: A VbiScienceTask with a populated backend ConstantsDb
    When: Initializing the task
    Then: The .constants attribute is loaded correctly
    """
    constants_obj = vbi_science_task.constants
    for k, v in expected_constants_dict.items():
        assert getattr(constants_obj, k.lower()) == v
