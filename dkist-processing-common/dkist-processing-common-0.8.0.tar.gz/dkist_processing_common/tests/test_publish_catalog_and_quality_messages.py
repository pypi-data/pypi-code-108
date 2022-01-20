from pathlib import Path

import pytest

from dkist_processing_common.models.message import CreateQualityReportMessage
from dkist_processing_common.tasks.l1_output_data import PublishCatalogAndQualityMessages
from dkist_processing_common.tests.conftest import FakeGQLClient


@pytest.fixture
def publish_catalog_and_quality_messages_task(recipe_run_id, mocker):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    with PublishCatalogAndQualityMessages(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        proposal_id = "publish_catalog_messages_proposal_id"
        task._constants_db["PROPOSAL_ID"] = proposal_id
        yield task, proposal_id
        task._constants_db.purge()


def test_frame_messages(publish_catalog_and_quality_messages_task):
    """
    :Given: a PublishCatalogAndQualityMessages task
    :When: creating frame messages
    :Then: the attributes are correctly populated
    """
    task, proposal_id = publish_catalog_and_quality_messages_task
    filenames = [f"test_frame_{i}.ext" for i in range(10)]
    print(filenames)
    filepaths = [Path(f"a/b/c/{filename}") for filename in filenames]
    frame_messages = task.frame_messages(paths=filepaths)
    for message in frame_messages:
        assert message.bucket == "data"
        assert proposal_id in message.objectName
        assert message.conversationId == str(task.recipe_run_id)


def test_object_messages(publish_catalog_and_quality_messages_task):
    """
    :Given: a PublishCatalogAndQualityMessages task
    :When: creating object messages
    :Then: the attributes are correctly populated
    """
    task, proposal_id = publish_catalog_and_quality_messages_task
    object_type = "test_type"
    filenames = [f"test_object_{i}.ext" for i in range(10)]
    print(filenames)
    filepaths = [Path(f"a/b/c/{filename}") for filename in filenames]
    object_messages = task.object_messages(paths=filepaths, object_type=object_type)
    for message in object_messages:
        assert message.bucket == "data"
        assert proposal_id in message.objectName
        assert message.conversationId == str(task.recipe_run_id)
        assert message.objectType == object_type
        assert message.groupId == task.dataset_id


def test_quality_report_message(publish_catalog_and_quality_messages_task):
    """
    :Given: a PublishCatalogAndQualityMessages task
    :When: creating quality report message
    :Then: the attributes are correctly populated
    """
    # Given
    task, proposal_id = publish_catalog_and_quality_messages_task
    # When
    message = task.quality_report_message
    # Then
    assert isinstance(message, CreateQualityReportMessage)
    assert message.bucket == task.destination_bucket
    # objectName exists and can be evaluated as a valid path
    assert message.objectName
    _ = Path(message.objectName)
    assert message.datasetId == task.dataset_id
    assert message.conversationId == str(task.recipe_run_id)
