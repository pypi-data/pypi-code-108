from unittest import TestCase
from unittest.mock import patch

import matplotlib.pyplot as plt

from magnumapi.geometry.GeometryChange import GeometryChange
from magnumapi.geometry.primitives.Area import Area
from magnumapi.geometry.blocks.CosThetaBlock import RelativeCosThetaBlock, CosThetaBlock
from magnumapi.geometry.primitives.Line import Line
from magnumapi.geometry.primitives.Point import Point
from magnumapi.geometry.definitions.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.cadata.CableDatabase import CableDatabase
from tests.resource_files import create_resources_path


class TestCosThetaBlock(TestCase):
    cadata_file_path = create_resources_path('resources/geometry/roxie/16T/roxieold_2.cadata')
    cadata = CableDatabase.read_cadata(cadata_file_path)

    # BLOCK 1
    #     1     1     1            0          0              0        13500     16TIL6B   2 20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn

    #  INSUL 1
    #   1 BARE                 0            0 'BARE                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TILG6B         21.84       2.2595       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6B       1 16TILG6B     STR11     NB3SN2    BARE    NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_rect_no_insulation_no_radius_no_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=0, phi_r=0.0, alpha_r=0.0, nco=1, condname='16TIL6B',
                                                        no=1, current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6B'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6B'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6B'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6B'))
        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref,
                                                           alpha_ref=block.get_alpha())
        area_shift = area_ins.copy()

        if block.is_area_intersecting_or_within_radius(area_ins):
            area_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_phi()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_shift)
            area_shift = area_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_shift.plot(ax)
        plt.show()

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 0.0000
        # y(1) = 2.2595
        # x(2) = 0.0000
        # y(2) = 0.0000
        # x(3) = 21.8400
        # y(3) = 0.0000
        # x(4) = 21.8400
        # y(4) = 2.2595
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.2595, round(area_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8400, round(area_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8400, round(area_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.2595, round(area_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = NaN
        # Alph0 (1-4) = 0.0000
        # Phi0 (2-3) = 90.0000
        # Alph0 (2-3) = 0.0000

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 0.0000
        # y(1) = 2.2595
        # x(2) = 0.0000
        # y(2) = 0.0000
        # x(3) = 21.8400
        # y(3) = 0.0000
        # x(4) = 21.8400
        # y(4) = 2.2595

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_shift.get_line(0)))

        self.assertAlmostEqual(0.0000, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.2595, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8400, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8400, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.2595, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     1            0          0              0        13500     16TILG6   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn

    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'eurocircol                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TILG6B         21.84       2.2595       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6C       1 16TILG6B     STR11     NB3SN2   16TINS2    NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_rect_with_insulation_no_radius_no_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=0, phi_r=0.0, alpha_r=0.0, nco=1, condname='16TIL6B',
                                                        no=1, current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6C'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6C'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6B'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6B'))
        p_ref = Point.of_polar(block.block_def.radius, block.block_def.phi_r)
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref,
                                                           alpha_ref=block.get_alpha())
        area_shift = area_ins.copy()

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_shift.plot(ax)
        plt.show()

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 0.0000
        # y(1) = 2.5595
        # x(2) = 0.0000
        # y(2) = 0.0000
        # x(3) = 22.1400
        # y(3) = 0.0000
        # x(4) = 22.1400
        # y(4) = 2.5595
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.5595, round(area_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(22.1400, round(area_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(22.1400, round(area_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.5595, round(area_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = NaN
        # Alph0 (1-4) = 0.0000
        # Phi0 (2-3) = 90.0000
        # Alph0 (2-3) = 0.0000

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 0.1500
        # y(1) = 2.5595
        # x(2) = 0.1500
        # y(2) = 0.1500
        # x(3) = 22.1400
        # y(3) = 0.0000
        # x(4) = 22.1400
        # y(4) = 2.5595

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_shift.get_line(0)))

        self.assertAlmostEqual(0.1500, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.4095, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(21.9900, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(21.9900, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.4095, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     1           25          0              0        13500     16TILG6   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn

    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'eurocircol                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TILG6B         21.84       2.2595       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6C       1 16TILG6B     STR11     NB3SN2   16TINS2    NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_rect_with_insulation_with_radius_no_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=0.0, alpha_r=0.0, nco=1, condname='16TIL6C',
                                                        no=1,
                                                        current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6C'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6C'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6B'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6B'))
        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref,
                                                           alpha_ref=block.get_alpha())
        area_shift = area_ins.copy()

        if block.is_area_intersecting_or_within_radius(area_ins):
            area_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_alpha()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_shift)
            area_shift = area_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_shift.plot(ax)
        plt.show()

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 25.0000
        # y(1) = 2.5595
        # x(2) = 25.0000
        # y(2) = 0.0000
        # x(3) = 47.1400
        # y(3) = 0.0000
        # x(4) = 47.1400
        # y(4) = 2.5595
        self.assertAlmostEqual(25.0000, round(area_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.5595, round(area_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.0000, round(area_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(47.1400, round(area_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(47.1400, round(area_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.5595, round(area_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 5.8762
        # Alph0 (1-4) = 0.0000
        # Phi0 (2-3) = 0.0000
        # Alph0 (2-3) = 0.0000
        self.assertAlmostEqual(5.8762, Line.calculate_positioning_angle(area_shift.get_line(2), block.block_def.radius),
                               places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area_shift.get_line(2)), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_positioning_angle(area_shift.get_line(0), block.block_def.radius),
                               places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area_shift.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 25.1500
        # y(1) = 2.4095
        # x(2) = 25.1500
        # y(2) = 0.1500
        # x(3) = 46.9900
        # y(3) = 0.1500
        # x(4) = 46.9900
        # y(4) = 2.4095

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_shift.get_line(0)))

        self.assertAlmostEqual(25.1500, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.4095, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.1500, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.9900, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.9900, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.4095, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     1           25          5              0        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'eurocircol                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TILG6B         21.84       2.2595       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6C       1 16TILG6B     STR11     NB3SN2   16TINS2    NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_rect_with_insulation_with_radius_with_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=5.0, alpha_r=0.0, nco=1, condname='16TIL6C',
                                                        no=1,
                                                        current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6C'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6C'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6B'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6B'))
        p_ref = Point.of_polar(block.block_def.radius, block.block_def.phi_r)
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref,
                                                           alpha_ref=block.get_alpha())
        area_shift = area_ins.copy()

        if block.is_area_intersecting_or_within_radius(area_ins):
            area_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_alpha()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_shift)
            area_shift = area_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_shift.plot(ax)
        plt.show()

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.9049
        # y(1) = 4.7384
        # x(2) = 24.9049
        # y(2) = 2.1789
        # x(3) = 47.0449
        # y(3) = 2.1789
        # x(4) = 47.0449
        # y(4) = 4.7384
        self.assertAlmostEqual(24.9049, round(area_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.7384, round(area_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(24.9049, round(area_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1789, round(area_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(47.0449, round(area_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1789, round(area_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(47.0449, round(area_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(4.7384, round(area_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 10.9257
        # Alph0 (1-4) = 0.0000
        # Phi0 (2-3) = 5.0000
        # Alph0 (2-3) = 0.0000
        self.assertAlmostEqual(10.9257, Line.calculate_positioning_angle(area_shift.get_line(2),
                                                                         block.block_def.radius), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area_shift.get_line(2)), places=4)
        self.assertAlmostEqual(5.0000, Line.calculate_positioning_angle(area_shift.get_line(0),
                                                                        block.block_def.radius), places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area_shift.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 25.0549
        # y(1) = 4.5884
        # x(2) = 25.0549
        # y(2) = 2.3289
        # x(3) = 46.8949
        # y(3) = 2.3289
        # x(4) = 46.8949
        # y(4) = 4.5884

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_shift.get_line(0)))

        self.assertAlmostEqual(25.0549, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.5884, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.0549, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3289, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8949, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3289, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8949, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(4.5884, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     1           25          5             10        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'EUROCIRCOL                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TILG6          21.84       2.2595       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6        1 16TILG6     STR11     NB3SN2    16TINS    NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_rect_with_insulation_with_radius_with_phi_with_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=5.0, alpha_r=10.0, nco=1, condname='16TIL6C',
                                                        no=1, current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6C'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6C'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6B'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6B'))
        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref,
                                                           alpha_ref=block.get_alpha())
        area_shift = area_ins.copy()

        if block.is_area_intersecting_or_within_radius(area_ins):
            area_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_alpha()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_shift, eps=1e-9)
            area_shift = area_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(22, 27)
        ax.set_ylim(0, 10)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_shift.plot(ax)
        plt.show()

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.5541
        # y(1) = 4.7160
        # x(2) = 24.9986
        # y(2) = 2.1954
        # x(3) = 46.8022
        # y(3) = 6.0400
        # x(4) = 46.3577
        # y(4) = 8.5606

        self.assertAlmostEqual(24.5541, round(area_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.7160, round(area_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(24.9986, round(area_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1954, round(area_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8022, round(area_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.0400, round(area_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.3577, round(area_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.5606, round(area_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 10.8723
        # Alph0 (1-4) = 10.0000
        # Phi0 (2-3) = 5.0000
        # Alph0 (2-3) = 10.0000
        self.assertAlmostEqual(10.8723, Line.calculate_positioning_angle(area_shift.get_line(2),
                                                                         block.block_def.radius), places=4)
        self.assertAlmostEqual(10.0000, Line.calculate_relative_alpha_angle(area_shift.get_line(2)), places=4)
        self.assertAlmostEqual(5.0000, Line.calculate_positioning_angle(area_shift.get_line(0),
                                                                        block.block_def.radius), places=4)
        self.assertAlmostEqual(10.0000, Line.calculate_relative_alpha_angle(area_shift.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.7279
        # y(1) = 4.5944
        # x(2) = 25.1202
        # y(2) = 2.3692
        # x(3) = 46.6284
        # y(3) = 6.1617
        # x(4) = 46.2361
        # y(4) = 8.3868

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_shift.get_line(0)))

        self.assertAlmostEqual(24.7279, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.5944, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.1202, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3692, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.6284, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.1617, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.2361, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.3868, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     4            0            0            0        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 BARE                 0            0 'BARE                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TOLG78B        21.84       1.8782       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6D        1 16TOLG78B  STR11     NB3SN2    BARE      NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_trapz_no_insulation_no_radius_no_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=0, phi_r=0.0, alpha_r=0.0, nco=1, condname='16TIL6D',
                                                        no=1,
                                                        current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6D'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6D'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6D'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6D'))
        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref,
                                                           alpha_ref=block.get_alpha())
        area_shift = area_ins.copy()

        if block.is_area_intersecting_or_within_radius(area_ins):
            area_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_alpha()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_shift)
            area_shift = area_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_shift.plot(ax)
        plt.show()

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = -0.0164
        # y(1) = 1.8781
        # x(2) = 0.0000
        # y(2) = 0.0000
        # x(3) = 41.8408
        # y(3) = 0.0000
        # x(4) = 21.8211
        # y(4) = 2.2594
        self.assertAlmostEqual(-0.0164, round(area_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(1.8781, round(area_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8408, round(area_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8211, round(area_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.2594, round(area_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = nan
        # Alph0 (1-4) = 1.003
        # Phi0 (2-3) = 0.0000
        # Alph0 (2-3) = 0.0000
        self.assertAlmostEqual(1.0003, Line.calculate_relative_alpha_angle(area_shift.get_line(2)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = -0.0164
        # y(1) = 1.8781
        # x(2) = 0.0000
        # y(2) = 0.0000
        # x(3) = 41.8408
        # y(3) = 0.0000
        # x(4) = 21.8211
        # y(4) = 2.2594

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_shift.get_line(0)))

        self.assertAlmostEqual(-0.0164, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(1.8781, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8408, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(21.8211, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.2594, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     4            0            0            0        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'eurocircol                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TOLG78B        21.84       1.8782       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6E        1 16TOLG78B  STR11     NB3SN2    16TINS2   NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_trapz_with_insulation_no_radius_no_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=0, phi_r=0.0, alpha_r=0.0, nco=1, condname='16TIL6E',
                                                        no=1,
                                                        current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6E'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6E'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6E'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6E'))
        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref,
                                                           alpha_ref=block.get_alpha())
        area_shift = area_ins.copy()

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_shift.plot(ax)
        plt.show()

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = -0.0190
        # y(1) = 2.1755
        # x(2) = 0.0000
        # y(2) = 0.0000
        # x(3) = 22.1408
        # y(3) = 0.0000
        # x(4) = 22.1185
        # y(4) = 2.5620
        self.assertAlmostEqual(-0.0190, round(area_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1755, round(area_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(22.1408, round(area_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(22.1185, round(area_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.5620, round(area_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = nan
        # Alph0 (1-4) = 1.003
        # Phi0 (2-3) = 0.0000
        # Alph0 (2-3) = 0.0000
        self.assertAlmostEqual(1.0003, Line.calculate_relative_alpha_angle(area_shift.get_line(2)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 0.1323
        # y(1) = 2.0281
        # x(2) = 0.1487
        # y(2) = 0.1500
        # x(3) = 21.9895
        # y(3) = 0.1500
        # x(4) = 21.9698
        # y(4) = 2.4094

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_shift.get_line(0)))

        self.assertAlmostEqual(0.1323, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.0281, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(0.1487, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(21.9895, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(21.9698, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.4094, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     4           25            0            0        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'eurocircol                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TOLG78B        21.84       1.8782       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6E        1 16TOLG78B  STR11     NB3SN2    16TINS2   NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_traps_with_insulation_with_radius_no_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=0.0, alpha_r=0.0, nco=1, condname='16TIL6E',
                                                        no=1,
                                                        current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6E'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6E'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6E'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6E'))

        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref, alpha_ref=block.get_alpha())
        area_ins_shift = area_ins.copy()
        if block.is_area_intersecting_or_within_radius(area_ins):
            area_ins_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_alpha()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_ins_shift, eps=1e-9)
            area_ins_shift = area_ins_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.grid(True)
        ax.set_xlim(24.9, 25.1)
        ax.set_ylim(0, 3)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_ins_shift.plot(ax)
        plt.show()

        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.9820
        # y(1) = 2.1755
        # x(2) = 25.0010
        # y(2) = 0.0000
        # x(3) = 47.1418
        # y(3) = 0.0000
        # x(4) = 47.1194
        # y(4) = 2.5620
        self.assertAlmostEqual(24.9820, round(area_ins_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1755, round(area_ins_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.0010, round(area_ins_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_ins_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(47.1418, round(area_ins_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area_ins_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(47.1194, round(area_ins_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.5620, round(area_ins_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0(1 - 4) = 4.9891
        # Alph0(1 - 4) = 1.0003
        # Phi0(2 - 3) = 0.0000
        # Alph0(2 - 3) = 0.0000
        self.assertAlmostEqual(4.9891, round(
            Line.calculate_positioning_angle(area_ins_shift.get_line(2), block.block_def.radius), 4), places=4)
        self.assertAlmostEqual(1.0003, round(Line.calculate_relative_alpha_angle(area_ins_shift.get_line(2)), 4),
                               places=4)
        self.assertAlmostEqual(0.0000,
                               Line.calculate_positioning_angle(area_ins_shift.get_line(0), block.block_def.radius),
                               places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area_ins_shift.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 25.1333
        # y(1) = 2.0281
        # x(2) = 25.1496
        # y(2) = 0.1500
        # x(3) = 46.9905
        # y(3) = 0.1500
        # x(4) = 46.9708
        # y(4) = 2.4094

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_ins_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_ins_shift.get_line(0)))

        self.assertAlmostEqual(25.1333, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(2.0281, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.1496, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.9905, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1500, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.9708, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(2.4094, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     4           25            5            0        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'eurocircol                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TOLG78B        21.84       1.8782       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6E        1 16TOLG78B  STR11     NB3SN2    16TINS2   NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_trapz_with_insulation_with_radius_with_phi_no_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=5.0, alpha_r=0.0, nco=1, condname='16TIL6E',
                                                        no=1,
                                                        current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6E'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6E'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6E'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6E'))

        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref, alpha_ref=block.get_alpha())
        area_ins_shift = area_ins.copy()
        if block.is_area_intersecting_or_within_radius(area_ins):
            area_ins_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_alpha()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_ins_shift, eps=1e-6)
            area_ins_shift = area_ins_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_ins_shift.plot(ax)
        plt.show()

        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 24.8859
        # y(1) = 4.3544
        # x(2) = 24.9049
        # y(2) = 2.1789
        # x(3) = 47.0457
        # y(3) = 2.1789
        # x(4) = 47.0233
        # y(4) = 4.7409
        self.assertAlmostEqual(24.8859, round(area_ins_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.3544, round(area_ins_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(24.9049, round(area_ins_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1789, round(area_ins_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(47.0457, round(area_ins_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1789, round(area_ins_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(47.0233, round(area_ins_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(4.7409, round(area_ins_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0(1 - 4) = 10.0199
        # Alph0(1 - 4) = 1.0003
        # Phi0(2 - 3) = 5.0000
        # Alph0(2 - 3) = 0.0000
        self.assertAlmostEqual(10.0199,
                               Line.calculate_positioning_angle(area_ins_shift.get_line(2), block.block_def.radius),
                               places=4)
        self.assertAlmostEqual(1.0003, Line.calculate_relative_alpha_angle(area_ins_shift.get_line(2)), places=4)
        self.assertAlmostEqual(5.0000,
                               Line.calculate_positioning_angle(area_ins_shift.get_line(0), block.block_def.radius),
                               places=4)
        self.assertAlmostEqual(0.0000, Line.calculate_relative_alpha_angle(area_ins_shift.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 25.0372
        # y(1) = 4.2070
        # x(2) = 25.0536
        # y(2) = 2.3289
        # x(3) = 46.8944
        # y(3) = 2.3289
        # x(4) = 46.8747
        # y(4) = 4.5883

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_ins_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_ins_shift.get_line(0)))

        self.assertAlmostEqual(25.0372, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.2070, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.0536, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3289, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8944, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3289, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8747, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(4.5883, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     1     4           25            5           10        13500     16TIL9   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current    condname  n1 n2  imag         turn
    #  INSUL 1
    #   1 16TINS2           0.15         0.15 'eurocircol                    '
    #  No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #   1 16TOLG78B        21.84       1.8782       2.2595    38          100            3 'EUROCIRCOL 26 STR             '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    #   1 16TIL6E        1 16TOLG78B  STR11     NB3SN2    16TINS2   NONE      NB3SN                1.9 'eurocircol                    '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans     QuenchMat.           T_o  Comment
    @patch("matplotlib.pyplot.show")
    def test_get_first_isosceles_trapezium_trapz_with_insulation_with_radius_with_phi_with_alpha(self, mock_show=None):
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=5.0, alpha_r=10.0, nco=1, condname='16TIL6E',
                                                        no=1, current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6E'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6E'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6E'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6E'))

        p_ref = Point.of_polar(block.block_def.radius, block.get_phi())
        area_ins = block.get_insulated_isosceles_trapezium(p_ref=p_ref, alpha_ref=block.get_alpha())
        area_ins_shift = area_ins.copy()
        if block.is_area_intersecting_or_within_radius(area_ins):
            area_ins_shift = area_ins.translate(Point.of_polar(2 * block.cable_def.thickness_i, block.get_alpha()))
            shift = Area.find_trapezoid_shift_to_intercept_with_radius(block.block_def.radius, area_ins_shift, eps=1e-6)
            area_ins_shift = area_ins_shift.translate(area_ins.get_line(0).unit() * shift)

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        circle = plt.Circle((0, 0), block.block_def.radius, color='r', fill=False)
        ax.add_patch(circle)
        area_ins.plot(ax)
        area_ins_shift.plot(ax)
        plt.show()

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
        self.assertAlmostEqual(24.6208, round(area_ins_shift.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.3379, round(area_ins_shift.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.0173, round(area_ins_shift.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.1987, round(area_ins_shift.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.8217, round(area_ins_shift.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.0434, round(area_ins_shift.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.3548, round(area_ins_shift.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.5627, round(area_ins_shift.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0(1 - 4) = 9.9922
        # Alph0(1 - 4) = 11.0003
        # Phi0(2 - 3) = 5.0000
        # Alph0(2 - 3) = 10.0000
        self.assertAlmostEqual(9.9922,
                               Line.calculate_positioning_angle(area_ins_shift.get_line(2), block.block_def.radius),
                               places=4)
        self.assertAlmostEqual(11.0003, Line.calculate_relative_alpha_angle(area_ins_shift.get_line(2)), places=4)
        self.assertAlmostEqual(5.0000,
                               Line.calculate_positioning_angle(area_ins_shift.get_line(0), block.block_def.radius),
                               places=4)
        self.assertAlmostEqual(10.0000, Line.calculate_relative_alpha_angle(area_ins_shift.get_line(0)), places=4)

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

        area_bare = block.get_bare_isosceles_trapezium(p_ref=area_ins_shift.get_line(0).p1,
                                                       alpha_ref=Line.calculate_relative_alpha_angle(
                                                           area_ins_shift.get_line(0)))

        self.assertAlmostEqual(24.7954, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(4.2190, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(25.1376, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(2.3723, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(46.6467, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(6.1649, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(46.2349, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(8.3865, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    @patch.multiple(CosThetaBlock, __abstractmethods__=set())
    def test_get_alpha(self):
        # arrange
        cos_theta_block = CosThetaBlock(block_def=None,
                                        cable_def=None,
                                        insul_def=None,
                                        strand_def=None,
                                        conductor_def=None)

        # act
        # assert
        with self.assertRaises(NotImplementedError) as context:
            cos_theta_block.get_alpha()

        self.assertTrue('This method is not implemented for this class' in str(context.exception))

    @patch.multiple(CosThetaBlock, __abstractmethods__=set())
    def test_get_phi(self):
        # arrange
        cos_theta_block = CosThetaBlock(block_def=None,
                                        cable_def=None,
                                        insul_def=None,
                                        strand_def=None,
                                        conductor_def=None)

        # act
        # assert
        with self.assertRaises(NotImplementedError) as context:
            cos_theta_block.get_phi()

        self.assertTrue('This method is not implemented for this class' in str(context.exception))

    @patch.multiple(CosThetaBlock, __abstractmethods__=set())
    def test_to_roxie_df(self):
        # arrange
        cos_theta_block = CosThetaBlock(block_def=None,
                                        cable_def=None,
                                        insul_def=None,
                                        strand_def=None,
                                        conductor_def=None)

        # act
        # assert
        with self.assertRaises(NotImplementedError) as context:
            cos_theta_block.to_block_df()

        self.assertTrue('This method is not implemented for this class' in str(context.exception))

    def test_calculate_radiality_alpha_correction_index_error(self):
        # arrange
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=5.0, alpha_r=10.0, nco=1, condname='16TIL6E',
                                                        no=1, current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6E'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6E'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6E'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6E'))

        # act
        # assert
        with self.assertRaises(IndexError) as context:
            GeometryChange.compute_radial_alpha(block)

        exception_message = 'The list of areas is empty, please build block first with build_block() method.'
        self.assertTrue(exception_message in str(context.exception))

    def test_calculate_radiality_alpha_correction_single_turn(self):
        # arrange
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=5.0, alpha_r=10.0, nco=1, condname='16TIL6E',
                                                        no=1, current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6E'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6E'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6E'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6E'))

        # act
        block.build_block()

        # assert
        alpha_correction = GeometryChange.compute_radial_alpha(block)

        self.assertAlmostEqual(-2.99267610, alpha_correction, places=7)

    def test_calculate_radiality_alpha_correction_five_turns(self):
        # arrange
        block_rel_def = RelativeCosThetaBlockDefinition(radius=25, phi_r=5.0, alpha_r=10.0, nco=5, condname='16TIL6E',
                                                        no=1, current=13500, type=1, n1=2, n2=20, imag=0, turn=0)
        block = RelativeCosThetaBlock(block_def=block_rel_def,
                                      cable_def=self.cadata.get_cable_definition('16TIL6E'),
                                      insul_def=self.cadata.get_insul_definition('16TIL6E'),
                                      strand_def=self.cadata.get_strand_definition('16TIL6E'),
                                      conductor_def=self.cadata.get_conductor_definition('16TIL6E'))

        # act
        block.build_block()

        # assert
        alpha_correction = GeometryChange.compute_radial_alpha(block)

        self.assertAlmostEqual(4.93033090, alpha_correction, places=7)
