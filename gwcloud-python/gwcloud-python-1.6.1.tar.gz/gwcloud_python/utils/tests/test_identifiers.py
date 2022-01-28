import pytest
from pathlib import Path
from gwcloud_python.utils import identifiers


@pytest.fixture
def setup_paths():
    return {
        'png': Path('test.png'),

        'html': Path('test.html'),
        'dir_html': Path('this/is/a/test.html'),

        'no_suffix': Path('this/is/a/test'),
        'png_dir': Path('this/is/not/a/png'),
        'html_dir': Path('this/is/not/a/html'),

        'corner': Path('this/is/a_corner.png'),
        'corner_bad_ext': Path('this/is/a_corner.txt'),
        'corner_bad_pattern': Path('this/is/a_coroner.png'),

        'config': Path('this/is/a_config_complete.ini'),
        'config_bad_ext': Path('this/is/a_config_complete.txt'),
        'config_bad_pattern': Path('this/is/a_config_incomplete.ini'),

        'merged_json': Path('this/is/a_merge_result.json'),
        'merged_json_bad_ext': Path('this/is/a_merge_result.txt'),
        'merged_json_bad_pattern': Path('this/is/a_merged_result.txt'),

        'unmerged_json': Path('this/is/a_result.json'),
        'unmerged_json_bad_ext': Path('this/is/a_result.txt'),
        'unmerged_json_bad_pattern': Path('this/is/a_resalt.json'),

        'absolute_data_path': Path('/data/this/is/a/test'),
        'data_path': Path('data/this/is/a/test'),
        'data_dir': Path('data/'),

        'absolute_result_path': Path('/result/this/is/a/test'),
        'result_path': Path('result/this/is/a/test'),
        'result_dir': Path('result/'),

        'data_dir_png': Path('data/dir/test.png'),
        'data_png': Path('data.png'),

        'result_dir_png': Path('result/dir/test.png'),
        'result_png': Path('result.png'),

        'result_merged_json': Path('result/dir/a_merge_result.json'),
        'result_unmerged_json': Path('result/dir/a_result.json'),
    }


@pytest.fixture
def setup_identifiers():
    return [
        (
            identifiers.html_file,
            ['html', 'dir_html']
        ),
        (
            identifiers.png_file,
            ['png', 'corner', 'corner_bad_pattern', 'data_dir_png', 'data_png', 'result_dir_png', 'result_png']
        ),
        (
            identifiers.data_dir,
            ['data_path', 'data_dir', 'data_dir_png']
        ),
        (
            identifiers.result_dir,
            ['result_path', 'result_dir', 'result_dir_png', 'result_merged_json', 'result_unmerged_json']
        ),
        (
            identifiers.config_file,
            ['config']
        ),
        (
            identifiers.merged_json_file,
            ['merged_json', 'result_merged_json']
        ),
        (
            identifiers.unmerged_json_file,
            ['unmerged_json', 'result_unmerged_json', 'merged_json', 'result_merged_json']
        ),
        (
            identifiers.corner_plot_file,
            ['corner']
        ),
        (
            identifiers.data_png_file,
            ['data_dir_png']
        ),
        (
            identifiers.result_png_file,
            ['result_dir_png']
        ),
        (
            identifiers.result_merged_json_file,
            ['result_merged_json']
        ),
        (
            identifiers.result_json_file,
            ['result_merged_json', 'result_unmerged_json']
        ),
    ]


@pytest.fixture
def check_identifier(setup_paths):
    def _check_identifier(identifier, true_path_keys):
        true_paths = [value for key, value in setup_paths.items() if key in true_path_keys]
        false_paths = [value for key, value in setup_paths.items() if key not in true_path_keys]

        for path in true_paths:
            assert identifier(path) is True

        for path in false_paths:
            assert identifier(path) is False

    return _check_identifier


def test_identifiers(setup_identifiers, check_identifier):
    for identifier, true_path_keys in setup_identifiers:
        check_identifier(identifier, true_path_keys)
