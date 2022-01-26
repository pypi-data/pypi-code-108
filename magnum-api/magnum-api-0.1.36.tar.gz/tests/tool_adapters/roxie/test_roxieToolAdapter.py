from unittest import TestCase
from unittest.mock import patch

import pandas as pd

from magnumapi.tool_adapters.roxie.RoxieToolAdapter import RoxieToolAdapter
from tests.resource_files import create_resources_path


class TestRoxieToolAdapter(TestCase):
    @patch("plotly.graph_objects.Figure.show")
    def test_parse_roxie_xml_11T(self, mock_show=None):
        # arrange
        roxie_data_xml_path = create_resources_path('resources/geometry/roxie/11T/reference/roxieData11T.xml')
        strand_data = RoxieToolAdapter.parse_roxie_xml(roxie_data_xml_path)

        # act
        RoxieToolAdapter.plotly_results(strand_data, column='|B|')

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    def test_parse_roxie_xml_16T_formatted(self):
        # arrange
        roxie_data_xml_path = create_resources_path('resources/geometry/roxie/16T/reference/roxieData16T.xml')

        # assert
        with self.assertRaises(IndexError):
            RoxieToolAdapter.parse_roxie_xml(roxie_data_xml_path)

    @patch("plotly.graph_objects.Figure.show")
    def test_parse_roxie_xml_16T_raw(self, mock_show=None):
        # arrange
        roxie_data_xml_path = create_resources_path('resources/geometry/roxie/16T/roxieData.xml')
        roxie_data_formatted_xml_path = create_resources_path(
            'resources/geometry/roxie/16T/roxieData_formatted.xml')

        # act
        RoxieToolAdapter.correct_xml_file(roxie_data_xml_path, roxie_data_formatted_xml_path)

        strand_data = RoxieToolAdapter.parse_roxie_xml(roxie_data_formatted_xml_path)
        RoxieToolAdapter.plotly_results(strand_data, column='|B|', xlim=(0, 85), ylim=(0, 85))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("plotly.graph_objects.Figure.show")
    def test_parse_roxie_xml_16T_two_variable_raw(self, mock_show=None):
        # arrange
        roxie_data_xml_path = create_resources_path('resources/tool_adapters/roxie/roxieDataTwoVariables.xml')
        roxie_data_formatted_xml_path = create_resources_path(
            'resources/tool_adapters/roxie/roxieDataTwoVariables_formatted.xml')

        # act
        RoxieToolAdapter.correct_xml_file(roxie_data_xml_path, roxie_data_formatted_xml_path)

        strand_data_df = RoxieToolAdapter.parse_roxie_xml(roxie_data_formatted_xml_path)
        RoxieToolAdapter.plotly_results(strand_data_df, column='|B|', xlim=(0, 85), ylim=(0, 85))
        RoxieToolAdapter.plotly_results(strand_data_df, column='B3', xlim=(0, 85), ylim=(0, 85))

        roxie_data_xml_path = create_resources_path('resources/tool_adapters/roxie/strand_data_ref.csv')
        strand_data_ref_df = pd.read_csv(roxie_data_xml_path, index_col=0)

        pd.testing.assert_frame_equal(strand_data_df, strand_data_ref_df)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    def test_read_figures_of_merit_table_from_output(self):
        # arrange
        roxie_output = create_resources_path('resources/tool_adapters/roxie/input.output')

        # act
        fom_df = RoxieToolAdapter.read_figures_of_merit_table_from_output(roxie_output)

        # assert
        fom_ref_df = pd.DataFrame([{'S1': 3, 'S2': 1, 'OPER': 'MINABS', 'OBJECTIVE.1': 89.57, 'WEIGHTED OBJ': 8.957},
                                   {'S1': 5, 'S2': 1, 'OPER': 'MINABS', 'OBJECTIVE.1': 8.257, 'WEIGHTED OBJ': 0.8257},
                                   {'S1': 7, 'S2': 1, 'OPER': 'MINABS', 'OBJECTIVE.1': 12.96, 'WEIGHTED OBJ': 1.296},
                                   {'S1': 0, 'S2': 0, 'OPER': '=2', 'OBJECTIVE.1': 65.14, 'WEIGHTED OBJ': 2514.0},
                                   {'S1': 1, 'S2': 1, 'OPER': '=2', 'OBJECTIVE.1': -4.539, 'WEIGHTED OBJ': 218.9}],
                                  index=['B', 'B', 'B', 'MARGMI', 'BIGB'])
        fom_ref_df.index.names = ['OBJECTIVE']


        pd.testing.assert_frame_equal(fom_ref_df, fom_df)

    def test_convert_figures_of_merit_to_dict(self):
        # arrange
        roxie_output = create_resources_path('resources/tool_adapters/roxie/input.output')

        # act
        fom_df = RoxieToolAdapter.read_figures_of_merit_table_from_output(roxie_output)
        fom_dct = RoxieToolAdapter.convert_figures_of_merit_to_dict(fom_df)

        # assert
        fom_dct_ref = {'B_3_1': 89.57, 'B_5_1': 8.257, 'B_7_1': 12.96, 'MARGMI_0_0': 65.14, 'BIGB_1_1': -4.539}

        assert fom_dct == fom_dct_ref
