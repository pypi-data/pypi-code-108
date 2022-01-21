from abc import ABC
import datetime
from copy import deepcopy
from typing import List, Union
from itertools import chain

import pandas as pd

import magnumapi
from magnumapi.geometry.GeometryPlot import GeometryPlot
from magnumapi.geometry.blocks.RectangularBlock import RectangularBlock
from magnumapi.geometry.primitives.Line import Line
from magnumapi.geometry.primitives.Area import Area
from magnumapi.geometry.definitions.LayerDefinition import LayerDefinition, SlottedLayerDefinition
from magnumapi.geometry.definitions.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.geometry.definitions.AbsoluteCosThetaBlockDefinition import AbsoluteCosThetaBlockDefinition
from magnumapi.geometry.blocks.Block import Block
from magnumapi.geometry.blocks.CosThetaBlock import RelativeCosThetaBlock, HomogenizedCosThetaBlock, CosThetaBlock, \
    AbsoluteCosThetaBlock

print('Analysis executed on %s' % str(datetime.datetime.now()).split('.')[0])
print('Loaded MagNum API version %s' % magnumapi.__version__)


class Geometry(ABC):
    """ Abstract geometry class providing a skeleton for all geometry types (CosTheta, Rectangular, etc.).

    """

    def __init__(self,
                 blocks: List[Union[AbsoluteCosThetaBlock, RectangularBlock,
                                    HomogenizedCosThetaBlock, RelativeCosThetaBlock]],
                 layer_defs: List[Union[LayerDefinition, SlottedLayerDefinition]]
                 ) -> None:
        """ Constructor of a Geometry class

        :param blocks: a list of instances of Block class implementations (e.g., RectangularBlock, CosThetaBlock, etc.)
        :param layer_defs: a list of layer definitions indicating symmetry type,
        and a list of blocks belonging to a layer
        """
        _check_input_consistency(blocks, layer_defs)
        self.blocks = blocks
        self.layer_defs = layer_defs

    def compute_surface(self):
        """ Method computing surface of a geometry as sum of all block surfaces

        :return: a surface in mm^2
        """
        return sum([block.compute_surface() for block in self.blocks])

    def compute_surface_cu(self):
        """ Method computing copper surface of a block as S = ns * S_strand_cu,
        where S_strand_cu = f_cu * pi * d_strand^2 / 4

        :return: a copper surface of a block in mm^2
        """
        return sum([block.compute_surface_cu() for block in self.blocks])

    def compute_surface_nocu(self):
        """ Method computing copper surface of a block as S = ns * S_strand_nocu,
        where S_strand_nocu = f_nocu * pi * d_strand^2 / 4

        :return: a non-copper surface of a block in mm^2
        """
        return sum([block.compute_surface_nocu() for block in self.blocks])

    def build_blocks(self) -> None:
        """ Method building all blocks for a given geometry definition

        """
        for block in self.blocks:
            block.build_block()

    def to_block_df(self) -> pd.DataFrame:
        """ Method concatenates row definition of each block into a ROXIE-compatible dataframe

        :return: a concatenated dataframe with ROXIE block definition for a geometry instance
        """
        return pd.concat([block.to_block_df() for block in self.blocks], axis=0).reset_index(drop=True)

    def to_layer_df(self) -> pd.DataFrame:
        return pd.DataFrame([layer_def.to_roxie_dict() for layer_def in self.layer_defs])

    def to_dict(self) -> dict:
        """ Method returning an absolute geometry definition (block definitions and layer definitions) as a dictionary.

        :return: a dictionary with two keys: block_defs and layer_defs
        """
        block_defs = []
        for layer_def in self.layer_defs:
            for block_index in layer_def.blocks:
                index_in_blocks = self.get_index_in_blocks_for_layer_block_index(block_index)
                block_defs.append(self.blocks[index_in_blocks].to_abs_dict())

        layer_defs = [layer_def.__dict__ for layer_def in self.layer_defs]

        return self.init_geometry_dict(block_defs, layer_defs)

    def init_geometry_dict(self, block_defs, layer_defs):
        return {'block_defs': block_defs, 'layer_defs': layer_defs}

    def to_df(self) -> pd.DataFrame:
        """ Method concatenating dataframes with area coordinates for each block

        :return: a concatenated dataframe with area coordinates
        """
        return pd.concat([block.to_df() for block in self.blocks], axis=0).reset_index(drop=True)

    def plot_blocks(self, figsize=(10, 10), is_grid=True, xlim=(0, 80), ylim=(0, 80)) -> None:
        GeometryPlot.plot_blocks(self, figsize, is_grid, xlim, ylim)

    def plotly_blocks(self, figsize=(750, 750), xlim=(0, 80), ylim=(0, 80)) -> None:
        GeometryPlot.plotly_geometry_blocks(self, figsize, xlim, ylim)

    def plot_bare_blocks(self, figsize=(15, 15), is_grid=True, xlim=(0, 80), ylim=(0, 80)) -> None:
        GeometryPlot.plot_bare_blocks(self, figsize, is_grid, xlim, ylim)

    def get_bare_areas_for_blocks(self) -> List[List[Area]]:
        """ Method returning a list of list of bare (uninsulated) areas constructed from iterating over all blocks in a
        geometry and all areas in a block.

        :return: a list of list of bare (uninsulated) areas
        """
        return [block.get_bare_areas() for block in self.blocks]

    def empty_block_areas(self):
        for block in self.blocks:
            block.empty_areas()

    def to_rel_geometry(self) -> "RelativeCosThetaGeometry":
        geometry = deepcopy(self)
        # check whether areas were initialize before geometry casting
        is_any_area_initialized = any([area for block in self.blocks for area in block.areas])

        if not all([isinstance(block, CosThetaBlock) for block in self.blocks]):
            raise TypeError('Only a geometry composed of CosThetaBlocks can be converted to a relative geometry.')

        geometry.build_blocks()

        blocks = []
        for layer_def in geometry.layer_defs:
            for index, block_index in enumerate(layer_def.blocks):
                index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(block_index)
                block = geometry.blocks[index_in_blocks]
                alpha_ref, phi_ref = retrieve_alpha_and_phi_ref(geometry, layer_def, index)
                block_def = RelativeCosThetaBlockDefinition(**block.to_rel_dict(alpha_ref=alpha_ref, phi_ref=phi_ref))
                blocks.append(RelativeCosThetaBlock(cable_def=block.cable_def,
                                                    insul_def=block.insul_def,
                                                    strand_def=block.strand_def,
                                                    conductor_def=block.conductor_def,
                                                    block_def=block_def))

        geometry_rel = self.init_geometry_instance(blocks, geometry)
        # Return to the external context of the geometry before entering
        Geometry.recover_context(is_any_area_initialized, geometry_rel)
        return geometry_rel

    def init_geometry_instance(self, blocks, geometry):
        return RelativeCosThetaGeometry(blocks=blocks, layer_defs=geometry.layer_defs)

    def homogenize(self) -> "HomogenizedCosThetaGeometry":
        """ Class method creating a homogenized cos-theta geometry from a cos-theta geometry.
        The method assumes that all blocks are CosThetaBlock type

        :param geometry: an input cos-theta geometry
        :return: a HomogenizedCosThetaGeometry instance
        """
        if not all([isinstance(block, CosThetaBlock) for block in self.blocks]):
            raise TypeError('Only a geometry composed of CosThetaBlocks can be converted to a homogenized geometry.')

        blocks = []
        for layer_index, layer_def in enumerate(self.layer_defs):
            for block_index in layer_def.blocks:
                index_in_blocks = self.get_index_in_blocks_for_layer_block_index(block_index)
                block = self.blocks[index_in_blocks]
                homo_cos_theta_block = block.homogenize()
                blocks.append(homo_cos_theta_block)

        return self.init_homogenized_geometry(blocks, self.layer_defs)

    def init_homogenized_geometry(self, blocks, layer_defs):
        return HomogenizedCosThetaGeometry(blocks, layer_defs)

    def get_index_in_blocks_for_layer_block_index(self, block_index: int) -> int:
        # The indexing of blocks does not have to be incremented from block to block
        # - also in a layer the block indexing is not given
        for index, block in enumerate(self.blocks):
            if block.block_def.no == block_index:
                return index

        raise IndexError('Block index from layer %d does not appear in block definitions' % block_index)

    @staticmethod
    def recover_context(is_any_area_initialized, geometry_rel):
        if is_any_area_initialized:
            geometry_rel.build_blocks()
        else:
            geometry_rel.empty_block_areas()

    def to_abs_geometry(self) -> "Geometry":
        return deepcopy(self)

    def get_number_of_layers(self) -> int:
        """ Method returning the number of layers in a cos-theta coil

        :return: number of layers
        """
        return len(self.layer_defs)

    def get_number_of_blocks_per_layer(self) -> List[int]:
        """ Method returning the number of blocks per layer in a cos-theta coil

        :return: list with number of blocks per layer
        """
        return [len(layer_def.blocks) for layer_def in self.layer_defs]


def _check_input_consistency(blocks: List[Block], layer_defs: List[LayerDefinition]) -> None:
    block_nos = [block.block_def.no for block in blocks]
    # are there any duplications in block numbers
    if len(block_nos) != len(set(block_nos)):
        raise AttributeError('The block numbering ({}) contains duplications!'.format(block_nos))

    # are there any duplications in layer numbers
    layer_nos = [layer_def.no for layer_def in layer_defs]
    if len(layer_nos) != len(set(layer_nos)):
        raise AttributeError('The layer numbering ({}) contains duplications!'.format(layer_nos))

    # are there any duplications in layer block numbers
    layer_blocks = list(chain.from_iterable([layer_def.blocks for layer_def in layer_defs]))
    if len(layer_blocks) != len(set(layer_blocks)):
        raise AttributeError('The layer numbering of blocks ({}) contains duplications!'.format(layer_blocks))

    # are the block nos matching the layer block numbers
    if set(block_nos) != set(layer_blocks):
        raise AttributeError('The numbering in block {} and layer {} do not match!'.format(block_nos, layer_blocks))


def retrieve_alpha_and_phi_ref(geometry, layer_def, index):
    if index == 0:
        return 0.0, 0.0
    else:
        index_prev_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(layer_def.blocks[index - 1])
        block_prev = geometry.blocks[index_prev_in_blocks]
        area_prev = block_prev.areas[-1]
        radius = block_prev.get_radius()
        phi_ref = Line.calculate_positioning_angle(area_prev.get_line(2), radius)
        alpha_ref = Line.calculate_relative_alpha_angle(area_prev.get_line(2))
        return alpha_ref, phi_ref


class RelativeCosThetaGeometry(Geometry):
    """RelativeCosThetaGeometry class for relative cos-theta geometry. Needed to implement the relative creation of
    cos-theta blocks.

    """

    def __init__(self, blocks: List[RelativeCosThetaBlock], layer_defs: List[LayerDefinition]) -> None:
        """Constructor of RelativeCosThetaGeometry class

        :param blocks: list of RelativeCosThetaBlock definitions
        :param layer_defs: a list of layer definitions
        """
        super().__init__(blocks, layer_defs)
        self.blocks = blocks  # Superfluous assignment to fix attribute warnings of mypy

    def build_blocks(self):
        for layer_index, layer_def in enumerate(self.layer_defs):
            for index, block_index in enumerate(layer_def.blocks):
                index_in_blocks = self.get_index_in_blocks_for_layer_block_index(block_index)
                block = self.blocks[index_in_blocks]
                alpha_ref, phi_ref = retrieve_alpha_and_phi_ref(self, layer_def, index)
                block.build_block(phi_ref=phi_ref, alpha_ref=alpha_ref)

    def to_abs_geometry(self) -> "Geometry":
        geometry = deepcopy(self)
        # check whether areas were initialize before geometry casting
        is_any_area_initialized = any([area for block in self.blocks for area in block.areas])

        geometry.build_blocks()

        blocks = []
        for block in geometry.blocks:
            abs_block_def = AbsoluteCosThetaBlockDefinition(**block.to_abs_dict())
            abs_block = AbsoluteCosThetaBlock(cable_def=block.cable_def,
                                              insul_def=block.insul_def,
                                              strand_def=block.strand_def,
                                              conductor_def=block.conductor_def,
                                              block_def=abs_block_def)
            blocks.append(abs_block)

        geometry_abs = self.init_geometry_instance(blocks, geometry.layer_defs)
        # Return to the external context of the geometry before entering
        Geometry.recover_context(is_any_area_initialized, geometry_abs)
        return geometry_abs

    def init_geometry_instance(self, blocks, layer_defs):
        return Geometry(blocks=blocks, layer_defs=self.layer_defs)

    def to_rel_geometry(self) -> "RelativeCosThetaGeometry":
        return deepcopy(self)

    def to_dict(self) -> dict:
        """ Method returning a relative geometry definition (block definitions and layer definitions) as a dictionary.

        :return: a dictionary with two keys: block_defs and layer_defs
        """
        block_defs = []
        for layer_def in self.layer_defs:
            for block_index in layer_def.blocks:
                index_in_blocks = self.get_index_in_blocks_for_layer_block_index(block_index)
                block_defs.append(self.blocks[index_in_blocks].to_rel_dict())

        layer_defs = [layer_def.__dict__ for layer_def in self.layer_defs]

        return self.init_geometry_dict(block_defs, layer_defs)

    def init_geometry_dict(self, block_defs, layer_defs):
        return {'block_defs': block_defs, 'layer_defs': layer_defs}


class HomogenizedCosThetaGeometry(Geometry):
    """HomogenizedCosThetaGeometry class for homogenized cos-theta geometry. Creates a homogenized geometry from both
    relative and absolute cos-theta geometry definition. Used for creation of ANSYS models.

    """

    def __init__(self, blocks: List[HomogenizedCosThetaBlock], layer_defs: List[LayerDefinition]) -> None:
        """Constructor of HomogenizedCosThetaGeometry class

        :param blocks: list of HomogenizedCosThetaBlock blocks
        :param layer_defs: a list of layer definitions
        """
        super().__init__(blocks, layer_defs)
        self.blocks = blocks  # Superfluous assignment to fix attribute warnings of mypy

    def to_block_df(self):
        raise NotImplementedError('This method is not implemented for this class')

    def plotly_blocks(self, figsize=(750, 750), xlim=(0, 80), ylim=(0, 80)):
        GeometryPlot.plotly_homogenized_geometry_blocks(self, figsize, xlim, ylim)
