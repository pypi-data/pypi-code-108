from io import BytesIO

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.base import WorkflowDataTaskBase


class WorkflowDataTaskBaseTask(WorkflowDataTaskBase):
    def run(self):
        pass


@pytest.fixture(scope="function")
def workflow_data_task(tmp_path, recipe_run_id):
    number_of_files = 10
    tag_string = "WORKFLOW_DATA_TASK"
    tag_object = Tag.input()
    filenames = [f"file_{filenum}.ext" for filenum in range(number_of_files)]
    with WorkflowDataTaskBaseTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task._constants_db[BudName.instrument.value] = "foo"
        task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
        for filename in filenames:
            filepath = task.scratch.workflow_base_path / filename
            filepath.touch()
            task.tag(filepath, tag_string)
            task.tag(filepath, tag_object)

        yield task, number_of_files, filenames, tag_string, tag_object
        task.scratch.purge()
        task._constants_db.purge()


def test_valid_read_with_strings(workflow_data_task):
    """
    Given: a WorkflowDataTask with tagged data
    When: reading tagged files using a string
    Then: the correct number of files are returned and they have the correct names
    """
    task, number_of_files, filenames, tag_string, _ = workflow_data_task
    task()
    tagged_filepaths = list(task.read(tags=tag_string))
    assert len(tagged_filepaths) == number_of_files
    for tagged_filepath in tagged_filepaths:
        assert tagged_filepath.name in filenames
        assert tagged_filepath.exists()


def test_valid_read_with_tag_object(workflow_data_task):
    """
    Given: a WorkflowDataTask with tagged data
    When: reading tagged files using a string
    Then: the correct number of files are returned and they have the correct names
    """
    task, number_of_files, filenames, _, tag_object = workflow_data_task
    tagged_filepaths = list(task.read(tags=tag_object))
    assert len(tagged_filepaths) == number_of_files
    for tagged_filepath in tagged_filepaths:
        assert tagged_filepath.name in filenames
        assert tagged_filepath.exists()


def test_valid_write_with_bytes(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: writing a bytes object to disk
    Then: the file is on disk and correctly tagged
    """
    task, _, _, _, _ = workflow_data_task
    relative_path = "bytes_path"
    task.write(file_obj=bytes("abcdefg", "utf-8"), tags="BYTES_OBJECT", relative_path=relative_path)
    assert (task.scratch.workflow_base_path / relative_path).exists()
    assert len(list(task.read(tags="BYTES_OBJECT"))) == 1


def test_valid_write_with_bytesio(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: writing a BytesIO object to disk
    Then: the file is on disk and correctly tagged
    """
    task, _, _, _, _ = workflow_data_task
    relative_path = "bytesio_path"
    task.write(
        file_obj=BytesIO(bytes("abcdefg", "utf-8")),
        tags="BYTESIO_OBJECT",
        relative_path=relative_path,
    )
    assert (task.scratch.workflow_base_path / relative_path).exists()
    assert len(list(task.read(tags="BYTESIO_OBJECT"))) == 1


def test_write_tags_is_none(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: writing a file to disk with tags=None
    Then: a ValueError is raised
    """
    task, _, _, _, _ = workflow_data_task
    relative_path = "bytesio_path"
    with pytest.raises(ValueError):
        task.write(file_obj=bytes("abcdefg", "utf-8"), tags=None, relative_path=relative_path)


def test_read_nonexistent_tag(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: reading from a tag that doesn't exist
    Then: an empty generator is returned
    """
    task, _, _, _, _ = workflow_data_task
    filepaths = task.read(tags="DOES_NOT_EXIST")
    with pytest.raises(StopIteration):
        next(filepaths)


def test_tag_nonexistent_file(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: trying to tag a file that doesn't exist
    Then: a FileNotFoundError is raised
    """
    task, _, _, _, _ = workflow_data_task
    with pytest.raises(FileNotFoundError):
        task.tag(path=task.scratch.workflow_base_path / "abc.ext", tags="NONEXISTENT_FILE")


def test_tag_not_on_base_path(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: trying to tag a file that isn't on the workflow base path
    Then: a ValueError is raised
    """
    task, _, _, _, _ = workflow_data_task
    with pytest.raises(ValueError):
        task.tag(path="abc.ext", tags="NOT_ON_BASE_PATH")


def test_count(workflow_data_task):
    """
    Given: a WorkflowDataTask with tagged data
    When: counting tagged files
    Then: the correct number of files are returned
    """
    task, number_of_files, filenames, tag_string, _ = workflow_data_task
    task()
    assert task.count(tags=tag_string) == number_of_files


def test_constants(workflow_data_task):
    """
    Given: a WorkflowDataTask
    When: accessing a value on that task's constants object
    Then: the correct value is returned
    """
    task = workflow_data_task[0]
    assert task.constants.instrument == "foo"
