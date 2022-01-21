import unittest
from unittest.mock import patch

from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.geometry.GeometryCheck import GeometryCheck
from magnumapi.geometry.GeometryFactory import GeometryFactory
from tests.resource_files import create_resources_path, read_csv_as_pd


class GeometryCheckTest(unittest.TestCase):
    layer_dct_defs = [
        {"no": 1, "symm": 1, "typexy": 1, "blocks": [1, 2, 3, 4]},
        {"no": 2, "symm": 1, "typexy": 1, "blocks": [5, 6, 7]},
        {"no": 3, "symm": 1, "typexy": 1, "blocks": [8, 9, 10]},
        {"no": 4, "symm": 1, "typexy": 1, "blocks": [11, 12]}]

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_first_quadrant_pass(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.57294, 'nco': 4, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 23.0, 'nco': 5, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 50.8, 'nco': 2, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 65.5, 'nco': 2, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'type': 1,
                       'condname': '16TOL77B', 'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'type': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'type': 1,
                       'condname': '16TOL77B', 'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'type': 1,
                       'condname': '16TOL77B', 'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertFalse(GeometryCheck.is_outside_of_first_quadrant(geometry))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_first_quadrant_sm_ct_fail(self, mock_show=None):
        # arrange
        json_path = create_resources_path('resources/geometry/roxie/SM_CT/SM_CT_rel.json')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_json(json_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertFalse(GeometryCheck.is_outside_of_first_quadrant(geometry))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_too_sharp_wedge_pass(self, mock_show=None):
        # arrange
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/ins_relative_block_data_trapezoid.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()
        geometry.plot_bare_blocks()

        # assert
        is_wedge_tip_too_sharp = GeometryCheck.is_wedge_tip_too_sharp(geometry, min_value_in_mm=2)

        # check if a wedge is not too sharp
        self.assertEqual(False, is_wedge_tip_too_sharp)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_too_sharp_wedge_fail(self, mock_show=None):
        # arrange
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/ins_relative_block_data_trapezoid.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()
        geometry.plot_bare_blocks()

        # assert
        is_wedge_tip_too_sharp = GeometryCheck.is_wedge_tip_too_sharp(geometry, min_value_in_mm=5)

        # check if a wedge is not too sharp
        self.assertTrue(is_wedge_tip_too_sharp)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_overlapping_turns_pass(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.57294, 'nco': 4, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 23.0, 'nco': 5, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 50.8, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 65.5, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertFalse(GeometryCheck.are_turns_overlapping(geometry))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_overlapping_turns_fail(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.57294, 'nco': 8, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 23.0, 'nco': 5, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 50.8, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 65.5, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertTrue(GeometryCheck.are_turns_overlapping(geometry))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_is_outside_of_first_quadrant_fail(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.5729, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 38.4482, 'nco': 3, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 60.7555, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 87.2871, 'nco': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertTrue(GeometryCheck.is_outside_of_first_quadrant(geometry))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_is_bending_radius_too_small_true(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.5729, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 38.4482, 'nco': 3, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 60.7555, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 87.2871, 'nco': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertTrue(GeometryCheck.is_bending_radius_too_small(geometry, angle_bending_deg_min=15))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_is_bending_radius_too_small_false(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.5729, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 38.4482, 'nco': 3, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 60.7555, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 70.2871, 'nco': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertFalse(GeometryCheck.is_bending_radius_too_small(geometry, angle_bending_deg_min=15))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_is_conductor_radiality_too_skewed_false(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.5729, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 38.4482, 'nco': 3, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 60.7555, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 87.2871, 'nco': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertFalse(GeometryCheck.is_conductor_radiality_too_skewed(geometry, radiality_max_angle_deg=32))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_consistency_is_conductor_radiality_too_skewed_true(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.5729, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 38.4482, 'nco': 3, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 60.7555, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 87.2871, 'nco': 1, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1},
                      {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'condname': '16TOL77B',
                       'current': 13500, 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0, 'type': 1}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        self.assertTrue(GeometryCheck.is_conductor_radiality_too_skewed(geometry, radiality_max_angle_deg=25))

        # assert
        if mock_show is not None:
            mock_show.assert_called()
