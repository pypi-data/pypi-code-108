from dataclasses import asdict
from dataclasses import dataclass

import pytest

from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.tasks.vbi_base import VbiScienceTask
from dkist_processing_vbi.tests.conftest import FakeVbiConstants


@dataclass
class testing_constants(FakeVbiConstants):
    # Just add one constant from the common set to make sure
    instrument: str = "CHECK_OUT_THIS_INSTRUMENT"


@pytest.fixture(scope="session")
def expected_constant_dict() -> dict:
    lower_dict = asdict(FakeVbiConstants())
    return {k.upper(): v for k, v in lower_dict.items()}


@pytest.fixture(scope="function")
def vbi_science_task_with_constants(expected_constant_dict, recipe_run_id):
    class Task(VbiScienceTask):
        def run(self):
            ...

    task = Task(
        recipe_run_id=recipe_run_id,
        workflow_name="test_vbi_constants",
        workflow_version="VX.Y",
    )
    task.constants = VbiConstants(expected_constant_dict)

    yield task

    task._constants_db.purge()


def test_vbi_constants(vbi_science_task_with_constants, expected_constant_dict):
    """
    Given: A VbiScienceTask with a constants attribute
    When: Accessing specifici constants
    Then: The correct values are returned
    """
    task = vbi_science_task_with_constants
    for k, v in expected_constant_dict.items():
        if type(v) is tuple:
            v = list(v)  # Because dataclass

        raw_val = getattr(task.constants, k.lower())
        if type(raw_val) is tuple:
            raw_val = list(raw_val)  # Because dataclass

        assert raw_val == v
