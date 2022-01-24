import unittest
from unittest.mock import patch

from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.tool_adapters.ansys.AnsysInputBuilder import AnsysInputBuilder
import magnumapi.commons.text_file as text_file
from tests.resource_files import create_resources_path


class TestAnsysInputBuilder(unittest.TestCase):
    @patch("matplotlib.pyplot.show")
    def test_input_file_generation(self, mock_show=None):

        json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        geometry = GeometryFactory.init_with_json(json_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        homo_geometry = geometry.homogenize()

        # Find number of layers
        n_layers = homo_geometry.get_number_of_layers()

        self.assertEqual(4, n_layers)
        # For each layer
        # # Number of blocks per layer
        blocks_per_layer = homo_geometry.get_number_of_blocks_per_layer()
        self.assertListEqual([4, 3, 3, 2], blocks_per_layer)

        output_text = AnsysInputBuilder.generate_ansys_input_text(homo_geometry)
        output_text_ref_path = create_resources_path('resources/tool_adapters/ansys/Model.inp')
        output_text_ref = text_file.readlines(output_text_ref_path)

        self.assertListEqual(output_text_ref, output_text)
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_input_file_generation_sm_ct(self, mock_show=None):

        json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel_slotted.json')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        geometry = GeometryFactory.init_slotted_with_json(json_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        homo_geometry = geometry.homogenize()

        output_text = AnsysInputBuilder.generate_ansys_input_text_sm_ct(homo_geometry)
        output_text_ref_path = create_resources_path('resources/tool_adapters/ansys/Model_slotted.inp')
        output_text_ref = text_file.readlines(output_text_ref_path)
        output_text_ref = [el.replace('\n', '') for el in output_text_ref]
        self.assertListEqual(output_text_ref, output_text)
        if mock_show is not None:
            mock_show.assert_called()

    def test_update_ansys_input_template_15T_mech(self):
        # arrange
        template_path = create_resources_path('resources/tool_adapters/ansys/15T_mech.template')
        output_dir = create_resources_path('resources/tool_adapters/ansys/')
        index = 0

        # act
        AnsysInputBuilder.update_input_template(template_path, index, output_dir, '15T_mech_%d.inp')

        # assert
        inp_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_0.inp')
        inp_ref_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_0_ref.inp')

        # # read reference
        inp_ref = text_file.readlines(inp_ref_path)

        # # read created file
        inp = text_file.readlines(inp_path)

        # # compare two strings
        assert inp_ref == inp

    def test_update_ansys_input_template_15T_mech_post_roxie(self):
        # arrange
        template_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_post_roxie.template')
        output_dir = create_resources_path('resources/tool_adapters/ansys/')
        index = 0

        # act
        AnsysInputBuilder.update_input_template(template_path, index, output_dir, '15T_mech_post_roxie_%d.inp')

        # assert
        inp_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_post_roxie_0.inp')
        inp_ref_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_post_roxie_0_ref.inp')

        # # read reference
        inp_ref = text_file.readlines(inp_ref_path)

        # # read created file
        inp = text_file.readlines(inp_path)

        # # compare two strings
        assert inp_ref == inp

    def test_update_ansys_input_template_15T_mech_solu(self):
        # arrange
        template_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_solu.template')
        output_dir = create_resources_path('resources/tool_adapters/ansys/')
        index = 0

        # act
        AnsysInputBuilder.update_input_template(template_path, index, output_dir, '15T_mech_solu_%d.inp')

        # assert
        inp_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_solu_0.inp')
        inp_ref_path = create_resources_path('resources/tool_adapters/ansys/15T_mech_solu_0_ref.inp')

        # # read reference
        inp_ref = text_file.readlines(inp_ref_path)

        # # read created file
        inp = text_file.readlines(inp_path)

        # # compare two strings
        assert inp_ref == inp
