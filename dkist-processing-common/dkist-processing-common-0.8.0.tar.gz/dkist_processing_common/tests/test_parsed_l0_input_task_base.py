from string import ascii_uppercase

import pytest
from hashids import Hashids
from hypothesis import given
from hypothesis.strategies import integers

from dkist_processing_common.tasks.base import ParsedL0InputTaskBase


class Task(ParsedL0InputTaskBase):
    def run(self):
        pass


@pytest.fixture
def parsed_l0(recipe_run_id):
    proposal_id = "proposal_id"
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task._constants_db["PROPOSAL_ID"] = proposal_id
        yield task, proposal_id
        task._constants_db.purge()


def test_proposal_id(parsed_l0):
    """
    Given: a ParsedL0InputTaskBase task
    When: getting the proposal id
    Then: the proposal id from the constants mutable mapping is returned
    """
    task, proposal_id = parsed_l0
    task()
    assert task.constants.proposal_id == proposal_id


def test_dataset_id(parsed_l0):
    """
    Given: a ParsedL0InputTaskBase task
    When: getting the dataset id
    Then: the dataset id hashed from the recipe run id is returned
    """
    task, _ = parsed_l0
    assert task.dataset_id == Hashids(min_length=5, alphabet=ascii_uppercase).encode(
        task.recipe_run_id
    )


@given(
    id_x=integers(min_value=1, max_value=2147483647),
    id_y=integers(min_value=1, max_value=2147483647),
)
def test_dataset_id_uniquely_generated_from_recipe_run_id(id_x, id_y):
    """
    Given: 2 integers > 0
    When: 2 tasks are created using the integers for each of the tasks
    Then: The dataset_id for each class compares the same as the integers compare
       e.g. (1 == 1) is (dataset_id(1) == dataset_id(1))  : True is True
       e.g. (1 == 2) == (dataset_id(1) == dataset_id(2))  : False is False
    """
    expected = id_x == id_y
    task_x = Task(recipe_run_id=id_x, workflow_name="", workflow_version="")
    task_y = Task(recipe_run_id=id_y, workflow_name="", workflow_version="")
    actual = task_x.dataset_id == task_y.dataset_id
    assert expected is actual


@given(id_x=integers(min_value=1, max_value=2147483647))
def test_dataset_id_from_recipe_run_id_produces_the_same_value(id_x):
    """
    Given: an integer > 0
    When: 2 tasks are created using the same integer for each of the tasks
    Then: The dataset_id for each class are equal
    """
    task_1 = Task(recipe_run_id=id_x, workflow_name="", workflow_version="")
    task_2 = Task(recipe_run_id=id_x, workflow_name="", workflow_version="")
    assert task_1.dataset_id == task_2.dataset_id
