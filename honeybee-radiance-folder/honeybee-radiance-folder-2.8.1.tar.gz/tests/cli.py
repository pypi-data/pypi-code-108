from click.testing import CliRunner
from honeybee_radiance_folder.cli import filter_json_file
import json
import os


def test_filter_file():
    runner = CliRunner()
    input_file = './tests/assets/project_folder/grid_info.json'
    output_file = './tests/assets/temp/grid_filtered_0.json'
    result = runner.invoke(
        filter_json_file, [
            input_file, 'group:daylight_grids', '--output-file', output_file
        ]
    )
    assert result.exit_code == 0
    # check the file is created
    with open(output_file) as inf:
        data = json.load(inf)
    assert len(data) == 1
    os.unlink(output_file)


def test_filter_file_remove():
    runner = CliRunner()
    input_file = './tests/assets/project_folder/grid_info.json'
    output_file = './tests/assets/project_folder/grid_filtered_1.json'
    result = runner.invoke(
        filter_json_file, [
            input_file, 'group:daylight_grids', '--output-file', output_file, '--remove'
        ]
    )
    assert result.exit_code == 0
    # check the file is created
    with open(output_file) as inf:
        data = json.load(inf)
    assert len(data) == 8
    os.unlink(output_file)
