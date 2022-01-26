import os

from magnumapi.tool_adapters.roxie.RoxieToolAdapter import TerminalRoxieToolAdapter

config = {
    "executable_name": "runroxie",
    "input_folder_rel_dir": "input",
    "input_file": "input.data",
    "output_file": "input.output",
    "cadata_file": "roxieold_2.cadata",
    "xml_output_file": "roxieData.xml"
}

def test_constructor():
    # arrange

    # act
    roxie = TerminalRoxieToolAdapter(**config)

    # assert
    assert 'runroxie' == roxie.executable_name
    assert 'input' == roxie.input_folder_rel_dir
    assert 'input%sroxieData.xml' % os.sep == roxie.xml_output_file_path
    assert 'input%sinput.output' % os.sep == roxie.output_file_path
    assert 'input%sinput.data' % os.sep == roxie.input_file_path
    assert 'input%sroxieold_2.cadata' % os.sep == roxie.cadata_file_path
    assert 'roxieold_2.cadata' == roxie.cadata_file

def test__get_process_command():
    # arrange

    # act
    roxie = TerminalRoxieToolAdapter(**config)
    command = roxie._get_process_command()

    assert  ['runroxie', 'input%sinput.data' % os.sep] == command
