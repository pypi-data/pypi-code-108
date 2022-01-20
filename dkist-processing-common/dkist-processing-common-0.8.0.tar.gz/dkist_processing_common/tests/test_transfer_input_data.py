import json
from pathlib import Path
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.transfer_input_data import TransferL0Data


@pytest.fixture
def transfer_l0_data(recipe_run_id, tmp_path):
    bucket_name = "transfer_l0_bucket"
    task = TransferL0Data(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    )
    task.scratch = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        scratch_base_path=tmp_path,
    )
    task.scratch.scratch_base_path = tmp_path
    file_path = task.scratch.workflow_base_path / Path(f"{uuid4().hex[:6]}.ext")
    input_dataset = {
        "bucket": bucket_name,
        "parameters": [
            {
                "parameterName": "param_name",
                "parameterValues": [
                    {
                        "parameterValueId": 1,
                        "parameterValue": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                        "parameterValueStartDate": "2000-01-01",
                    }
                ],
            }
        ],
        "frames": [
            Path("objectkey1").as_posix(),
            Path("objectkey2").as_posix(),
            Path("objectkey3").as_posix(),
        ],
    }
    file_path.write_text(data=json.dumps(input_dataset))
    task.tag(path=file_path, tags=Tag.input_dataset())
    yield task, input_dataset
    task.scratch.purge()


def test_format_transfer_items(transfer_l0_data):
    """
    :Given: a TransferL0Data task with a valid input dataset
    :When: formatting items in the input dataset for transfer
    :Then: the items are correctly loaded into GlobusTransferItem objects
    """
    task, input_dataset = transfer_l0_data
    filenames = [Path(frame).name for frame in input_dataset["frames"]]
    assert len(task.format_transfer_items()) == len(input_dataset["frames"])
    for item in task.format_transfer_items():
        assert item.source_path.as_posix() in [
            "/" + input_dataset["bucket"] + "/" + frame for frame in input_dataset["frames"]
        ]
        assert item.destination_path.name in filenames
        assert not item.recursive
