import os
import unittest

import pytest

from magnumapi.tool_adapters.ansys.AnsysToolAdapter import AnsysToolAdapter
from magnumapi.tool_adapters.roxie.RoxieToolAdapter import RoxieToolAdapter
from tests.resource_files import create_resources_path

config = {"input_folder_rel_dir": "input%sMechanic_Plate" % os.sep,
          "input_file": "15T_mech.inp",
          "output_file": "vallone.out",
          "model_file": "Model.inp",
          "rst_file": "15T_2d_mech.rst"}


class TestAnsysToolAdapter(unittest.TestCase):

    def test_get_input_path(self):
        # arrange
        ansys = AnsysToolAdapter(**config)

        # act
        input_path = ansys.get_input_path()

        # assert
        input_path_ref = os.path.join(os.getcwd(), 'input%sMechanic_Plate%s15T_mech.inp' % (os.sep, os.sep))
        assert input_path_ref == input_path

    def test_get_output_path(self):
        # arrange
        ansys = AnsysToolAdapter(**config)

        # act
        output_path = ansys.get_output_path()

        # assert
        output_path_ref = os.path.join(os.getcwd(), 'input%sMechanic_Plate%svallone.out' % (os.sep, os.sep))
        assert output_path_ref == output_path

    def test_get_model_path(self):
        # arrange
        ansys = AnsysToolAdapter(**config)

        # act
        model_path = ansys.get_model_path()

        # assert
        model_path_ref = os.path.join(os.getcwd(), 'input%sMechanic_Plate%sModel.inp' % (os.sep, os.sep))
        assert model_path_ref == model_path

    def test_convert_roxie_force_file_to_ansys(self):
        # arrange
        roxie_force_input_path = create_resources_path('resources/tool_adapters/ansys/roxie.force2d')
        roxie_force_output_path = create_resources_path('resources/tool_adapters/ansys/roxie_edit.force2d')
        ansys_force_output_path = create_resources_path('resources/tool_adapters/ansys/forces_edit.vallone')
        field = 16
        target_field = 15

        # act
        # # update ROXIE force file
        RoxieToolAdapter.update_force2d_with_field_scaling(roxie_force_input_path,
                                                           roxie_force_output_path,
                                                           field,
                                                           target_field)

        # # prepare ANSYS force file
        AnsysToolAdapter.convert_roxie_force_file_to_ansys(roxie_force_output_path, ansys_force_output_path)

        # assert
        with open(ansys_force_output_path, 'r') as file:
            ansys_force = file.readlines()

        output_text_ref_path = create_resources_path('resources/tool_adapters/ansys/forces_edit_ref.vallone')

        with open(output_text_ref_path, 'r') as file:
            ansys_force_ref = file.readlines()

        for ansys_force_ref_el, ansys_force_el in zip(ansys_force_ref, ansys_force):
            self.assertEqual(ansys_force_ref_el, ansys_force_el)


if __name__ == '__main__':
    unittest.main()

