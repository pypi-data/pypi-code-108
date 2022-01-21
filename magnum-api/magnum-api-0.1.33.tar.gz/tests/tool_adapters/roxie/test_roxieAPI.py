import unittest

import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI
from tests.resource_files import create_resources_path


class TestRoxieAPI(unittest.TestCase):
    def test_find_index_start_and_length_bottom_header_table(self):
        # arrange
        keyword = 'CABLE'

        # act
        # assert
        with self.assertRaises(Exception) as context:
            RoxieAPI.find_index_start_and_length_bottom_header_table('', keyword)

        self.assertTrue('Not found start index and length for keyword CABLE' in str(context.exception))

    def test_read_nested_bottom_header_table(self):
        # arrange
        data_path = create_resources_path('resources/geometry/roxie/16T/16T_22b-37-optd7f8_gx.data')

        # act
        layer_defs_df = RoxieAPI.read_nested_bottom_header_table(data_path, keyword='LAYER')


if __name__ == '__main__':
    unittest.main()
