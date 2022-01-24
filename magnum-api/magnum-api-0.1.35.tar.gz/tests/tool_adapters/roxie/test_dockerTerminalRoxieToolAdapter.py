import os

from magnumapi.tool_adapters.roxie.RoxieToolAdapter import DockerTerminalRoxieToolAdapter


config = {
    "executable_name": "runroxie",
    "input_folder_rel_dir": "input",
    "input_file": "input.data",
    "output_file": "input.output",
    "cadata_file": "roxieold_2.cadata",
    "xml_output_file": "roxieData.xml",
    "docker_image_name": "roxie_terminal"
}


def test_constructor():
    # arrange

    # act
    roxie = DockerTerminalRoxieToolAdapter(**config)

    # assert
    assert 'runroxie' == roxie.executable_name
    assert 'input' == roxie.input_folder_rel_dir
    assert 'input%sroxieData.xml' % os.sep == roxie.xml_output_file_path
    assert 'input%sinput.output' % os.sep == roxie.output_file_path
    assert 'input%sinput.data' % os.sep == roxie.input_file_path
    assert 'input%sroxieold_2.cadata' % os.sep == roxie.cadata_file_path
    assert 'roxieold_2.cadata' == roxie.cadata_file
    assert 'roxie_terminal' == roxie.docker_image_name


def test__get_process_command():
    # arrange

    # act
    roxie = DockerTerminalRoxieToolAdapter(**config)
    command = roxie._get_process_command()

    assert  ['docker', 'exec', 'roxie_terminal', 'runroxie', 'input/input.data'] == command
