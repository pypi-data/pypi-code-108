import math
from abc import abstractmethod
from copy import deepcopy

import pandas as pd
import matplotlib.pyplot as plt

from magnumapi.geometry.primitives.Arc import Arc
from magnumapi.geometry.primitives.Area import Area
from magnumapi.geometry.blocks.Block import Block
from magnumapi.geometry.primitives.Line import Line
from magnumapi.geometry.primitives.Point import Point
from magnumapi.geometry.definitions.HomogenizedBlockDefinition import HomogenizedBlockDefinition
from magnumapi.geometry.definitions.AbsoluteCosThetaBlockDefinition import AbsoluteCosThetaBlockDefinition
from magnumapi.cadata.ConductorDefinition import ConductorDefinition
from magnumapi.geometry.definitions.CosThetaBlockDefinition import CosThetaBlockDefinition
from magnumapi.geometry.definitions.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.cadata.CableDefinition import CableDefinition
from magnumapi.cadata.InsulationDefinition import InsulationDefinition
from magnumapi.cadata.StrandDefinition import StrandDefinition


class CosThetaBlock(Block):
    """ A CosThetaBlock class implementing a container with block definitions from cadata input and cos-theta geometry.
    In addition, the class stores initialized coordinates of all conductors per block of cos-theta type.
    It is a base class for absolute and relative cos-theta blocks.
    """

    def __init__(self,
                 block_def: CosThetaBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition) -> None:
        """ Constructs a CosThetaBlock abstract class instance

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

    @abstractmethod
    def get_alpha(self):
        """ Abstract method for returning the inclination angle

        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def get_phi(self):
        """ Abstract method for returning the positioning angle

        """
        raise NotImplementedError('This method is not implemented for this class')

    def get_radius(self):
        """ Method for returning the block radius

        """
        return self.block_def.radius

    def get_nco(self):
        """ Abstract method for returning the positioning angle

        """
        return self.block_def.nco

    def build_block(self, phi_ref=0.0, alpha_ref=0.0) -> None:
        """ Method building a cos-theta block for absolute and relative definition

        :param phi_ref: reference positioning angle from a previous block (0 by default)
        :param alpha_ref: reference inclination angle from a previous block (0 by default)
        """
        self.areas = []  # to avoid creating duplicate blocks
        phi = phi_ref + self.get_phi()
        alpha = alpha_ref + self.get_alpha()
        p_ref = Point.of_polar(self.get_radius(), phi)

        for nco_i in range(self.get_nco()):
            area = self.get_insulated_isosceles_trapezium(p_ref=p_ref, alpha_ref=alpha)
            area_shift = area.copy()
            if self.is_area_intersecting_or_within_radius(area_shift):
                alpha_top_line = Line.calculate_relative_alpha_angle(area_shift.get_line(0))
                area_shift = area.translate(Point.of_polar(2 * self.cable_def.thickness_i, alpha_top_line))

            shift = Area.find_trapezoid_shift_to_intercept_with_radius(self.get_radius(), area_shift)
            alpha_low = Line.calculate_relative_alpha_angle(area_shift.get_line(0))
            area = area_shift.copy().translate(Point.of_polar(-shift, alpha_low))

            self.areas.append(area)

            p_ref = area.get_line(2).p2.copy()
            alpha = Line.calculate_relative_alpha_angle(self.areas[-1].get_line(2))

    def is_area_intersecting_or_within_radius(self, area: Area) -> bool:
        """ Method checking whether an area of a block is either intersecting with a radius or within a radius.
        If so, then the block needs to be shifted in order to align it with the radius.

        :param area: an area for which the check is performed
        :return: True if one of the two conditions is satisfied, otherwise False
        """
        is_intercepting = Line.find_interception_parameter(self.get_radius(), area.get_line(3)) is not None
        is_within_radius = Line.is_line_intercepting_radius(radius=self.get_radius(), line=area.get_line(3))
        return is_intercepting or is_within_radius

    def get_bare_area(self, area_ins: Area) -> Area:
        """ Method returning a bare are from an insulated one

        :param area_ins: an insulated area
        :return: a bare area
        """
        line_ref = area_ins.get_line(0).copy()
        p_ref = line_ref.p1.copy()
        alpha_ref = Line.calculate_relative_alpha_angle(line_ref)
        return self.get_bare_isosceles_trapezium(p_ref=p_ref, alpha_ref=alpha_ref)

    def get_insulated_isosceles_trapezium(self, p_ref=Point.of_cartesian(0.0, 0.0), alpha_ref=0.0) -> Area:
        """ Method calculating an area as an isosceles trapezium for a cos-theta distribution
        A turn is represented as an isosceles trapezoid of a given height, inner and outer width. When inner and outer
        widths are equal, then the turn is a rectangle. The difference between the inner and outer widths gives the
        keystone angle of a cable. The inner width is in contact with the mandrel radius.

        :return: an area composed of lines
        """
        keystone_half_rad = math.atan(
            (self.cable_def.thickness_o - self.cable_def.thickness_i) / (2 * self.cable_def.width))
        keystone_half_deg = math.degrees(keystone_half_rad)

        area_bare = self.get_bare_isosceles_trapezium(p_ref=p_ref, alpha_ref=alpha_ref)

        # calculate insulation coordinates
        ins_r_projected = self.insul_def.thickness / math.cos(keystone_half_rad)
        ins_a_projected = self.insul_def.width / math.cos(keystone_half_rad)

        p1_ins_r = Point.of_polar(ins_r_projected, 180 + alpha_ref)
        p1_ins_a = Point.of_polar(ins_a_projected, -90 + keystone_half_deg + alpha_ref)
        p1_ins = area_bare.get_line(0).p1 + (p1_ins_r + p1_ins_a)

        p2_ins_r = Point.of_polar(ins_r_projected, alpha_ref)
        p2_ins_a = Point.of_polar(ins_a_projected, -90 + keystone_half_deg + alpha_ref)
        p2_ins = area_bare.get_line(1).p1 + (p2_ins_r + p2_ins_a)

        p3_ins_r = Point.of_polar(ins_r_projected, 2 * keystone_half_deg + alpha_ref)
        p3_ins_a = Point.of_polar(ins_a_projected, 90 + keystone_half_deg + alpha_ref)
        p3_ins = area_bare.get_line(2).p1 + (p3_ins_r + p3_ins_a)

        p4_ins_r = Point.of_polar(ins_r_projected, 180 + 2 * keystone_half_deg + alpha_ref)
        p4_ins_a = Point.of_polar(ins_a_projected, 90 + keystone_half_deg + alpha_ref)
        p4_ins = area_bare.get_line(3).p1 + (p4_ins_r + p4_ins_a)

        return Area.of_closed_ordered_list_of_points(points=(p1_ins, p2_ins, p3_ins, p4_ins))

    def get_bare_isosceles_trapezium(self, p_ref=Point.of_cartesian(0.0, 0.0), alpha_ref=0.0) -> Area:
        """ Method calculating a bare isosceles trapezium

        :param p_ref: a reference point for a bottom left corner of the trapezium, assuming 0 alpha angle
        (0.0 by default)
        :param alpha_ref: reference inclination angle for a trapezium from previous one (0 by default)
        :return: an area with bare isosceles trapezium
        """
        keystone_half_rad = math.atan(
            (self.cable_def.thickness_o - self.cable_def.thickness_i) / (2 * self.cable_def.width))
        keystone_half_deg = math.degrees(keystone_half_rad)
        side = self.cable_def.width / math.cos(keystone_half_rad)

        p1 = p_ref
        p2 = p1 + Point.of_polar(side, alpha_ref)
        p3 = p2.copy() + Point.of_polar(self.cable_def.thickness_o, alpha_ref + 90 + keystone_half_deg)
        p4 = p1 + Point.of_polar(self.cable_def.thickness_i, alpha_ref + 90 + keystone_half_deg)

        area = Area.of_closed_ordered_list_of_points(points=(p1, p2, p3, p4))

        ins_r_projected = self.insul_def.thickness / math.cos(keystone_half_rad)
        ins_a_projected = self.insul_def.width / math.cos(keystone_half_rad)

        p1_ins_r = Point.of_polar(ins_r_projected, 180 + alpha_ref)
        p1_ins_a = Point.of_polar(ins_a_projected, -90 + keystone_half_deg + alpha_ref)

        return area.translate(-(p1_ins_r + p1_ins_a))

    def plot_block(self, ax: plt.Axes) -> None:
        """ Method plotting insulated areas corresponding to a block

        :param ax: a matplotlib axis on which a block will be plotted
        """
        circle = plt.Circle((0, 0), self.get_radius(), color='r', fill=False)
        ax.add_patch(circle)
        for area in self.areas:
            area.plot(ax)

    def plot_bare_block(self, ax: plt.Axes) -> None:
        """ Method plotting bare areas corresponding to a block

        :param ax: a matplotlib axis on which a block will be plotted
        """
        circle = plt.Circle((0, 0), self.get_radius(), color='r', fill=False)
        ax.add_patch(circle)
        for area in self.areas:
            self.get_bare_area(area).plot(ax)

    def homogenize(self):
        if not self.areas:
            raise AttributeError('In order to extract a homogenized block definition, areas need to be initialized!')

        inner_radius = self.block_def.radius
        outer_radius = inner_radius + self.cable_def.width + 2 * self.insul_def.width

        # write block corner angles
        # 4 ----- 3
        # |       |
        # |       |
        # 1-------2
        phi_0 = self.areas[0].get_line(0).p1.get_phi()
        phi_1 = self.areas[0].get_line(0).p2.get_phi()
        phi_2 = self.areas[-1].get_line(2).p1.get_phi()
        phi_3 = self.areas[-1].get_line(2).p2.get_phi()

        param_dct = dict(no=self.block_def.no, type=1, nco=self.block_def.nco, radius_inner=inner_radius,
                         radius_outer=outer_radius, phi_0=phi_0, phi_1=phi_1, phi_2=phi_2, phi_3=phi_3,
                         current=self.block_def.current, condname=self.block_def.condname,
                         n1=self.block_def.n1, n2=self.block_def.n2, imag=self.block_def.imag,
                         turn=self.block_def.turn)

        return HomogenizedCosThetaBlock(block_def=HomogenizedBlockDefinition(**param_dct),
                                        cable_def=self.cable_def, strand_def=self.strand_def,
                                        conductor_def=self.conductor_def,
                                        insul_def=self.insul_def)


class AbsoluteCosThetaBlock(CosThetaBlock):
    """ An AbsoluteCosThetaBlock class implementing a container with block definitions from cadata input and
    absolute cos-theta geometry. It relies on absolute alpha and phi block angles.
    In addition, the class stores initialized coordinates of all conductors per block of cos-theta type.

    """

    def __init__(self,
                 block_def: AbsoluteCosThetaBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition) -> None:
        """ Constructor of AbsoluteCosThetaBlock instance
        :param block_def: an absolute cos-theta block definition with radius information
        :param cable_def: a cable definition from cadata
        :param insul_def: an insulation definition from cadata
        :param strand_def: a strand definition from cadata
        :param conductor_def: a conductor definition from cadata
        """
        super().__init__(block_def, cable_def, insul_def, strand_def, conductor_def)
        self.block_def = block_def

    def get_alpha(self):
        return self.block_def.alpha

    def get_phi(self):
        return self.block_def.phi

    def to_block_df(self):
        dct_no_areas = self.to_abs_dict()
        df = pd.DataFrame(dct_no_areas, index=[0])
        return df[['no', 'type', 'nco', 'radius', 'phi', 'alpha', 'current', 'condname', 'n1', 'n2', 'imag', 'turn']]

    def to_rel_dict(self, alpha_ref=0.0, phi_ref=0.0) -> dict:
        dct = self.to_abs_dict()
        dct['alpha_r'] = dct['alpha'] - alpha_ref
        dct['phi_r'] = dct['phi'] - phi_ref
        dct.pop('alpha')
        dct.pop('phi')
        return dct

    def to_abs_dict(self):
        return deepcopy(self.block_def.__dict__)


class RelativeCosThetaBlock(CosThetaBlock):
    """ A RelativeCosThetaBlock class implementing a container with block definitions from cadata input and
    relative cos-theta geometry. It relies on relative alpha and phi block angles.
    In addition, the class stores initialized coordinates of all conductors per block of cos-theta type.

    """

    def __init__(self,
                 block_def: RelativeCosThetaBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition):
        """ Constructor of RelativeCosThetaBlock instance

        :param block_def: an absolute cos-theta block definition with radius information
        :param cable_def: a cable definition from cadata
        :param insul_def: an insulation definition from cadata
        :param strand_def: a strand definition from cadata
        :param conductor_def: a conductor definition from cadata
        """
        super().__init__(block_def, cable_def, insul_def, strand_def, conductor_def)
        self.block_def = block_def

    def get_alpha(self):
        return self.block_def.alpha_r

    def get_phi(self):
        return self.block_def.phi_r

    def to_block_df(self):
        dct_no_areas = self.to_rel_dict()
        df = pd.DataFrame(dct_no_areas, index=[0])
        return df[['no', 'type', 'nco', 'radius', 'phi_r', 'alpha_r', 'current', 'condname', 'n1', 'n2', 'imag', 'turn']]

    def to_abs_dict(self):
        dct_no_areas = deepcopy(self.block_def.__dict__)
        line_ref = self.areas[0].get_line(0)
        dct_no_areas['alpha'] = Line.calculate_relative_alpha_angle(line_ref)
        dct_no_areas['phi'] = Line.calculate_positioning_angle(line_ref, self.block_def.radius)
        dct_no_areas.pop('alpha_r')
        dct_no_areas.pop('phi_r')
        return dct_no_areas

    def to_rel_dict(self, alpha_ref=0.0, phi_ref=0.0):
        return deepcopy(self.block_def.__dict__)


class HomogenizedCosThetaBlock(Block):
    """ A HomogenizedCosThetaBlock class implementing a container with block definitions from cadata input and
    homogenized cos-theta geometry.
    In addition, the class stores initialized coordinates of all conductors per block of homogenized cos-theta type.

    """

    def __init__(self,
                 block_def: HomogenizedBlockDefinition,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition) -> None:
        super().__init__(cable_def, insul_def, strand_def, conductor_def)
        self.block_def = block_def

    def to_block_df(self):
        raise NotImplementedError('This method is not implemented for this class')

    def to_abs_dict(self):
        raise NotImplementedError('This method is not implemented for this class')

    def to_rel_dict(self, alpha_ref, phi_ref):
        raise NotImplementedError('This method is not implemented for this class')

    def plot_bare_block(self, ax: plt.Axes) -> None:
        raise NotImplementedError('This method is not implemented for this class')

    def get_bare_area(self, area_ins: Area) -> Area:
        raise NotImplementedError('This method is not implemented for this class')

    def plot_block(self, ax):
        self.areas[0].plot(ax)

    def build_block(self):
        p0 = Point.of_polar(self.block_def.radius_inner, self.block_def.phi_0)
        p1 = Point.of_polar(self.block_def.radius_outer, self.block_def.phi_1)
        p2 = Point.of_polar(self.block_def.radius_outer, self.block_def.phi_2)
        p3 = Point.of_polar(self.block_def.radius_inner, self.block_def.phi_3)
        self.areas = [Area.of_lines((Line.of_end_points(p0, p1),
                                     Arc.of_end_points_center(p1, p2),
                                     Line.of_end_points(p2, p3),
                                     Arc.of_end_points_center(p3, p0)))]

    def homogenize(self):
        return self
