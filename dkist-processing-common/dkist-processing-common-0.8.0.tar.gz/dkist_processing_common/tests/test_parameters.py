import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import ScienceTaskL0ToL1Base
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin
from dkist_processing_common.tests.conftest import InputDatasetTask
from dkist_processing_common.tests.test_input_dataset import INPUT_DATASET

INPUT_DATASET_PARAMETERS_ONLY_NO_DATE = {
    "parameters": [
        {
            "parameterName": "param_name",
            "parameterValues": [{"parameterValueId": 1, "parameterValue": json.dumps(4)}],
        }
    ]
}

INPUT_DATASET_PARAMETERS_ONLY_TWO_VALUES = {
    "parameters": [
        {
            "parameterName": "param_name",
            "parameterValues": [
                {
                    "parameterValueId": 1,
                    "parameterValue": json.dumps(4),
                    "parameterValueStartDate": "2020-03-13",
                },
                {
                    "parameterValueId": 2,
                    "parameterValue": json.dumps(6),
                    "parameterValueStartDate": "1955-01-02",
                },
                {
                    "parameterValueId": 3,
                    "parameterValue": json.dumps(5),
                    "parameterValueStartDate": "2021-12-15",
                },
            ],
        }
    ]
}
INPUT_DATASET_PARAMETERS_ONLY_TWO_VALUES_NO_DATE = {
    "parameters": [
        {
            "parameterName": "param_name",
            "parameterValues": [
                {"parameterValueId": 1, "parameterValue": json.dumps(4)},
                {
                    "parameterValueId": 2,
                    "parameterValue": json.dumps(6),
                    "parameterValueStartDate": "1955-01-02",
                },
            ],
        }
    ]
}


class FilledParameters(ParameterBase):
    @property
    def test_parameter(self):
        return self._find_most_recent_past_value("param_name")


@pytest.fixture()
def construct_parameters(construct_task_with_input_dataset):
    def make_parameters(input_dataset_dict):
        task = next(construct_task_with_input_dataset(input_dataset_dict))[0]
        return FilledParameters(task.input_dataset_parameters)

    return make_parameters


class ParameterScienceTask(ScienceTaskL0ToL1Base, InputDatasetMixin):
    """ An example of how parameters will be used in instrument repos """

    def __init__(self, recipe_run_id: int, workflow_name: str, workflow_version: str):
        super().__init__(recipe_run_id, workflow_name, workflow_version)
        self.parameters = FilledParameters(self.input_dataset_parameters)

    def run(self) -> None:
        pass


@pytest.fixture()
def task_with_parameters(recipe_run_id, tmp_path):
    try:
        tagger = InputDatasetTask(
            recipe_run_id=recipe_run_id,
            workflow_name="workflow_name",
            workflow_version="workflow_version",
        )
        tagger.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        tagger.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
        file_path = tagger.scratch.workflow_base_path / Path(f"{uuid4().hex[:6]}.ext")
        file_path.write_text(data=json.dumps(INPUT_DATASET))
        tagger.tag(path=file_path, tags=Tag.input_dataset())

        task = (
            ParameterScienceTask(  # These arguments ensure that the tagger and task share databases
                recipe_run_id=recipe_run_id,
                workflow_name="workflow_name",
                workflow_version="workflow_version",
            )
        )
        yield task
    except:
        raise
    finally:
        tagger.scratch.purge()
        tagger._constants_db.purge()


def test_parameters(construct_parameters):
    """
    Given: a ParameterBase subclass with populated parameters
    When: asking for a specific parameter value
    Then: the correct value is returned
    """
    parameters = construct_parameters(INPUT_DATASET)
    assert parameters.test_parameter == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


def test_find_most_recent_date_out_of_range(construct_parameters):
    """
    Given: a ParameterBase subclass with populated parameters
    When: asking for a specific parameter value at a time that is too far in the past
    Then: an error is raised
    """
    parameters = construct_parameters(INPUT_DATASET)
    with pytest.raises(ValueError):
        _ = parameters._find_most_recent_past_value("param_name", start_date=datetime(1776, 7, 4))


def test_parameters_get_no_startdate(construct_parameters):
    """
    Given: a ParameterBase subclass initialized with a parameter with no start_date
    When: asking for that specific parameter
    Then: the correct value is returned
    """
    parameters = construct_parameters(INPUT_DATASET_PARAMETERS_ONLY_NO_DATE)
    assert parameters.test_parameter == 4


def test_find_most_recent_multiple_dates(construct_parameters):
    """
    Given: a ParameterBase subclass with a parameter with multiple values
    When: asking for that specific parameter
    Then: the correct (i.e., most recent) value is returned
    """
    parameters = construct_parameters(INPUT_DATASET_PARAMETERS_ONLY_TWO_VALUES)
    assert (
        parameters._find_most_recent_past_value("param_name", start_date=datetime(2021, 1, 1)) == 4
    )


def test_parameter_get_multiple_values_no_start_date(construct_parameters):
    """
    Given: a ParameterBase subclass with a parameter with multiple values, one of which has no start date
    When: asking for that specific parameter
    Then: the value with *any* date is returned
    """
    parameters = construct_parameters(INPUT_DATASET_PARAMETERS_ONLY_TWO_VALUES_NO_DATE)
    assert parameters.test_parameter == 6


def test_parameters_on_task(task_with_parameters):
    """
    Given: a Task that inits a ParameterBase subclass
    When: asking for a parameter
    Then: the correct value is returned
    """
    assert task_with_parameters.parameters.test_parameter == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
