from unittest import TestCase
from unittest.mock import patch

import matplotlib.pyplot as plt

from magnumapi.geometry.primitives.Line import Line
from magnumapi.geometry.blocks.RectangularBlock import RectangularBlock
from magnumapi.geometry.definitions.RectangularBlockDefinition import RectangularBlockDefinition
from magnumapi.cadata.CableDatabase import CableDatabase
from tests.resource_files import create_resources_path


class TestRectangularBlock(TestCase):
    cadata_file_path = create_resources_path('resources/geometry/roxie/SMC/roxie-SMC.cadata')
    cadata = CableDatabase.read_cadata(cadata_file_path)

    # BLOCK 1
    #     1     2     1           40            0            0        10000   07NB3SN2   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current   condname  n1  n2  imag         turn

    #  INSUL 1
    # 29 HFDIP             0.19         0.19 'HF Dipole FNAL                '
    # No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    #  98 07NB3SN2         14.36        1.077        1.403    40          160           10 'HF Dipole FNAL                '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    # 101 07NB3SN2      1 07NB3SN2    HFDIP     HFM46     HFDIP     OST                1.9 'HF Dipole FNAL                '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans              T_o  Comment

    def test_trapezoidal_error(self):
        # arrange
        block_rel_def = RectangularBlockDefinition(x=40, y=0.0, alpha=0.0, nco=1, condname='07NB3SN2', no=1,
                                                   current=10000, type=2, n1=2, n2=20, imag=0, turn=0)

        # act
        with self.assertRaises(AttributeError) as context:
            RectangularBlock(block_def=block_rel_def,
                             cable_def=self.cadata.get_cable_definition('07NB3SN2'),
                             insul_def=self.cadata.get_insul_definition('07NB3SN2'),
                             strand_def=self.cadata.get_strand_definition('07NB3SN2'),
                             conductor_def=self.cadata.get_conductor_definition('07NB3SN2'))

        # assert
        self.assertTrue('Rectangular blocks do not work with trapezoidal cables '
                        '(thickness_i = 1.0770, thickness_o = 1.4030).' in str(context.exception))

    # BLOCK 1
    #     1     2     1           40            0            0        10000  SMC11T100   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current   condname  n1  n2  imag         turn

    #  INSUL 1
    # 28 TININS100          0.1          0.1 'Nb3Sn 100 um after rect.      '
    # No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    # 100 SMC11T2         14.847        1.305        1.305    40           90           10 'Guess 2 for rect. of FNAL_NC  '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    # 106 SMC11T100     1 SMC11T2     HFMD07B   HFM46     TININS100 OST                1.9 'SMC Rect of FNAL_NC 35 turns  '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans              T_o  Comment

    @patch("matplotlib.figure.Figure.show")
    def test_get_first_rect_with_insulation_0_alpha(self, mock_show=None):
        block_rel_def = RectangularBlockDefinition(x=40, y=0.0, alpha=0.0, nco=1, condname='SMC11T100', no=1,
                                                   current=10000, type=2, n1=2, n2=20, imag=0, turn=0)

        block = RectangularBlock(block_def=block_rel_def,
                                 cable_def=self.cadata.get_cable_definition('SMC11T100'),
                                 insul_def=self.cadata.get_insul_definition('SMC11T100'),
                                 strand_def=self.cadata.get_strand_definition('SMC11T100'),
                                 conductor_def=self.cadata.get_conductor_definition('SMC11T100'))

        block.build_block()

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        block.plot_block(ax)
        fig.show()

        area = block.areas[0]

        # assert positions - insulated
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

        area_bare = block.get_bare_area(area)

        self.assertAlmostEqual(40.1000, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(1.4050, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.1000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1000, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1000, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(54.9470, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(1.4050, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     2     1           40            0           45        10000  SMC11T100   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current   condname  n1  n2  imag         turn

    #  INSUL 1
    # 28 TININS100          0.1          0.1 'Nb3Sn 100 um after rect.      '
    # No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    # 100 SMC11T2         14.847        1.305        1.305    40           90           10 'Guess 2 for rect. of FNAL_NC  '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    # 106 SMC11T100     1 SMC11T2     HFMD07B   HFM46     TININS100 OST                1.9 'SMC Rect of FNAL_NC 35 turns  '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans              T_o  Comment

    @patch("matplotlib.figure.Figure.show")
    def test_get_first_rect_with_insulation_45_alpha(self, mock_show=None):
        block_rel_def = RectangularBlockDefinition(x=40, y=0.0, alpha=45.0, nco=1, condname='SMC11T100', no=1,
                                                   current=10000, type=2, n1=2, n2=20, imag=0, turn=0)

        block = RectangularBlock(block_def=block_rel_def,
                                 cable_def=self.cadata.get_cable_definition('SMC11T100'),
                                 insul_def=self.cadata.get_insul_definition('SMC11T100'),
                                 strand_def=self.cadata.get_strand_definition('SMC11T100'),
                                 conductor_def=self.cadata.get_conductor_definition('SMC11T100'))

        block.build_block()

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        block.plot_block(ax)
        fig.show()

        area = block.areas[0]

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 38.9358
        # y(1) = 1.0642
        # x(2) = 40.0000
        # y(2) = 0.0000
        # x(3) = 50.6398
        # y(3) = 10.6398
        # x(4) = 49.5756
        # y(4) = 11.7040
        self.assertAlmostEqual(38.9358, round(area.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(1.0642, round(area.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(50.6398, round(area.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(10.6398, round(area.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(49.5756, round(area.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(11.7040, round(area.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 1.5656
        # Alph0 (1-4) = 45.0000
        # Phi0 (2-3) = 0.0000
        # Alph0 (2-3) = 45.0000
        self.assertAlmostEqual(1.5656, area.get_line(2).p2.get_phi(), places=4)
        self.assertAlmostEqual(45.0000, Line.calculate_relative_alpha_angle(area.get_line(2)), places=4)
        self.assertAlmostEqual(0.0000, area.get_line(0).p1.get_phi(), places=4)
        self.assertAlmostEqual(45.0000, Line.calculate_relative_alpha_angle(area.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 39.0772
        # y(1) = 1.0642
        # x(2) = 40.0000
        # y(2) = 0.1414
        # x(3) = 50.4984
        # y(3) = 10.6398
        # x(4) = 49.5756
        # y(4) = 11.5626

        area_bare = block.get_bare_area(area)

        self.assertAlmostEqual(39.0772, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(1.0642, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1414, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(50.4984, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(10.6398, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(49.5756, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(11.5626, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     2     1           40            0           90        10000  SMC11T100   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current   condname  n1  n2  imag         turn

    #  INSUL 1
    # 28 TININS100          0.1          0.1 'Nb3Sn 100 um after rect.      '
    # No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    # 100 SMC11T2         14.847        1.305        1.305    40           90           10 'Guess 2 for rect. of FNAL_NC  '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    # 106 SMC11T100     1 SMC11T2     HFMD07B   HFM46     TININS100 OST                1.9 'SMC Rect of FNAL_NC 35 turns  '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans              T_o  Comment

    @patch("matplotlib.figure.Figure.show")
    def test_get_first_rect_with_insulation_90_alpha(self, mock_show=None):
        block_rel_def = RectangularBlockDefinition(x=40, y=0.0, alpha=90.0, nco=1, condname='SMC11T100', no=1,
                                                   current=10000, type=2, n1=2, n2=20, imag=0, turn=0)

        block = RectangularBlock(block_def=block_rel_def,
                                 cable_def=self.cadata.get_cable_definition('SMC11T100'),
                                 insul_def=self.cadata.get_insul_definition('SMC11T100'),
                                 strand_def=self.cadata.get_strand_definition('SMC11T100'),
                                 conductor_def=self.cadata.get_conductor_definition('SMC11T100'))

        block.build_block()

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        ax.set_xlim(0, 75)
        ax.set_ylim(0, 75)

        block.plot_block(ax)
        fig.show()

        area = block.areas[0]

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 38.4950
        # y(1) = 0.0000
        # x(2) = 40.0000
        # y(2) = 0.0000
        # x(3) = 40.0000
        # y(3) = 15.0470
        # x(4) = 38.4950
        # y(4) = 15.0470
        self.assertAlmostEqual(38.4950, round(area.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(15.0470, round(area.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(38.4950, round(area.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(15.0470, round(area.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 0.0000
        # Alph0 (1-4) = 90.0000
        # Phi0 (2-3) = 0.0000
        # Alph0 (2-3) = 90.0000
        self.assertAlmostEqual(0.0000, area.get_line(2).p2.get_phi(), places=4)
        self.assertAlmostEqual(90.0000, Line.calculate_relative_alpha_angle(area.get_line(2)), places=4)
        self.assertAlmostEqual(0.0000, area.get_line(0).p1.get_phi(), places=4)
        self.assertAlmostEqual(90.0000, Line.calculate_relative_alpha_angle(area.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 38.5950
        # y(1) = 0.1000
        # x(2) = 39.9000
        # y(2) = 0.1000
        # x(3) = 39.9000
        # y(3) = 14.9470
        # x(4) = 38.5950
        # y(4) = 14.9470

        area_bare = block.get_bare_area(area)

        self.assertAlmostEqual(38.5950, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1000, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(39.9000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.1000, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(39.9000, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(14.9470, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(38.5950, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(14.9470, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()

    # BLOCK 1
    #     1     2     1           40            0           90        10000  SMC11T100   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current   condname  n1  n2  imag         turn

    #  INSUL 1
    # 28 TININS100          0.1          0.1 'Nb3Sn 100 um after rect.      '
    # No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    # 100 SMC11T2         14.847        1.305        1.305    40           90           10 'Guess 2 for rect. of FNAL_NC  '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    # 106 SMC11T100     1 SMC11T2     HFMD07B   HFM46     TININS100 OST                1.9 'SMC Rect of FNAL_NC 35 turns  '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans              T_o  Comment

    @patch("matplotlib.figure.Figure.show")
    def test_get_first_rect_with_insulation_neg90_alpha(self, mock_show=None):
        block_rel_def = RectangularBlockDefinition(x=40, y=0.0, alpha=-90.0, nco=1, condname='SMC11T100', no=1,
                                                   current=10000, type=2, n1=2, n2=20, imag=0, turn=0)

        block = RectangularBlock(block_def=block_rel_def,
                                 cable_def=self.cadata.get_cable_definition('SMC11T100'),
                                 insul_def=self.cadata.get_insul_definition('SMC11T100'),
                                 strand_def=self.cadata.get_strand_definition('SMC11T100'),
                                 conductor_def=self.cadata.get_conductor_definition('SMC11T100'))

        block.build_block()

        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_aspect('equal', 'box')
        ax.grid(True)

        block.plot_block(ax)
        fig.show()

        area = block.areas[0]

        # assert positions - insulated
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 41.5050
        # y(1) = 0.0000
        # x(2) = 40.0000
        # y(2) = 0.0000
        # x(3) = 40.0000
        # y(3) = -15.0470
        # x(4) = 38.4950
        # y(4) = -15.0470
        self.assertAlmostEqual(41.5050, round(area.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(0.0000, round(area.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(40.0000, round(area.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(-15.0470, round(area.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(41.5050, round(area.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(-15.0470, round(area.get_line(2).p1.y, 4), places=4)

        # Positioning angles
        # Phi0 (1-4) = 0.0000
        # Alph0 (1-4) = 270.0000
        # Phi0 (2-3) = 0.0000
        # Alph0 (2-3) = 270.0000
        # The difference is due to orientation of lines in ROXIE and MagNum.
        self.assertAlmostEqual(0.0000, area.get_line(2).p2.get_phi(), places=4)
        self.assertAlmostEqual(90.0000, Line.calculate_relative_alpha_angle(area.get_line(2)), places=4)
        self.assertAlmostEqual(0.0000, area.get_line(0).p1.get_phi(), places=4)
        self.assertAlmostEqual(270.0000, Line.calculate_relative_alpha_angle(area.get_line(0)), places=4)

        # assert positions - bare
        # Conductor number: 1
        # Part of Block: 1
        # Corner co-ordinates:
        # x(1) = 41.4050
        # y(1) = -0.1000
        # x(2) = 40.1000
        # y(2) = -0.1000
        # x(3) = 40.1000
        # y(3) = -14.9470
        # x(4) = 41.4050
        # y(4) = -14.9470

        area_bare = block.get_bare_area(area)

        self.assertAlmostEqual(41.4050, round(area_bare.get_line(3).p1.x, 4), places=4)
        self.assertAlmostEqual(-0.1000, round(area_bare.get_line(3).p1.y, 4), places=4)
        self.assertAlmostEqual(40.1000, round(area_bare.get_line(0).p1.x, 4), places=4)
        self.assertAlmostEqual(-0.1000, round(area_bare.get_line(0).p1.y, 4), places=4)
        self.assertAlmostEqual(40.1000, round(area_bare.get_line(1).p1.x, 4), places=4)
        self.assertAlmostEqual(-14.9470, round(area_bare.get_line(1).p1.y, 4), places=4)
        self.assertAlmostEqual(41.4050, round(area_bare.get_line(2).p1.x, 4), places=4)
        self.assertAlmostEqual(-14.9470, round(area_bare.get_line(2).p1.y, 4), places=4)

        # assert
        if mock_show is not None:
            mock_show.assert_called()


    # BLOCK 1
    #     1     2     3           40            0            0        10000  SMC11T100   2  20     0            0
    #    no  type   nco       radius          phi        alpha      current   condname  n1  n2  imag         turn

    #  INSUL 1
    # 28 TININS100          0.1          0.1 'Nb3Sn 100 um after rect.      '
    # No Name            Radial       Azimut  Comment
    #
    #  CABLE 1
    # 100 SMC11T2         14.847        1.305        1.305    40           90           10 'Guess 2 for rect. of FNAL_NC  '
    #  No Name            height      width_i      width_o    ns      transp.        degrd  Comment
    #
    # CONDUCTOR 1
    # 106 SMC11T100     1 SMC11T2     HFMD07B   HFM46     TININS100 OST                1.9 'SMC Rect of FNAL_NC 35 turns  '
    #  No Name       Type CableGeom.  Strand    Filament  Insul     Trans              T_o  Comment

    @patch("matplotlib.figure.Figure.show")
    def test_homogenize(self, mock_show=None):
        block_rel_def = RectangularBlockDefinition(x=40, y=0.0, alpha=0, nco=3, condname='SMC11T100', no=1,
                                                   current=10000, type=2, n1=2, n2=20, imag=0, turn=0)

        block = RectangularBlock(block_def=block_rel_def,
                                 cable_def=self.cadata.get_cable_definition('SMC11T100'),
                                 insul_def=self.cadata.get_insul_definition('SMC11T100'),
                                 strand_def=self.cadata.get_strand_definition('SMC11T100'),
                                 conductor_def=self.cadata.get_conductor_definition('SMC11T100'))

        block.build_block()

        block_homo = block.homogenize()
        block_homo.build_block()

        assert abs(block_homo.block_def.x - 40.0) <  1e-6
        assert abs(block_homo.block_def.y - 0.0) <  1e-6
        assert abs(block_homo.block_def.x_up_r - 55.047) <  1e-6
        assert abs(block_homo.block_def.y_up_r - 4.515) <  1e-6
