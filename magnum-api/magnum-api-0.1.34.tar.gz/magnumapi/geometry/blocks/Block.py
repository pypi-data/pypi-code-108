from abc import ABC, abstractmethod
from typing import List

import pandas as pd
import matplotlib.pyplot as plt

from magnumapi.geometry.definitions.BlockDefinition import BlockDefinition
from magnumapi.geometry.primitives.Area import Area
from magnumapi.cadata.CableDefinition import CableDefinition
from magnumapi.cadata.ConductorDefinition import ConductorDefinition
from magnumapi.cadata.InsulationDefinition import InsulationDefinition
from magnumapi.cadata.StrandDefinition import StrandDefinition


class Block(ABC):
    """ An Block class implementing a container with block definitions from cadata input.
    In addition, the class stores initialized coordinates of all conductors per block.
    This is a base class extended by implementations of different types (cos-theta, rectangular, etc.).
    """

    def __init__(self,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition) -> None:
        """ Method constructing an instance of a Block class

        :param cable_def: a cable definition from cadata
        :param insul_def: an insulation definition from cadata
        :param strand_def: a strand definition from cadata
        :param conductor_def: a conductor definition from cadata
        """
        self.cable_def = cable_def
        self.insul_def = insul_def
        self.strand_def = strand_def
        self.conductor_def = conductor_def
        self.block_def: BlockDefinition = None
        self.areas: List[Area] = []

    def compute_surface(self):
        """ Method computing surface of a block as S = nco * ns * S_strand,
        where S_strand = pi * d_strand^2 / 4

        :return: a surface of a block in mm^2
        """
        return self.block_def.nco * self.cable_def.n_s * self.strand_def.compute_surface()

    def compute_surface_cu(self):
        """ Method computing copper surface of a block as S = nco * ns * S_strand_cu,
        where S_strand_cu = f_cu * pi * d_strand^2 / 4

        :return: a copper surface of a block in mm^2
        """
        return self.block_def.nco * self.cable_def.n_s * self.strand_def.compute_surface_cu()

    def compute_surface_nocu(self):
        """ Method computing copper surface of a block as S = nco * ns * S_strand_nocu,
        where S_strand_nocu = f_nocu * pi * d_strand^2 / 4

        :return: a non-copper surface of a block in mm^2
        """
        return self.block_def.nco * self.cable_def.n_s * self.strand_def.compute_surface_nocu()

    @abstractmethod
    def plot_block(self, ax: plt.Axes) -> None:
        """ Abstract method for plotting an insulated block

        :param ax: a matplotlib axis on which a block will be plotted
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def plot_bare_block(self, ax: plt.Axes) -> None:
        """ Abstract method for plotting a bare block

        :param ax: a matplotlib axis on which a bare block will be plotted
        """
        raise NotImplementedError('This method is not implemented for this class')

    def empty_areas(self) -> None:
        """ Method setting areas to an empty array

        """
        self.areas = []

    def get_bare_areas(self) -> List[Area]:
        """ Method returning bare areas, i.e., areas without insulation

        :return: a list of areas without insulation of a given block
        """
        return [self.get_bare_area(area) for area in self.areas]

    def get_bare_area(self, area_ins: Area) -> Area:
        """ Abstract method for returning a bare area

        :param area_ins: an insulated area
        :return: a bare area
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def build_block(self) -> None:
        """ Abstract method for building a block

        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def to_block_df(self) -> pd.DataFrame:
        """ Abstract method for converting a block definition into a ROXIE-compatible dataframe

        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def to_abs_dict(self):
        """ Abstract method for returning the absolute dictionary for block definition

        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def to_rel_dict(self, alpha_ref: float, phi_ref: float):
        """ Abstract method for returning the absolute dictionary for block definition

        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def homogenize(self):
        """ Abstract method for homogenizing a block

        """
        raise NotImplementedError('This method is not implemented for this class')

    def to_df(self) -> pd.DataFrame:
        """ Method concatenating rows representing coordinates of each area into a dataframe

        :return: a dataframe with coordinate information of each area of a block instance
        """
        return pd.concat([area.to_df() for area in self.areas], axis=0)

    def is_outside_of_first_quadrant(self, eps=1e-30) -> True:
        """ Method checking whether at least one area of a given block are outside of the first quadrant

        :param eps: a machine precision for comparison of 0 value
        :return: True if at least one area of a given block is outside of the first quadrant,
        False otherwise, i.e., if all areas are within the first quadrant.
        """
        if not self.areas:
            return False

        is_inside_first_quadrant = False
        for area in self.areas:
            is_inside_first_quadrant |= Area.is_outside_of_first_quadrant(area, eps=eps)

        return is_inside_first_quadrant
