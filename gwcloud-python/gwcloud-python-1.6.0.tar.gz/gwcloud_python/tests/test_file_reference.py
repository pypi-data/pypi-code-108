from gwcloud_python import FileReference, FileReferenceList
import pytest
from pathlib import Path
from gwcloud_python.utils import remove_path_anchor


@pytest.fixture
def setup_dicts():
    return [
        {'path': 'data/dir/test1.png', 'file_size': '1', 'download_token': 'test_download_token_1'},
        {'path': 'data/dir/test2.png', 'file_size': '1', 'download_token': 'test_download_token_2'},
        {'path': 'result/dir/test1.png', 'file_size': '1', 'download_token': 'test_download_token_3'},
        {'path': 'result/dir/test2.png', 'file_size': '1', 'download_token': 'test_download_token_4'},
    ]


def test_file_reference(setup_dicts):
    for file_dict in setup_dicts:
        ref = FileReference(**file_dict)
        assert ref.path == remove_path_anchor(Path(file_dict['path']))
        assert ref.file_size == int(file_dict['file_size'])
        assert ref.download_token == file_dict['download_token']


def test_file_reference_list(setup_dicts):
    file_references = [FileReference(**file_dict) for file_dict in setup_dicts]
    file_reference_list = FileReferenceList(file_references)

    for i, ref in enumerate(file_reference_list):
        assert ref.path == file_references[i].path
        assert ref.file_size == file_references[i].file_size
        assert ref.download_token == file_references[i].download_token

    assert file_reference_list.get_total_bytes() == sum([ref.file_size for ref in file_references])
    assert file_reference_list.get_tokens() == [ref.download_token for ref in file_references]
    assert file_reference_list.get_paths() == [ref.path for ref in file_references]
