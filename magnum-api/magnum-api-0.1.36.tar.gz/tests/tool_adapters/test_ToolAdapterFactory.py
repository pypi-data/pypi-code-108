import os
import pytest

from magnumapi.tool_adapters.ToolAdapterFactory import ToolAdapterFactory
from magnumapi.tool_adapters.roxie.RoxieToolAdapter import TerminalRoxieToolAdapter
from magnumapi.tool_adapters.roxie.RoxieToolAdapter import DockerTerminalRoxieToolAdapter
from tests.resource_files import create_resources_path


def test_init_with_json_terminal_roxie():
    # arrange
    config_path = create_resources_path('resources/tool_adapters/roxie/terminal_roxie.json')

    # act
    tool_adapter = ToolAdapterFactory.init_with_json(config_path)

    # assert
    assert isinstance(tool_adapter, TerminalRoxieToolAdapter)
    assert 'input' == tool_adapter.input_folder_rel_dir
    assert 'runroxie' == tool_adapter.executable_name
    assert 'input%sroxieData.xml' % os.sep == tool_adapter.xml_output_file_path
    assert 'input%sinput.output' % os.sep == tool_adapter.output_file_path
    assert 'input%sinput.data' % os.sep == tool_adapter.input_file_path
    assert 'input%sroxieold_2.cadata' % os.sep == tool_adapter.cadata_file_path
    assert 'roxieold_2.cadata' == tool_adapter.cadata_file


def test_init_with_json_docker_terminal_roxie():
    # arrange
    config_path = create_resources_path('resources/tool_adapters/roxie/docker_terminal_roxie.json')

    # act
    tool_adapter = ToolAdapterFactory.init_with_json(config_path)

    # assert
    assert isinstance(tool_adapter, DockerTerminalRoxieToolAdapter)
    assert 'input' == tool_adapter.input_folder_rel_dir
    assert 'runroxie' == tool_adapter.executable_name
    assert 'input%sroxieData.xml' % os.sep == tool_adapter.xml_output_file_path
    assert 'input%sinput.output' % os.sep == tool_adapter.output_file_path
    assert 'input%sinput.data' % os.sep == tool_adapter.input_file_path
    assert 'input%sroxieold_2.cadata' % os.sep == tool_adapter.cadata_file_path
    assert 'runroxie' == tool_adapter.executable_name
    assert 'roxieold_2.cadata' == tool_adapter.cadata_file


def test_init_with_dict_terminal_roxie():
    # arrange
    config = {
        "executable_name": "runroxie",
        "input_folder_rel_dir": "input",
        "input_file": "input.data",
        "output_file": "input.output",
        "cadata_file": "roxieold_2.cadata",
        "xml_output_file": "roxieData.xml"
    }

    # act
    tool_adapter = ToolAdapterFactory.init_with_dict(config)

    # assert
    assert isinstance(tool_adapter, TerminalRoxieToolAdapter)
    assert 'input' == tool_adapter.input_folder_rel_dir
    assert 'runroxie' == tool_adapter.executable_name
    assert 'input%sroxieData.xml' % os.sep == tool_adapter.xml_output_file_path
    assert 'input%sinput.output' % os.sep == tool_adapter.output_file_path
    assert 'input%sinput.data' % os.sep == tool_adapter.input_file_path
    assert 'input%sroxieold_2.cadata' % os.sep == tool_adapter.cadata_file_path
    assert 'roxieold_2.cadata' == tool_adapter.cadata_file


def test_init_with_dict_docker_terminal_roxie():
    # arrange
    config = {
        "executable_name": "runroxie",
        "input_folder_rel_dir": "input",
        "input_file": "input.data",
        "output_file": "input.output",
        "cadata_file": "roxieold_2.cadata",
        "xml_output_file": "roxieData.xml",
        "docker_image_name": "roxie_terminal"
    }

    # act
    tool_adapter = ToolAdapterFactory.init_with_dict(config)

    # assert
    assert isinstance(tool_adapter, DockerTerminalRoxieToolAdapter)
    assert 'input' == tool_adapter.input_folder_rel_dir
    assert 'runroxie' == tool_adapter.executable_name
    assert 'input%sroxieData.xml' % os.sep == tool_adapter.xml_output_file_path
    assert 'input%sinput.output' % os.sep == tool_adapter.output_file_path
    assert 'input%sinput.data' % os.sep == tool_adapter.input_file_path
    assert 'input%sroxieold_2.cadata' % os.sep == tool_adapter.cadata_file_path
    assert 'roxieold_2.cadata' == tool_adapter.cadata_file


def test_init_with_dict_docker_terminal_roxie_error():
    # arrange
    config = {
        "executable_name": "runroxie",
        "input_folder_rel_dir": "input",
        "input_file": "input.data",
        "output_file": "input.output",
        "cadata_file": "roxieold_2.cadata",
        "xml_output_file": "roxieData.xml",
        "docker_image": "roxie_terminal"
    }

    # act
    with pytest.raises(KeyError) as exc_info:
        tool_adapter = ToolAdapterFactory.init_with_dict(config)

    assert 'The input config definition keys dict_keys([\'executable_name\', \'input_folder_rel_dir\', ' \
           '\'input_file\', \'output_file\', \'cadata_file\', \'xml_output_file\', \'docker_image\']) ' \
           'do not match any tool adapter constructor signature!' in str(exc_info.value)


def test_init_with_dict_terminal_ansys():
    # arrange
    config = {"input_folder_rel_dir": "input\\Mechanic_Plate",
              "input_file": "15T_mech.inp",
              "output_file": "vallone.out",
              "model_file": "Model.inp",
              "rst_file": "15T_2d_mech.rst",
              "out_temp_file": "out_tmp_mech.txt",
              "license_type": "-aa_r",
              "executable_path": "C:\\Program Files\\ANSYS Inc\\v202\\ansys\\bin\\winx64\\ANSYS202.exe"}

    # act
    tool_adapter = ToolAdapterFactory.init_with_dict(config)

    # assert
    assert os.getcwd() == tool_adapter.root_dir
    assert "input\\Mechanic_Plate" == tool_adapter.input_folder_rel_dir
    assert "15T_mech.inp" == tool_adapter.input_file
    assert "vallone.out" == tool_adapter.output_file
    assert "Model.inp" == tool_adapter.model_file
    assert "15T_2d_mech.rst" == tool_adapter.rst_file
    assert "out_tmp_mech.txt" == tool_adapter.out_temp_file
    assert "-aa_r" == tool_adapter.license_type
    assert "C:\\Program Files\\ANSYS Inc\\v202\\ansys\\bin\\winx64\\ANSYS202.exe" == tool_adapter.executable_path


def test_init_with_json_terminal_ansys():
    # arrange
    config_path = create_resources_path('resources/tool_adapters/ansys/terminal_ansys_windows.json')

    # act
    tool_adapter = ToolAdapterFactory.init_with_json(config_path)

    # assert
    assert os.getcwd() == tool_adapter.root_dir
    assert "input\\Mechanic_Plate" == tool_adapter.input_folder_rel_dir
    assert "15T_mech.inp" == tool_adapter.input_file
    assert "vallone.out" == tool_adapter.output_file
    assert "Model.inp" == tool_adapter.model_file
    assert "15T_2d_mech.rst" == tool_adapter.rst_file
    assert "out_tmp_mech.txt" == tool_adapter.out_temp_file
    assert "-aa_r" == tool_adapter.license_type
    assert "C:\\Program Files\\ANSYS Inc\\v202\\ansys\\bin\\winx64\\ANSYS202.exe" == tool_adapter.executable_path


def test_init_with_dict_mapdl_ansys():
    # arrange
    config = {"input_folder_rel_dir": "input\\Mechanic_Plate",
              "input_file": "15T_mech.inp",
              "output_file": "vallone.out",
              "model_file": "Model.inp",
              "rst_file": "15T_2d_mech.rst",
              "single_upload_files": [],
              "reupload_files": []}

    # act
    tool_adapter = ToolAdapterFactory.init_with_dict(config)

    # assert
    assert os.getcwd() == tool_adapter.root_dir
    assert "input\\Mechanic_Plate" == tool_adapter.input_folder_rel_dir
    assert "15T_mech.inp" == tool_adapter.input_file
    assert "vallone.out" == tool_adapter.output_file
    assert "Model.inp" == tool_adapter.model_file
    assert "15T_2d_mech.rst" == tool_adapter.rst_file
    assert [] == tool_adapter.single_upload_files
    assert [] == tool_adapter.reupload_files


def test_init_with_json_mapdl_ansys():
    # arrange
    config_path = create_resources_path('resources/tool_adapters/ansys/mapdl_ansys.json')

    # act
    tool_adapter = ToolAdapterFactory.init_with_json(config_path)

    # assert
    assert os.getcwd() == tool_adapter.root_dir
    assert "input\\Mechanic_Plate" == tool_adapter.input_folder_rel_dir
    assert "15T_mech.inp" == tool_adapter.input_file
    assert "vallone.out" == tool_adapter.output_file
    assert "Model.inp" == tool_adapter.model_file
    assert "15T_2d_mech.rst" == tool_adapter.rst_file
    assert [] == tool_adapter.single_upload_files
    assert [] == tool_adapter.reupload_files


def test_init_with_dict_docker_mapdl_ansys():
    # arrange
    config = {"input_folder_rel_dir": "input\\Mechanic_Plate",
              "input_file": "15T_mech.inp",
              "output_file": "vallone.out",
              "model_file": "Model.inp",
              "rst_file": "15T_2d_mech.rst",
              "single_upload_files": [],
              "reupload_files": [],
              "ip": "127.0.0.1",
              "port": 50052}

    # act
    tool_adapter = ToolAdapterFactory.init_with_dict(config)

    # assert
    assert os.getcwd() == tool_adapter.root_dir
    assert "input\\Mechanic_Plate" == tool_adapter.input_folder_rel_dir
    assert "15T_mech.inp" == tool_adapter.input_file
    assert "vallone.out" == tool_adapter.output_file
    assert "Model.inp" == tool_adapter.model_file
    assert "15T_2d_mech.rst" == tool_adapter.rst_file
    assert [] == tool_adapter.single_upload_files
    assert [] == tool_adapter.reupload_files
    assert "127.0.0.1" == tool_adapter.ip
    assert 50052 == tool_adapter.port


def test_init_with_json_docker_mapdl_ansys():
    # arrange
    config_path = create_resources_path('resources/tool_adapters/ansys/docker_mapdl_ansys.json')

    # act
    tool_adapter = ToolAdapterFactory.init_with_json(config_path)

    # assert
    assert os.getcwd() == tool_adapter.root_dir
    assert "input\\Mechanic_Plate" == tool_adapter.input_folder_rel_dir
    assert "15T_mech.inp" == tool_adapter.input_file
    assert "vallone.out" == tool_adapter.output_file
    assert "Model.inp" == tool_adapter.model_file
    assert "15T_2d_mech.rst" == tool_adapter.rst_file
    assert [] == tool_adapter.single_upload_files
    assert [] == tool_adapter.reupload_files
    assert "127.0.0.1" == tool_adapter.ip
    assert 50052 == tool_adapter.port
