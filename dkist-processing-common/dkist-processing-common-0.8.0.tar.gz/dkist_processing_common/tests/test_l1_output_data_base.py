from pathlib import Path

import pytest

from dkist_processing_common.tasks.l1_output_data import L1OutputDataBase
from dkist_processing_common.tests.conftest import FakeGQLClient


class L1OutputDataBaseTask(L1OutputDataBase):
    def run(self) -> None:
        ...


@pytest.fixture
def l1_output_data_base_task(recipe_run_id, mocker):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    proposal_id = "test_proposal_id"
    with L1OutputDataBaseTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task._constants_db["PROPOSAL_ID"] = proposal_id
        yield task, proposal_id
        task._constants_db.purge()


def test_format_object_key(l1_output_data_base_task):
    """
    :Given: a task based on L1OutputDataBase with a proposal ID in its constants mapping
    :When: formatting a path into an object key
    :Then: the proposal ID and filename are in the object key
    """
    task, proposal_id = l1_output_data_base_task
    filename = "test_filename.ext"
    path = Path(f"a/b/c/d/{filename}")
    assert proposal_id in task.format_object_key(path)
    assert filename in task.format_object_key(path)
    assert task.destination_bucket == "data"
