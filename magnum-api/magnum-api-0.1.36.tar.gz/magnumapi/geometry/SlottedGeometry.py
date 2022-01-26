import math
from typing import List, Union

from magnumapi.geometry.Geometry import Geometry, RelativeCosThetaGeometry, HomogenizedCosThetaGeometry
from magnumapi.geometry.blocks.CosThetaBlock import RelativeCosThetaBlock, AbsoluteCosThetaBlock, \
    HomogenizedCosThetaBlock
from magnumapi.geometry.definitions.LayerDefinition import SlottedLayerDefinition


class SlottedGeometry(Geometry):

    def __init__(self,
                 blocks: List[Union[AbsoluteCosThetaBlock, RelativeCosThetaBlock]],
                 layer_defs: List[SlottedLayerDefinition],
                 r_aperture: float) -> None:
        """ Constructor of a SlottedGeometry class

        :param blocks: a list of instances of Block class implementations (e.g., RectangularBlock, CosThetaBlock, etc.)
        :param layer_defs: a list of layer definitions indicating symmetry type,
        and a list of blocks belonging to a layer
        :param r_aperture: aperture radius in mm
        """
        super().__init__(blocks, layer_defs)
        self.r_aperture = r_aperture

        calculate_layer_radii(self)
        calculate_positioning_angle_for_first_block_of_each_layer(self)

    def init_geometry_instance(self, blocks, geometry):
        return SlottedRelativeCosThetaGeometry(r_aperture=self.r_aperture,
                                               blocks=blocks,
                                               layer_defs=geometry.layer_defs)

    def init_geometry_dict(self, block_defs, layer_defs):
        return {'r_aperture': self.r_aperture, 'block_defs': block_defs, 'layer_defs': layer_defs}

    def init_homogenized_geometry(self, blocks, layer_defs):
        return SlottedHomogenizedCosThetaGeometry(blocks, layer_defs, self.r_aperture)


def calculate_layer_radii(geometry):
    # for each layer definition, for each block update the radius
    for layer_index, layer_def in enumerate(geometry.layer_defs):
        for block_index in layer_def.blocks:
            index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(block_index)
            block = geometry.blocks[index_in_blocks]
            if layer_index == 0:
                r_ref = geometry.r_aperture
            else:
                block_index_prev = geometry.layer_defs[layer_index - 1].blocks[0]
                index_prev_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(block_index_prev)
                r_prev = geometry.blocks[index_prev_in_blocks].block_def.radius
                width_prev = geometry.blocks[index_prev_in_blocks].cable_def.width
                ins_width_prev = geometry.blocks[index_prev_in_blocks].insul_def.width
                r_ref = r_prev + width_prev + 2 * ins_width_prev
            block.block_def.radius = r_ref + layer_def.spar_thickness


def calculate_positioning_angle_for_first_block_of_each_layer(geometry):
    # for each layer definition, for first block update the positioning angle
    for layer_def in geometry.layer_defs:
        first_block_index = layer_def.blocks[0]
        index_in_blocks = geometry.get_index_in_blocks_for_layer_block_index(first_block_index)
        block = geometry.blocks[index_in_blocks]

        phi_rad = math.asin(layer_def.midplane_wedge_thickness / block.block_def.radius)
        phi_deg = math.degrees(phi_rad)
        if hasattr(block.block_def, 'phi'):
            setattr(block.block_def, 'phi', phi_deg)
        elif hasattr(block.block_def, 'phi_r'):
            setattr(block.block_def, 'phi_r', phi_deg)
        else:
            raise AttributeError('Block definition {} does not contain neither phi nor phi_r parameter'
                                 .format(block.block_def))


class SlottedRelativeCosThetaGeometry(RelativeCosThetaGeometry):

    def __init__(self,
                 blocks: List[RelativeCosThetaBlock],
                 layer_defs: List[SlottedLayerDefinition],
                 r_aperture: float) -> None:
        """ Constructor of a Geometry class

        :param blocks: a list of instances of Block class implementations (e.g., RectangularBlock, CosThetaBlock, etc.)
        :param layer_defs: a list of layer definitions indicating symmetry type,
        and a list of blocks belonging to a layer
        :param r_aperture: aperture radius in mm
        """
        super().__init__(blocks, layer_defs)
        self.r_aperture = r_aperture
        calculate_layer_radii(self)
        calculate_positioning_angle_for_first_block_of_each_layer(self)

    def init_geometry_instance(self, blocks, layer_defs):
        return SlottedGeometry(r_aperture=self.r_aperture, blocks=blocks, layer_defs=layer_defs)

    def init_geometry_dict(self, block_defs, layer_defs):
        return {'r_aperture': self.r_aperture, 'block_defs': block_defs, 'layer_defs': layer_defs}

    def init_homogenized_geometry(self, blocks, layer_defs):
        return SlottedHomogenizedCosThetaGeometry(blocks, layer_defs, self.r_aperture)


class SlottedHomogenizedCosThetaGeometry(HomogenizedCosThetaGeometry):
    """SlottedHomogenizedCosThetaGeometry class for slotted, homogenized cos-theta geometry. Creates a slotted,
    homogenized geometry from both relative and absolute cos-theta geometry definition.
    Used for creation of ANSYS models.
    """

    def __init__(self,
                 blocks: List[HomogenizedCosThetaBlock],
                 layer_defs: List[SlottedLayerDefinition],
                 r_aperture: float) -> None:
        """Constructor of HomogenizedCosThetaGeometry class
    
        :param blocks: list of HomogenizedCosThetaBlock blocks
        :param layer_defs: a list of layer definitions
        """
        super().__init__(blocks, layer_defs)
        self.r_aperture = r_aperture
        self.blocks = blocks  # Superfluous assignment to fix attribute warnings of mypy

    def to_block_df(self):
        raise NotImplementedError('This method is not implemented for this class')
