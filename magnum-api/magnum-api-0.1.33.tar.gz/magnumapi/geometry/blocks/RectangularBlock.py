import pandas as pd
import matplotlib.pyplot as plt

from magnumapi.geometry.primitives.Area import Area
from magnumapi.geometry.primitives.Point import Point
from magnumapi.geometry.blocks.Block import Block
from magnumapi.cadata.CableDefinition import CableDefinition
from magnumapi.cadata.ConductorDefinition import ConductorDefinition
from magnumapi.cadata.InsulationDefinition import InsulationDefinition
from magnumapi.geometry.definitions.RectangularBlockDefinition import RectangularBlockDefinition
from magnumapi.geometry.definitions.HomogenizedRectangularBlockDefinition import HomogenizedRectangularBlockDefinition
from magnumapi.cadata.StrandDefinition import StrandDefinition


class RectangularBlock(Block):
    """ RectangularBlock class providing a container and construction method for blocks composed of rectangular turns

    """

    # A dictionary mapping from a ROXIE to magnum naming convention for block definition
    roxie_to_magnum_dct = {"radius": "x",
                           "phi": "y"}

    def __init__(self,
                 block_def: RectangularBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition) -> None:
        """ Constructor of the RectangularBlock class

        An attribute error is raised in case cable definition contains a trapezoidal cable.

        :param block_def: a rectangular block definition with x,y coordinates
        :param cable_def: a cable definition from cadata
        :param insul_def: an insulation definition from cadata
        :param strand_def: a strand definition from cadata
        :param conductor_def: a conductor definition from cadata
        """
        super().__init__(cable_def=cable_def,
                         insul_def=insul_def,
                         strand_def=strand_def,
                         conductor_def=conductor_def)
        self.block_def = block_def

        if self.cable_def.thickness_i != self.cable_def.thickness_o:
            raise AttributeError('Rectangular blocks do not work with trapezoidal cables '
                                 '(thickness_i = %.4f, thickness_o = %.4f).' %
                                 (self.cable_def.thickness_i, self.cable_def.thickness_o))

    def build_block(self) -> None:
        p_shift = Point.of_cartesian(self.block_def.x, self.block_def.y)

        for i in range(self.block_def.nco):
            p1 = Point.of_cartesian(0.0, 0.0)
            p2 = Point.of_cartesian(self.cable_def.width + 2 * self.insul_def.width, 0.0)
            p3 = Point.of_cartesian(self.cable_def.width + 2 * self.insul_def.width,
                                    self.cable_def.thickness_i + 2 * self.insul_def.thickness)
            p4 = Point.of_cartesian(0.0, self.cable_def.thickness_i + 2 * self.insul_def.thickness)
            area = Area.of_closed_ordered_list_of_points(points=(p1, p2, p3, p4))
            area = area.rotate(self.block_def.alpha).translate(p_shift)
            self.areas.append(area)

            p_shift = area.get_line(3).p1.copy()

    def plot_block(self, ax: plt.Axes) -> None:
        for area in self.areas:
            area.plot(ax)

    def plot_bare_block(self, ax: plt.Axes) -> None:
        for bare_area in self.get_bare_areas():
            bare_area.plot(ax)

    def to_block_df(self):
        dct_no_areas = self.to_abs_dict()
        df = pd.DataFrame(dct_no_areas, index=[0])
        return df[['no', 'type', 'nco', 'radius', 'phi', 'alpha', 'current', 'condname', 'n1', 'n2', 'imag', 'turn']]

    def to_abs_dict(self):
        dct = self.block_def.__dict__
        dct_no_areas = {key: value for key, value in dct.items()}
        for key, value in self.roxie_to_magnum_dct.items():
            dct_no_areas[key] = dct_no_areas.pop(value)
        return dct_no_areas

    def to_rel_dict(self, alpha_ref=0.0, phi_ref=0.0):
        raise NotImplementedError('This method is not implemented for this class')

    def get_bare_area(self, area: Area) -> Area:
        p1 = area.get_line(0).p1 + Point.of_cartesian(self.insul_def.width,
                                                      self.insul_def.thickness).rotate(self.block_def.alpha)
        p2 = area.get_line(1).p1 + Point.of_cartesian(-self.insul_def.width,
                                                      self.insul_def.thickness).rotate(self.block_def.alpha)
        p3 = area.get_line(2).p1 + Point.of_cartesian(-self.insul_def.width,
                                                      -self.insul_def.thickness).rotate(self.block_def.alpha)
        p4 = area.get_line(3).p1 + Point.of_cartesian(self.insul_def.width,
                                                      -self.insul_def.thickness).rotate(self.block_def.alpha)
        return Area.of_closed_ordered_list_of_points(points=(p1, p2, p3, p4))

    def homogenize(self):
        if not self.areas:
            raise AttributeError('In order to extract a homogenized block definition, areas need to be initialized!')

        # write block corner positions
        # 3 ------- x_up_r, y_up_r
        # |         |
        # |         |
        # x,y------ 1

        x = self.areas[0].get_line(0).p1.x
        y = self.areas[0].get_line(0).p1.y

        x_up_r = self.areas[-1].get_line(2).p1.x
        y_up_r = self.areas[-1].get_line(2).p1.y

        param_dct = dict(no=self.block_def.no, type=1, nco=self.block_def.nco, x=x, y=y, x_up_r=x_up_r, y_up_r=y_up_r,
                         current=self.block_def.current, condname=self.block_def.condname, alpha=self.block_def.alpha,
                         n1=self.block_def.n1, n2=self.block_def.n2, imag=self.block_def.imag,
                         turn=self.block_def.turn)

        return HomogenizedRectangularBlock(block_def=HomogenizedRectangularBlockDefinition(**param_dct),
                                           cable_def=self.cable_def,
                                           strand_def=self.strand_def,
                                           conductor_def=self.conductor_def,
                                           insul_def=self.insul_def)


class HomogenizedRectangularBlock(RectangularBlock):
    """ HomogenizedRectangularBlock class providing a container and construction method for blocks composed of
    homogenized rectangular turns

    """

    def __init__(self,
                 block_def: HomogenizedRectangularBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition) -> None:
        super().__init__(block_def, cable_def, insul_def, strand_def, conductor_def)
        self.block_def = block_def

    def plot_block(self, ax):
        self.areas[0].plot(ax)

    def to_block_df(self):
        raise NotImplementedError('This method is not implemented for this class')

    def to_abs_dict(self):
        raise NotImplementedError('This method is not implemented for this class')

    def to_rel_dict(self, alpha_ref, phi_ref):
        raise NotImplementedError('This method is not implemented for this class')

    def build_block(self):
        # write block corner positions
        # 3 ------- 2
        # |         |
        # |         |
        # 0 ------- 1
        p0 = Point.of_polar(self.block_def.x, self.block_def.y)
        p1 = Point.of_polar(self.block_def.x_up_r, self.block_def.y)
        p2 = Point.of_polar(self.block_def.x_up_r, self.block_def.y_up_r)
        p3 = Point.of_polar(self.block_def.x, self.block_def.y_up_r)
        self.areas = [Area.of_closed_ordered_list_of_points((p0, p1, p2, p3))]

    def homogenize(self):
        return self
