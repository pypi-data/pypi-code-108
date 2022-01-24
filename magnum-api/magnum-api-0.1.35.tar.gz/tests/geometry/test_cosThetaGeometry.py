import unittest
from unittest.mock import patch

import pandas as pd

from magnumapi.geometry.GeometryChange import GeometryChange
from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.geometry.GeometryPlot import GeometryPlot
from magnumapi.geometry.primitives.Line import Line
from magnumapi.cadata.CableDatabase import CableDatabase
from tests.resource_files import read_csv_as_pd, create_resources_path


class CosThetaGeometryTest(unittest.TestCase):
    layer_dct_defs = [
        {"no": 1, "symm": 1, "typexy": 1, "blocks": [1, 2, 3, 4]},
        {"no": 2, "symm": 1, "typexy": 1, "blocks": [5, 6, 7]},
        {"no": 3, "symm": 1, "typexy": 1, "blocks": [8, 9, 10]},
        {"no": 4, "symm": 1, "typexy": 1, "blocks": [11, 12]}]

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_bare_absolute_angles_rectangle_roxie(self, mock_show=None):
        # arrange
        blocks_dct_defs = [
            {'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.57294, 'nco': 4, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 23.0, 'nco': 5, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 50.8, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 65.5, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_dct_defs, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_absolute_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    def test_build_geometry_with_bare_absolute_angles_rectangle_roxie_to_df(self):
        # arrange
        blocks_def = [
            {'no': 1, 'radius': 25.0, 'alpha': 0, 'phi': 0.57294, 'nco': 4, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 2, 'radius': 25.0, 'alpha': 26, 'phi': 23.0, 'nco': 5, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 3, 'radius': 25.0, 'alpha': 47, 'phi': 50.8, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 4, 'radius': 25.0, 'alpha': 66, 'phi': 65.5, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 5, 'radius': 39.0, 'alpha': 0, 'phi': 0.36728, 'nco': 7, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 6, 'radius': 39.0, 'alpha': 35, 'phi': 26.0, 'nco': 10, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 7, 'radius': 39.0, 'alpha': 54, 'phi': 61.0, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 8, 'radius': 53.0, 'alpha': 0, 'phi': 0.27026, 'nco': 18, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 9, 'radius': 53.0, 'alpha': 30, 'phi': 31.3, 'nco': 9, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 10, 'radius': 53.0, 'alpha': 50, 'phi': 57.0, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 11, 'radius': 67.45, 'alpha': 0, 'phi': 0.21236, 'nco': 28, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 12, 'radius': 67.45, 'alpha': 30, 'phi': 37.9, 'nco': 11, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_absolute_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        roxie_block_def = read_csv_as_pd(
            'resources/geometry/roxie/16T/reference/roxie_block_def_bare_absolute_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(roxie_block_def, geometry.to_block_df())

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_bare_relative_angles_rectangle_roxie_to_df(self, mock_show=None):
        # arrange
        blocks_def = [
            {'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 4, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 2, 'radius': 25.0, 'alpha_r': 26, 'phi_r': 10.33328, 'nco': 5, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 3, 'radius': 25.0, 'alpha_r': 21, 'phi_r': 12.72078, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 4, 'radius': 25.0, 'alpha_r': 19, 'phi_r': 8.65904, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 5, 'radius': 39.0, 'alpha_r': 0, 'phi_r': 0.36728, 'nco': 7, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 6, 'radius': 39.0, 'alpha_r': 35, 'phi_r': 12.04384, 'nco': 10, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 7, 'radius': 39.0, 'alpha_r': 19, 'phi_r': 15.69139, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 18, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 9, 'radius': 53.0, 'alpha_r': 30, 'phi_r': 4.62409, 'nco': 9, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 10, 'radius': 53.0, 'alpha_r': 20, 'phi_r': 12.82996, 'nco': 2, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 28, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
            {'no': 12, 'radius': 67.45, 'alpha_r': 30, 'phi_r': 4.76003, 'nco': 11, 'type': 1, 'current': 13500,
             'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_relative_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        roxie_block_def = read_csv_as_pd(
            'resources/geometry/roxie/16T/reference/roxie_block_def_bare_relative_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(roxie_block_def, geometry.to_block_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_bare_relative_angles_rectangle_wrong_alignment(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 7, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 2, 'radius': 25.0, 'alpha_r': 2.34375, 'phi_r': 7.921875, 'nco': 2, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 3, 'radius': 25.0, 'alpha_r': 1.09375, 'phi_r': 8.140625, 'nco': 1, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 4, 'radius': 25.0, 'alpha_r': 0.0, 'phi_r': 9.890625, 'nco': 3, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 5, 'radius': 39.0, 'alpha_r': 0, 'phi_r': 0.36728, 'nco': 10, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 6, 'radius': 39.0, 'alpha_r': 2.03125, 'phi_r': 5.515625, 'nco': 12, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 7, 'radius': 39.0, 'alpha_r': 0.9375, 'phi_r': 6.171875, 'nco': 3, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 16, 'type': 1,
                       'current': 13500, 'condname': '16TIL6', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 9, 'radius': 53.0, 'alpha_r': 0.0, 'phi_r': 3.328125, 'nco': 9, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 10, 'radius': 53.0, 'alpha_r': 0.15625, 'phi_r': 5.953125, 'nco': 2, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 30, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 12, 'radius': 67.45, 'alpha_r': 9.84375, 'phi_r': 6.71875, 'nco': 12, 'type': 1,
                       'current': 13500, 'condname': '16TOL77B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_bare_absolute_angles_rectangle_csv(self, mock_show=None):
        # arrange
        root_dir = 'resources/geometry/roxie/16T/'
        block_df_path = create_resources_path('%sbare_absolute_block_data_rectangle.csv' % root_dir)
        layer_df_path = create_resources_path('%slayer_data.csv' % root_dir)
        cadata_path = create_resources_path('%sroxieold_2.cadata' % root_dir)
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_csv(block_df_path, layer_df_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks(xlim=(0, 80), ylim=(0, 80))

        # assert
        geometry_ref = read_csv_as_pd('%sreference/bare_absolute_angles_rectangle_ref.csv' % root_dir)
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_bare_absolute_angles_rectangle_df(self, mock_show=None):
        # arrange
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/bare_absolute_block_data_rectangle.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks(xlim=(0, 80), ylim=(0, 80))

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_absolute_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_bare_relative_angles_rectangle_csv(self, mock_show=None):
        # arrange
        root_dir = 'resources/geometry/roxie/16T/'
        block_df_path = create_resources_path('%sbare_relative_block_data_rectangle.csv' % root_dir)
        layer_df_path = create_resources_path('%slayer_data.csv' % root_dir)
        cadata_path = create_resources_path('%sroxieold_2.cadata' % root_dir)
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_csv(block_df_path, layer_df_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('%sreference/bare_relative_angles_rectangle_ref.csv' % root_dir)
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_bare_relative_angles_rectangle_df(self, mock_show=None):
        # arrange
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/bare_relative_block_data_rectangle.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_relative_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_bare_absolute_angles_rectangle_data(self, mock_show=None):
        # arrange
        data_path = create_resources_path('resources/geometry/roxie/16T/16T_22b-37-optd7f8_gx.data')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_data(data_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks(xlim=(0, 80), ylim=(0, 80))

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_bare_absolute_angles_trapezoid(self, mock_show=None):
        # arrange
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/bare_absolute_block_data_trapezoid.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_absolute_angles_trapezoid_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_bare_relative_angles_trapezoid(self, mock_show=None):
        # arrangee
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/bare_relative_block_data_trapezoid.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_relative_angles_trapezoid_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_ins_relative_angles_rectangle(self, mock_show=None):
        # arrange
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/ins_relative_block_data_rectangle.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/ins_relative_angles_rectangle_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_ins_absolute_angles_trapezoid(self, mock_show=None):
        # arrange
        block_df = read_csv_as_pd('resources/geometry/roxie/16T/ins_absolute_block_data_trapezoid.csv')
        layer_df = read_csv_as_pd('resources/geometry/roxie/16T/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_df(block_df, layer_df, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/ins_absolute_angles_trapezoid_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_with_roxie_ins_relative_angles_trapezoid(self, mock_show=None):
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
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/ins_relative_angles_trapezoid_ref.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_check_geometry_ansys(self, mock_show=None):
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
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     4           25            5           10        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 16TINS            0.15         0.15 'EUROCIRCOL                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TILG6          21.84       1.8782       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6        1 16TILG6     STR11     NB3SN2    16TINS    NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment

    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_three_trapz_with_insulation_with_radius_with_phi_with_alpha_abs(self,
                                                                                                           mock_show=None):

        # arrange
        blocks_def = [
            {'no': 1, 'radius': 25, 'alpha': 10, 'phi': 5, 'nco': 3, 'type': 1, 'current': 13500,
             'condname': '16TOL78B',
             'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]
        layer_def = [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1]}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, layer_def, cadata)

        geometry.build_blocks()
        geometry.plot_blocks()
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.6208
        # y(1) = 4.3379
        # x(2) = 25.0173
        # y(2) = 2.1987
        # x(3) = 46.8217
        # y(3) = 6.0434
        # x(4) = 46.3548
        # y(4) = 8.5627
        self.assertAlmostEqual(24.6208, round(geometry.blocks[0].areas[0].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.3379, round(geometry.blocks[0].areas[0].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.0173, round(geometry.blocks[0].areas[0].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1987, round(geometry.blocks[0].areas[0].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8217, round(geometry.blocks[0].areas[0].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.0434, round(geometry.blocks[0].areas[0].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.3548, round(geometry.blocks[0].areas[0].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.5627, round(geometry.blocks[0].areas[0].get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0(1 - 4) = 9.9922
        # Alph0(1 - 4) = 11.0003
        # Phi0(2 - 3) = 5.0000
        # Alph0(2 - 3) = 10.0000
        self.assertAlmostEqual(9.9922, Line.calculate_positioning_angle(geometry.blocks[0].areas[0].get_line(2),
                                                                        geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(11.0003, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[0].get_line(2)),
                               places=4)
        self.assertAlmostEqual(5.0000, Line.calculate_positioning_angle(geometry.blocks[0].areas[0].get_line(0),
                                                                        geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(10.0000, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[0].get_line(0)),
                               places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.7954
        # y(1) = 4.2190
        # x(2) = 25.1376
        # y(2) = 2.3723
        # x(3) = 46.6467
        # y(3) = 6.1649
        # x(4) = 46.2349
        # y(4) = 8.3865

        bare_blocks = geometry.get_bare_areas_for_blocks()

        self.assertAlmostEqual(24.7954, round(bare_blocks[0][0].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.2190, round(bare_blocks[0][0].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.1376, round(bare_blocks[0][0].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3723, round(bare_blocks[0][0].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.6467, round(bare_blocks[0][0].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.1649, round(bare_blocks[0][0].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.2349, round(bare_blocks[0][0].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.3865, round(bare_blocks[0][0].get_line(2).p1.y, 4), places=4)

        # Conductor number: 3
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 23.6795
        # y(1) = 8.5859
        # x(2) = 24.1505
        # y(2) = 6.4619
        # x(3) = 45.8074
        # y(3) = 11.0654
        # x(4) = 45.2528
        # y(4) = 13.5668
        self.assertAlmostEqual(23.6795, round(geometry.blocks[0].areas[-1].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(8.5859, round(geometry.blocks[0].areas[-1].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(24.1505, round(geometry.blocks[0].areas[-1].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(6.4619, round(geometry.blocks[0].areas[-1].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(45.8074, round(geometry.blocks[0].areas[-1].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(11.0654, round(geometry.blocks[0].areas[-1].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(45.2528, round(geometry.blocks[0].areas[-1].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(13.5668, round(geometry.blocks[0].areas[-1].get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0(1 - 4) = 19.9823
        # Alph0(1 - 4) = 13.0009
        # Phi0(2 - 3) = 14.9796
        # Alph0(2 - 3) = 12.0006
        self.assertAlmostEqual(19.9823, Line.calculate_positioning_angle(geometry.blocks[0].areas[-1].get_line(2),
                                                                         geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(13.0009, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[-1].get_line(2)),
                               places=4)
        self.assertAlmostEqual(14.9796, Line.calculate_positioning_angle(geometry.blocks[0].areas[-1].get_line(0),
                                                                         geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(12.0006, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[-1].get_line(0)),
                               places=4)

        # assert positions - bare
        # Conductor number: 3
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 23.8582
        # y(1) = 8.4732
        # x(2) = 24.2647
        # y(2) = 6.6395
        # x(3) = 45.6282
        # y(3) = 11.1807
        # x(4) = 45.1392
        # y(4) = 13.3866

        bare_blocks = geometry.get_bare_areas_for_blocks()

        self.assertAlmostEqual(23.8582, round(bare_blocks[0][-1].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(8.4732, round(bare_blocks[0][-1].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(24.2647, round(bare_blocks[0][-1].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(6.6395, round(bare_blocks[0][-1].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(45.6282, round(bare_blocks[0][-1].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(11.1807, round(bare_blocks[0][-1].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(45.1392, round(bare_blocks[0][-1].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(13.3866, round(bare_blocks[0][-1].get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_three_trapz_with_insulation_with_radius_with_phi_with_alpha_rel(self,
                                                                                                           mock_show=None):

        # arrange
        blocks_def = [
            {'no': 1, 'radius': 25, 'alpha_r': 10, 'phi_r': 5, 'nco': 3, 'type': 1, 'current': 13500,
             'condname': '16TOL78B', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]
        layer_def = [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1]}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, layer_def, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.6208
        # y(1) = 4.3379
        # x(2) = 25.0173
        # y(2) = 2.1987
        # x(3) = 46.8217
        # y(3) = 6.0434
        # x(4) = 46.3548
        # y(4) = 8.5627
        self.assertAlmostEqual(24.6208, round(geometry.blocks[0].areas[0].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.3379, round(geometry.blocks[0].areas[0].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.0173, round(geometry.blocks[0].areas[0].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1987, round(geometry.blocks[0].areas[0].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8217, round(geometry.blocks[0].areas[0].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.0434, round(geometry.blocks[0].areas[0].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.3548, round(geometry.blocks[0].areas[0].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.5627, round(geometry.blocks[0].areas[0].get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0(1 - 4) = 9.9922
        # Alph0(1 - 4) = 11.0003
        # Phi0(2 - 3) = 5.0000
        # Alph0(2 - 3) = 10.0000
        self.assertAlmostEqual(9.9922, Line.calculate_positioning_angle(geometry.blocks[0].areas[0].get_line(2),
                                                                        geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(11.0003, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[0].get_line(2)),
                               places=4)
        self.assertAlmostEqual(5.0000, Line.calculate_positioning_angle(geometry.blocks[0].areas[0].get_line(0),
                                                                        geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(10.0000, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[0].get_line(0)),
                               places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.7954
        # y(1) = 4.2190
        # x(2) = 25.1376
        # y(2) = 2.3723
        # x(3) = 46.6467
        # y(3) = 6.1649
        # x(4) = 46.2349
        # y(4) = 8.3865

        bare_blocks = geometry.get_bare_areas_for_blocks()

        self.assertAlmostEqual(24.7954, round(bare_blocks[0][0].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.2190, round(bare_blocks[0][0].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.1376, round(bare_blocks[0][0].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3723, round(bare_blocks[0][0].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.6467, round(bare_blocks[0][0].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.1649, round(bare_blocks[0][0].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.2349, round(bare_blocks[0][0].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.3865, round(bare_blocks[0][0].get_line(2).p1.y, 4), places=4)

        # Conductor number: 3
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 23.6795
        # y(1) = 8.5859
        # x(2) = 24.1505
        # y(2) = 6.4619
        # x(3) = 45.8074
        # y(3) = 11.0654
        # x(4) = 45.2528
        # y(4) = 13.5668
        self.assertAlmostEqual(23.6795, round(geometry.blocks[0].areas[-1].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(8.5859, round(geometry.blocks[0].areas[-1].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(24.1505, round(geometry.blocks[0].areas[-1].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(6.4619, round(geometry.blocks[0].areas[-1].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(45.8074, round(geometry.blocks[0].areas[-1].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(11.0654, round(geometry.blocks[0].areas[-1].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(45.2528, round(geometry.blocks[0].areas[-1].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(13.5668, round(geometry.blocks[0].areas[-1].get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0(1 - 4) = 19.9823
        # Alph0(1 - 4) = 13.0009
        # Phi0(2 - 3) = 14.9796
        # Alph0(2 - 3) = 12.0006
        self.assertAlmostEqual(19.9823, Line.calculate_positioning_angle(geometry.blocks[0].areas[-1].get_line(2),
                                                                         geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(13.0009, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[-1].get_line(2)),
                               places=4)
        self.assertAlmostEqual(14.9796, Line.calculate_positioning_angle(geometry.blocks[0].areas[-1].get_line(0),
                                                                         geometry.blocks[0].block_def.radius), places=4)
        self.assertAlmostEqual(12.0006, Line.calculate_relative_alpha_angle(geometry.blocks[0].areas[-1].get_line(0)),
                               places=4)

        # assert positions - bare
        # Conductor number: 3
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 23.8582
        # y(1) = 8.4732
        # x(2) = 24.2647
        # y(2) = 6.6395
        # x(3) = 45.6282
        # y(3) = 11.1807
        # x(4) = 45.1392
        # y(4) = 13.3866

        bare_blocks = geometry.get_bare_areas_for_blocks()

        self.assertAlmostEqual(23.8582, round(bare_blocks[0][-1].get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(8.4732, round(bare_blocks[0][-1].get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(24.2647, round(bare_blocks[0][-1].get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(6.6395, round(bare_blocks[0][-1].get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(45.6282, round(bare_blocks[0][-1].get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(11.1807, round(bare_blocks[0][-1].get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(45.1392, round(bare_blocks[0][-1].get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(13.3866, round(bare_blocks[0][-1].get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_wrongly_generated_geometry(self, mock_show=None):

        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 3, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 2, 'radius': 25.0, 'alpha_r': 2.1875, 'phi_r': 7.375, 'nco': 4, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 3, 'radius': 25.0, 'alpha_r': 9.84375, 'phi_r': 4.09375, 'nco': 2, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 4, 'radius': 25.0, 'alpha_r': 6.71875, 'phi_r': 6.171875, 'nco': 2, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 5, 'radius': 39.0, 'alpha_r': 0.0, 'phi_r': 0.36728, 'nco': 3, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 6, 'radius': 39.0, 'alpha_r': 8.59375, 'phi_r': 8.25, 'nco': 9, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 7, 'radius': 39.0, 'alpha_r': 9.84375, 'phi_r': 3.21875, 'nco': 3, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 18, 'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 9, 'radius': 53.0, 'alpha_r': 9.84375, 'phi_r': 9.5625, 'nco': 12, 'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 10, 'radius': 53.0, 'alpha_r': 3.28125, 'phi_r': 6.828125, 'nco': 0, 'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 30, 'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 12, 'radius': 67.45, 'alpha_r': 0.15625, 'phi_r': 3.0, 'nco': 12, 'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_simplified_magnet_input(self, mock_show=None):
        # arrange
        blocks_def = [{'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 4, 'type': 1, 'current': 13500,
                       'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 2, 'radius': 25.0, 'alpha_r': 23.9998691192517, 'phi_r': 1.9732107800086354, 'nco': 5,
                       'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 3, 'radius': 25.0, 'alpha_r': 18.499836399064584, 'phi_r': 2.2613872613106736, 'nco': 2,
                       'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 4, 'radius': 25.0, 'alpha_r': 17.999934559625828, 'phi_r': 4.545439476728973, 'nco': 2,
                       'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 5, 'radius': 39.0, 'alpha_r': 0.0, 'phi_r': 0.36728, 'nco': 7, 'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 6, 'radius': 39.0, 'alpha_r': 31.499770958690473, 'phi_r': 2.6566334521150843, 'nco': 10,
                       'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 7, 'radius': 39.0, 'alpha_r': 13.99967279812931, 'phi_r': 2.4079874063247146, 'nco': 2,
                       'type': 1,
                       'current': 13500, 'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 8, 'radius': 53.0, 'alpha_r': 0, 'phi_r': 0.27026, 'nco': 18, 'type': 1, 'current': 13500,
                       'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 9, 'radius': 53.0, 'alpha_r': 21.00147158488118, 'phi_r': 1.1333184204627678, 'nco': 9,
                       'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 10, 'radius': 53.0, 'alpha_r': 15.500735792440558, 'phi_r': 10.975148087526826, 'nco': 2,
                       'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 11, 'radius': 67.45, 'alpha_r': 0, 'phi_r': 0.21236, 'nco': 28, 'type': 1,
                       'current': 13500,
                       'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0},
                      {'no': 12, 'radius': 67.45, 'alpha_r': 16.002289132037205, 'phi_r': 1.0131471917431227, 'nco': 11,
                       'type': 1,
                       'current': 13500, 'condname': '16TOL8', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(blocks_def, self.layer_dct_defs, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        # ToDo - fix this test
        # geometry_ref = read_csv_as_pd('resources/geometry/roxie/16T/reference/bare_absolute_angles_rectangle_ref.csv')
        # pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("plotly.graph_objects.Figure.show")
    def test_simplified_magnet_input_plotly_blocks(self, mock_show=None):
        # arrange
        block_def = [{'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 4, 'type': 1, 'current': 13500,
                      'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]
        layer_def = [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1]}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(block_def, layer_def, cadata)
        geometry.build_blocks()
        geometry.plotly_blocks()

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("plotly.graph_objects.Figure.show")
    def test_simplified_magnet_input_plotly_homogenized_blocks(self, mock_show=None):
        # arrange
        block_def = [{'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 4, 'type': 1, 'current': 13500,
                      'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]
        layer_def = [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1]}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(block_def, layer_def, cadata)
        geometry.build_blocks()

        homo_geometry = geometry.homogenize()
        homo_geometry.build_blocks()
        homo_geometry.plotly_blocks()

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    def test_simplified_magnet_input_display_table(self):
        # arrange
        block_def = [{'no': 1, 'radius': 25.0, 'alpha_r': 0, 'phi_r': 0.57294, 'nco': 4, 'type': 1, 'current': 13500,
                      'condname': '16TIL9', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]
        layer_def = [{"no": 1, "symm": 1, "typexy": 1, "blocks": [1]}]

        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(block_def, layer_def, cadata)
        geometry.build_blocks()
        GeometryPlot.display_definition_table(geometry.to_df())

    def test_with_roxie_absolute_angle_definition_json(self):
        # arrange
        json_path = create_resources_path('resources/geometry/roxie/16T/16T_abs.json')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_json(json_path, cadata)

        current = geometry.blocks[0].block_def.current
        f_cu_nocu = geometry.blocks[0].strand_def.f_cu_nocu
        temp_ref = geometry.blocks[0].conductor_def.temp_ref
        rrr = geometry.blocks[0].strand_def.rrr
        d_strand = geometry.blocks[0].strand_def.d_strand
        n_s = geometry.blocks[0].cable_def.n_s

        # assert
        self.assertEqual(13500, current)
        self.assertAlmostEqual(0.85, f_cu_nocu, places=2)
        self.assertAlmostEqual(1.9, temp_ref, places=2)
        self.assertEqual(100, rrr)
        self.assertAlmostEqual(1.1, d_strand, places=2)
        self.assertEqual(22, n_s)

    def test_with_roxie_relative_angle_definition_json(self):
        # arrange
        json_path = create_resources_path('resources/geometry/roxie/16T/16T_rel.json')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_json(json_path, cadata)

        current = geometry.blocks[0].block_def.current
        f_cu_nocu = geometry.blocks[0].strand_def.f_cu_nocu
        temp_ref = geometry.blocks[0].conductor_def.temp_ref
        rrr = geometry.blocks[0].strand_def.rrr
        d_strand = geometry.blocks[0].strand_def.d_strand
        n_s = geometry.blocks[0].cable_def.n_s

        # assert
        self.assertEqual(13500, current)
        self.assertAlmostEqual(0.85, f_cu_nocu, places=2)
        self.assertAlmostEqual(1.9, temp_ref, places=2)
        self.assertEqual(100, rrr)
        self.assertAlmostEqual(1.1, d_strand, places=2)
        self.assertEqual(22, n_s)

    @patch("plotly.graph_objects.Figure.show")
    def test_with_roxie_absolute_angle_definition_json_radiality_corection(self, mock_show=None):
        # arrange
        json_path = create_resources_path('resources/geometry/roxie/16T/16T_abs.json')
        cadata_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_json(json_path, cadata)

        geometry.build_blocks()
        geometry.plotly_blocks(figsize=(90, 90), xlim=(0, 85))

        geometry = GeometryChange.calculate_radial_alpha(geometry)

        # Build corrected blocks
        geometry.build_blocks()

        # Display corrected blocks
        geometry.plotly_blocks(figsize=(90, 90), xlim=(0, 85))

        # assert
        if mock_show is not None:
            mock_show.assert_called()
