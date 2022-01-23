import shutil

import pytest

from resolve_name_clash import resolve_name_clash

test_cases = [
    {
        "name": "clash - no extension",
        "src_filename": "a",
        "existing_files_in_dest": ["a"],
        "expected_file_name": "a_1",
    },
    {
        "name": "clash - one extension",
        "src_filename": "a.png",
        "existing_files_in_dest": ["a.png"],
        "expected_file_name": "a_1.png",
    },
    {
        "name": "clash - two extensions",
        "src_filename": "a.tar.gz",
        "existing_files_in_dest": ["a.tar.gz"],
        "expected_file_name": "a_1.tar.gz",
    },
    {
        "name": "no clash",
        "src_filename": "a.jpg",
        "existing_files_in_dest": [],
        "expected_file_name": "a.jpg",
    },
    {
        "name": "multiple clashes",
        "src_filename": "a.png",
        "existing_files_in_dest": ["a.png", "a_1.png", "a_2.png", "a_3.png"],
        "expected_file_name": "a_4.png",
    },
    {
        "name": "multiple clashes - hole in list of clashes",
        "src_filename": "a.png",
        "existing_files_in_dest": ["a.png", "a_1.png", "a_3.png"],  # Note no "a_2.png"
        "expected_file_name": "a_2.png",
    },
]


def get_test_case_ids():
    return [case["name"] for case in test_cases]


# Fixture that, given the test case data, sets up the
# src and dest directories and then returns
# (src_file: Path, dest: Path, expected_file_name: str)
@pytest.fixture(name="test_params", params=test_cases, ids=get_test_case_ids())
def fixture_test_params(tmp_path, request):
    # Make src and dest dirs
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()

    # Make src file
    src_file = src / request.param["src_filename"]
    src_file.touch()

    # Make dest files
    for file in request.param["existing_files_in_dest"]:
        (dest / file).touch()

    return (
        src_file,
        dest,
        request.param["expected_file_name"],
    )


def test_case(test_params):
    """Test the regular expected behavior of resolve_name_clash given the test data above"""
    src_file, dest, expected_file_name = test_params

    result = resolve_name_clash(src_file, dest)

    assert result == (dest / expected_file_name)


def test_case_dest_dir_does_not_exist(test_params):
    """Test what happens when the given destination directory doesn't exist.
    We go through each of the cases but remove the destination directory
    before invoking resolve_name_clash. In call cases, we expect the result
    to be the source file name appended to the destination directory because
    if the destination doesn't exist, there is no clash. Of course, using this
    destination path in, say, a copy operation, will fail but that's not our
    problem."""
    src_file, dest, _ = test_params

    # Remove the destination tree and assert that it doesn't exist
    shutil.rmtree(dest)
    assert not dest.exists()

    result = resolve_name_clash(src_file, dest)

    # Destination doesn't exist, so the result is always the destination dir
    # and the regular src file name.
    assert result == (dest / src_file.name)


def test_case_src_file_does_not_exist(test_params):
    """Test what happens when the given source file doesn't exist.
    In short - it doesn't matter: this should be have exactly the
    same as the case when the src file does exist. resolve_name_clash
    just computes a filename that would resolve a clash in the destination
    were the given source file to be copied to the destination."""

    src_file, dest, expected_file_name = test_params

    # Remove the source file and assert that it doesn't exist
    src_file.unlink()
    assert not src_file.exists()

    result = resolve_name_clash(src_file, dest)

    assert result == (dest / expected_file_name)
