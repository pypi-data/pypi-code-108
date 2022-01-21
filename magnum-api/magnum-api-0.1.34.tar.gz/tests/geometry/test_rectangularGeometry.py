import unittest
from unittest.mock import patch

import pandas as pd

from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.geometry.primitives.Line import Line
from magnumapi.geometry.blocks.RectangularBlock import RectangularBlock
from magnumapi.cadata.CableDatabase import CableDatabase
from tests.resource_files import read_csv_as_pd, create_resources_path


class TestRectangularGeometry(unittest.TestCase):

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_rectangle_with_dict(self, mock_show=None):
        # arrange
        block_def = [
            {'no': 1, 'radius': 40.0, 'phi': 0, 'alpha': 0.0, 'nco': 3, 'type': 2, 'current': 13500,
             'condname': 'SMC11T100', 'n1': 2, 'n2': 20, 'imag': 0, 'turn': 0}]
        layer_def = [{"no": 1,"symm": 1,"typexy": 1,"blocks": [1]}]

        cadata_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_dict(block_def, layer_def, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/SMC/reference/three_cable_coil.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert - compare to ROXIE
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 40.0000
        # y(1) = 1.5050
        # x(2) = 40.0000
        # y(2) = 0.0000
        # x(3) = 55.0470
        # y(3) = 0.0000
        # x(4) = 55.0470
        # y(4) = 1.5050
        area = geometry.blocks[0].areas[0]
        self.assertAlmostEqual(40.0000, round(area.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(1.5050, round(area.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(55.0470, round(area.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(55.0470, round(area.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(1.5050, round(area.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 2.1547
        # Alph0 (1-4) = 0.0000
        # Phi0 (2-3) = 0.0000
        # Alph0 (2-3) = 0.0000
        self.assertAlmostEqual(2.1547, area.get_line(2).p2.get_phi(), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area.get_line(2)), places=4)
        self.assertAlmostEqual(0.0000, area.get_line(0).p1.get_phi(), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 40.1000
        # y(1) = 1.4050
        # x(2) = 40.1000
        # y(2) = 0.1000
        # x(3) = 54.9470
        # y(3) = 0.1000
        # x(4) = 54.9470
        # y(4) = 1.4050

        area_bare = geometry.blocks[0].get_bare_area(area)

        self.assertAlmostEqual(40.1000, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(1.4050, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.1000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1000, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1000, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(1.4050, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert - compare to ROXIE
        # Conductor number: 2
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 40.0000
        # y(1) = 3.0100
        # x(2) = 40.0000
        # y(2) = 1.5050
        # x(3) = 55.0470
        # y(3) = 1.5050
        # x(4) = 55.0470
        # y(4) = 3.0100
        area = geometry.blocks[0].areas[1]
        self.assertAlmostEqual(40.0000, round(area.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(3.0100, round(area.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(1.5050, round(area.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(55.0470, round(area.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(1.5050, round(area.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(55.0470, round(area.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(3.0100, round(area.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 4.3034
        # Alph0 (1-4) = 0.0000
        # Phi0 (2-3) = 2.1547
        # Alph0 (2-3) = 0.0000
        self.assertAlmostEqual(4.3034, area.get_line(2).p2.get_phi(), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area.get_line(2)), places=4)
        self.assertAlmostEqual(2.1547, area.get_line(0).p1.get_phi(), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 40.1000
        # y(1) = 2.9100
        # x(2) = 40.1000
        # y(2) = 1.6050
        # x(3) = 54.9470
        # y(3) = 1.6050
        # x(4) = 54.9470
        # y(4) = 2.9100

        area_bare = geometry.blocks[0].get_bare_area(area)

        self.assertAlmostEqual(40.1000, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.9100, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.1000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(1.6050, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(1.6050, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.9100, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert - compare to ROXIE
        # Conductor number: 3
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 40.0000
        # y(1) = 4.5150
        # x(2) = 40.0000
        # y(2) = 3.0100
        # x(3) = 55.0470
        # y(3) = 3.0100
        # x(4) = 55.0470
        # y(4) = 4.5150
        area = geometry.blocks[0].areas[2]
        self.assertAlmostEqual(40.0000, round(area.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.5150, round(area.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(3.0100, round(area.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(55.0470, round(area.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(3.0100, round(area.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(55.0470, round(area.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(4.5150, round(area.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 6.4400
        # Alph0 (1-4) = 0.0000
        # Phi0 (2-3) = 4.3034
        # Alph0 (2-3) = 0.0000
        self.assertAlmostEqual(6.4400, area.get_line(2).p2.get_phi(), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area.get_line(2)), places=4)
        self.assertAlmostEqual(4.3034, area.get_line(0).p1.get_phi(), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 40.1000
        # y(1) = 4.4150
        # x(2) = 40.1000
        # y(2) = 3.1100
        # x(3) = 54.9470
        # y(3) = 3.1100
        # x(4) = 54.9470
        # y(4) = 4.4150

        area_bare = geometry.blocks[0].get_bare_area(area)

        self.assertAlmostEqual(40.1000, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.4150, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.1000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(3.1100, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(3.1100, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(4.4150, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_rectangle_with_json(self, mock_show=None):
        # arrange
        json_path = create_resources_path('resources/geometry/roxie/SMC/three_cable_coil.json')
        cadata_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_json(json_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/SMC/reference/three_cable_coil.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_rectangle_with_data(self, mock_show=None):
        # arrange
        data_path = create_resources_path('resources/geometry/roxie/SMC/three_cable_coil.data')
        cadata_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_data(data_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/SMC/reference/three_cable_coil.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_build_geometry_rectangle_with_csv(self, mock_show=None):
        # arrange
        block_dl_path = create_resources_path('resources/geometry/roxie/SMC/three_cable_coil.csv')
        layer_df_path = create_resources_path('resources/geometry/roxie/SMC/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_csv(block_dl_path, layer_df_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/SMC/reference/three_cable_coil.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("matplotlib.pyplot.show")
    def test_smc_build_geometry_rectangle_with_data(self, mock_show=None):
        # arrange
        data_path = create_resources_path('resources/geometry/roxie/SMC/SMC11T_v3_35turns_ins100_new.data')
        cadata_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_data(data_path, cadata)
        geometry.build_blocks()
        geometry.plot_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/SMC/reference/SMC11T_v3_35turns_ins100_new.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch("plotly.graph_objects.Figure.show")
    def test_smc_plotly_geometry_rectangle_with_data(self, mock_show=None):
        # arrange
        data_path = create_resources_path('resources/geometry/roxie/SMC/SMC11T_v3_35turns_ins100_new.data')
        cadata_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_data(data_path, cadata)
        geometry.build_blocks()
        geometry.plotly_blocks()

        # assert
        geometry_ref = read_csv_as_pd('resources/geometry/roxie/SMC/reference/SMC11T_v3_35turns_ins100_new.csv')
        pd.testing.assert_frame_equal(geometry_ref, geometry.to_df())

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    def test_to_roxie_df_with_csv(self):
        # arrange
        block_df_path = create_resources_path('resources/geometry/roxie/SMC/three_cable_coil.csv')
        layer_df_path = create_resources_path('resources/geometry/roxie/SMC/layer_data.csv')
        cadata_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)

        # act
        geometry = GeometryFactory.init_with_csv(block_df_path, layer_df_path, cadata)

        # assert
        roxie_ref = read_csv_as_pd('resources/geometry/roxie/SMC/three_cable_coil.csv')
        roxie_ref = roxie_ref.rename(columns={val: key for key, val in RectangularBlock.roxie_to_magnum_dct.items()})
        pd.testing.assert_frame_equal(roxie_ref.reset_index(drop=True), geometry.to_block_df().reset_index(drop=True))
