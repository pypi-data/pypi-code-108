"""
Tests for the workflow file system wrapper
"""
from pathlib import Path
from typing import Callable
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem


@pytest.fixture()
def tagged_workflow_fs_data(workflow_file_system):
    wkflow_fs, _, _ = workflow_file_system
    file_obj = b"file contents"
    tags = ["A", "B", "C"]
    intersection = Path("Intersect/f.txt")
    union = [Path(f"Union{t}/f.txt") for t in tags]
    union.append(intersection)
    wkflow_fs.write(file_obj, intersection, tags=tags)
    for t, p in zip(tags, union):
        wkflow_fs.write(file_obj, p, tags=t)

    # prepend base path
    intersection = wkflow_fs.workflow_base_path / intersection
    union = [wkflow_fs.workflow_base_path / u for u in union]

    return tags, intersection, union, file_obj


def test_workflow_file_system(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: Accessing attributes
    Then: has attr workflow_base_path which is namespace(d) to recipe run id that exists
    """
    wkflow_fs, rrun_id, custom_base_path = workflow_file_system
    assert wkflow_fs.workflow_base_path.stem == str(rrun_id)
    assert wkflow_fs.workflow_base_path.exists()


@pytest.mark.parametrize(
    "folder_path",
    [
        pytest.param(Path("test_write_path"), id="Path"),
        pytest.param("test_write_str", id="str"),
    ],
)
@pytest.mark.parametrize(
    "tags",
    [
        pytest.param(None, id="0"),
        pytest.param("foo", id="1"),
        pytest.param(["foo", "baz"], id="2"),
    ],
)
def test_workflow_file_system_write(workflow_file_system, tags, folder_path):
    """
    Given: An instance of WorkflowFileSystem and a file to write
    When: writing to a relative path with/without tags
    Then: file is written to the path relative to the workflow fs configuration
      tags are added to the tag db if they exist
    """
    wkflow_fs, _, _ = workflow_file_system
    file_obj = uuid4().hex.encode("utf8")
    file_path = Path(f"{uuid4().hex[:6]}.bin")
    rel_path = folder_path / file_path
    # When
    wkflow_fs.write(file_obj, rel_path, tags=tags)
    # Then
    full_file_path = wkflow_fs.workflow_base_path / rel_path
    assert full_file_path.exists()
    with full_file_path.open(mode="rb") as f:
        assert file_obj == f.read()
    if tags:
        assert next(wkflow_fs.find_all(tags=tags)) == full_file_path


def test_workflow_file_system_write_invalid(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: writing to an absolute path
    Then: ValueError is raised
    """
    wkflow_fs, _, _ = workflow_file_system
    with pytest.raises(ValueError):
        wkflow_fs.write(b"1234", Path.cwd())


def test_workflow_file_system_tag(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem and a file already in a path
      relative to WorkflowFileSystem base path
    When: Tagging the path
    Then: Tag is added
    """
    wkflow_fs, _, _ = workflow_file_system
    path = wkflow_fs.workflow_base_path / Path("tag_test.txt")
    path.touch()
    # When
    wkflow_fs.tag(path, tags="tag_test")
    wkflow_fs.tag(str(path), tags="tag_test2")

    # Then
    assert next(wkflow_fs.find_any(tags="tag_test")) == path


def test_workflow_file_system_tag_invalid_base_path(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: tagging a path that isn't relative to the WorkflowFileSystem Base path
    Then: get a value error
    """
    wkflow_fs, _, _ = workflow_file_system
    bad_path = Path.cwd()
    with pytest.raises(ValueError):
        wkflow_fs.tag(bad_path, tags="bad_base")


def test_workflow_file_system_tag_invalid_path_not_exists(workflow_file_system):
    """
    Given: An instance of WorkflowFileSystem
    When: tagging a path that is relative to the WorkflowFileSystem base path
       doesn't exist
    Then: get a FileNotFoundError error
    """
    wkflow_fs, _, _ = workflow_file_system
    bad_path = wkflow_fs.workflow_base_path / Path("foo/bar.txt")
    assert not bad_path.exists()
    with pytest.raises(FileNotFoundError):
        wkflow_fs.tag(bad_path, tags="bad_base")


def test_workflow_file_system_find_any(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling find any
    Then: Receive the union of the tagged data as Path objects to the data
    """
    tags, _, union, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    result = list(wkflow_fs.find_any(tags))
    # Then
    assert len(result) == len(union)
    for path in result:
        assert path.exists()
        assert path in union
        with path.open(mode="rb") as f:
            assert f.read() == file_obj


def test_workflow_file_system_find_all(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling find all
    Then: Receive the intersection of the tagged data as Path objects to the data
    """
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    result = list(wkflow_fs.find_all(tags))
    # Then
    assert len(result) == 1
    path = result[0]
    assert path.exists()
    assert path == intersection
    with path.open(mode="rb") as f:
        assert f.read() == file_obj


def test_workflow_file_system_count_any(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling count any
    Then: Receive the number of objects in the union of the tagged data
    """
    tags, _, union, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    result = wkflow_fs.count_any(tags)
    # Then
    assert result == len(union)


def test_workflow_file_system_count_all(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Calling count all
    Then: Receive the number of objects in the intersection of the tagged data
    """
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system
    # When
    result = wkflow_fs.count_all(tags)
    # Then
    assert result == 1


def test_workflow_file_system_downstream_task(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: closing that instance and creating a new one
    Then: Receive the intersection of the tagged data as Path objects that were added
        to the original instance
    """
    wkflow_fs, rrun_id, custom_base_path = workflow_file_system
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    # wkflow_fs.close()
    wkflow_fs2 = WorkflowFileSystem(
        recipe_run_id=rrun_id,
        task_name="wkflow_fs_test",
        scratch_base_path=custom_base_path,
    )
    # When
    try:
        result = list(wkflow_fs2.find_all(tags))
        # Then
        assert len(result) == 1
        path = result[0]
        assert path.exists()
        assert path == intersection
        with path.open(mode="rb") as f:
            assert f.read() == file_obj
    finally:
        # Teardown
        wkflow_fs2.purge()


def test_workflow_file_system_purge(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: calling purge
    Then: There is no more tagged data or paths in the base_path
    """
    tags, intersection, _, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system

    # When
    wkflow_fs.purge()
    # Then
    result = list(wkflow_fs.find_any(tags))
    assert not result
    assert not wkflow_fs.workflow_base_path.exists()


@pytest.mark.parametrize(
    "func, attr",
    [
        pytest.param(repr, "__repr__", id="repr"),
        pytest.param(str, "__str__", id="str"),
    ],
)
def test_workflow_file_system_dunder(workflow_file_system, func: Callable, attr):
    """
    Given: Connection to a tag database
    When: retrieving dunder method that should be implemented
    Then: It is implemented
    """
    wkflow_fs, _, _ = workflow_file_system

    assert getattr(wkflow_fs, attr, None)
    assert func(wkflow_fs)


def test_workflow_file_system_delete(workflow_file_system, tagged_workflow_fs_data):
    """
    Given: An instance of WorkflowFileSystem with tagged data
    When: Deleting a specific file
    Then: The file is removed from disk and all references to it are gone from tags
    """
    tags, _, union, file_obj = tagged_workflow_fs_data
    wkflow_fs, _, _ = workflow_file_system
    assert union[0].exists()
    assert str(union[0]) in wkflow_fs._tag_db.any(tags=tags)
    wkflow_fs.delete(path=union[0])
    assert not union[0].exists()
    assert not str(union[0]) in wkflow_fs._tag_db.any(tags=tags)
