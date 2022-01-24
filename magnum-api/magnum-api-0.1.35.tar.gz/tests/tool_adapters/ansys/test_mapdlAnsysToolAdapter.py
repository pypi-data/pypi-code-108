import os

import pytest

from magnumapi.tool_adapters.ansys.AnsysToolAdapter import MapdlAnsysToolAdapter

config = {"input_folder_rel_dir": "input\\Mechanic_Plate",
          "input_file": "15T_mech.inp",
          "output_file": "vallone.out",
          "model_file": "Model.inp",
          "rst_file": "15T_2d_mech.rst",
          "single_upload_files": [],
          "reupload_files": []}


def test_constructor():
    # arrange

    # act
    ansys = MapdlAnsysToolAdapter(**config)

    # assert
    assert os.getcwd() == ansys.root_dir
    assert "input\\Mechanic_Plate" == ansys.input_folder_rel_dir
    assert "15T_mech.inp" == ansys.input_file
    assert "vallone.out" == ansys.output_file
    assert "Model.inp" == ansys.model_file
    assert "15T_2d_mech.rst" == ansys.rst_file
    assert [] == ansys.single_upload_files
    assert [] == ansys.reupload_files
