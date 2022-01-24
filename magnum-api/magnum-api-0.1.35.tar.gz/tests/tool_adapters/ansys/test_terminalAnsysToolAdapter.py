import os

import pytest

from magnumapi.tool_adapters.ansys.AnsysToolAdapter import TerminalAnsysToolAdapter

config = {"input_folder_rel_dir": "input\\Mechanic_Plate",
          "input_file": "15T_mech.inp",
          "output_file": "vallone.out",
          "model_file": "Model.inp",
          "rst_file": "15T_2d_mech.rst",
          "out_temp_file": "out_tmp_mech.txt",
          "license_type": "-aa_r",
          "executable_path": "C:\\Program Files\\ANSYS Inc\\v202\\ansys\\bin\\winx64\\ANSYS202.exe"}


def test_constructor():
    # arrange

    # act
    ansys = TerminalAnsysToolAdapter(**config)

    # assert
    assert os.getcwd() == ansys.root_dir
    assert "input\\Mechanic_Plate" == ansys.input_folder_rel_dir
    assert "15T_mech.inp" == ansys.input_file
    assert "vallone.out" == ansys.output_file
    assert "Model.inp" == ansys.model_file
    assert "15T_2d_mech.rst" == ansys.rst_file
    assert "out_tmp_mech.txt" == ansys.out_temp_file
    assert "-aa_r" == ansys.license_type
    assert "C:\\Program Files\\ANSYS Inc\\v202\\ansys\\bin\\winx64\\ANSYS202.exe" == ansys.executable_path
