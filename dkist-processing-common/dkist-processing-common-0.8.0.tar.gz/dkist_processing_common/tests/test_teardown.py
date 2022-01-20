import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.teardown import Teardown


class TeardownTest(Teardown):
    def metadata_store_change_recipe_run_to_completed_successfully(self):
        pass


@pytest.fixture(scope="function")
def teardown_task(tmp_path, recipe_run_id):
    number_of_files = 10
    tag_object = Tag.output()
    filenames = [f"file_{filenum}.ext" for filenum in range(number_of_files)]
    with TeardownTest(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
        for filename in filenames:
            filepath = task.scratch.workflow_base_path / filename
            filepath.touch()
            task.tag(filepath, tag_object)

        yield task, filenames, tag_object


def test_purge_data(teardown_task):
    """
    :Given: a Teardown task with files and tags linked to it
    :When: running the purge_data method
    :Then: all the files are deleted and the tags are removed
    """
    task, filenames, tag_object = teardown_task
    tagged_data = task.read(tags=tag_object)
    for filepath in tagged_data:
        assert filepath.exists()
    task()
    for filepath in tagged_data:
        assert not filepath.exists()
    post_purge_tagged_data = list(task.read(tags=tag_object))
    assert len(post_purge_tagged_data) == 0
