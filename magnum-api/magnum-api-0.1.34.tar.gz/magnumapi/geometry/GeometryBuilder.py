import pandas as pd

from magnumapi.cadata.CableDatabase import CableDatabase
from magnumapi.geometry.blocks.RectangularBlock import RectangularBlock
from magnumapi.geometry.blocks.CosThetaBlock import AbsoluteCosThetaBlock, RelativeCosThetaBlock
from magnumapi.geometry.definitions.LayerDefinition import LayerDefinition, SlottedLayerDefinition
from magnumapi.geometry.definitions.RectangularBlockDefinition import RectangularBlockDefinition
from magnumapi.geometry.definitions.AbsoluteCosThetaBlockDefinition import AbsoluteCosThetaBlockDefinition
from magnumapi.geometry.definitions.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.geometry.Geometry import Geometry, RelativeCosThetaGeometry
from magnumapi.geometry.SlottedGeometry import SlottedGeometry, SlottedRelativeCosThetaGeometry


class GeometryBuilder():
    """ Class building a geometry object with block and layer definitions. It is capable of constructing:
    - relative cos-theta geometry
    - absolute cos-theta and rectangular geometry

    """

    def __init__(self) -> None:
        self.blocks = []
        self.layer_defs = []

    def with_block_defs(self, block_defs: list, cadata: CableDatabase) -> "GeometryBuilder":
        """ Method setting block definitions for a geometry builder instance

        :param block_defs: a list of dictionaries with block definitions: absolute and relative cos-theta, absolute
        rectangular
        :param cadata: cable database instance with suplementary cable definitoins
        :return: an updated GeometryBuilder instance
        """
        self.blocks = GeometryBuilder._initialize_blocks(block_defs, cadata)
        return self

    def with_block_df(self, block_df: pd.DataFrame, cadata: CableDatabase):
        """ Method setting block definitions for a geometry builder instance

        :param block_df: a dataframe with block definitions: absolute and relative cos-theta, absolute
        rectangular
        :param cadata: cable database instance with suplementary cable definitoins
        :return: an updated GeometryBuilder instance
        """
        lst_block_defs = [row.to_dict() for _, row in block_df.iterrows()]
        self.blocks = self._initialize_blocks(lst_block_defs, cadata)
        return self

    @classmethod
    def _initialize_blocks(cls, dct_block_defs: list, cadata: CableDatabase) -> list:
        """ Private method initializing a list of blocks from a list of block definitions

        :param block_defs: a list of dictionaries with block definitions: absolute and relative cos-theta, absolute
        rectangular
        :param cadata: cable database instance with suplementary cable definitoins
        :return: a list of initialized blocks
        """
        blocks = []
        for dct_block_def in dct_block_defs:
            if dct_block_def['type'] == 2:
                for key, value in RectangularBlock.roxie_to_magnum_dct.items():
                    dct_block_def[value] = dct_block_def.pop(key)

            BlockClass, BlockDefinitionClass = cls._get_block_and_block_definition_classes(dct_block_def)
            block_def = BlockDefinitionClass(**dct_block_def)
            block = BlockClass(block_def=block_def,
                               cable_def=cadata.get_cable_definition(block_def.condname),
                               insul_def=cadata.get_insul_definition(block_def.condname),
                               strand_def=cadata.get_strand_definition(block_def.condname),
                               conductor_def=cadata.get_conductor_definition(block_def.condname))

            blocks.append(block)
        return blocks

    @staticmethod
    def _get_block_and_block_definition_classes(block_def: dict):
        """ Private method returning a tuple of a block and block definition classes to initialize a block

        :param block_def: an input block definition dictionary
        :return: a tuple of block and block definition classes
        """
        block_def_set = set(block_def.keys())

        if block_def_set == set(RelativeCosThetaBlockDefinition.__dict__['__dataclass_fields__'].keys()):
            return RelativeCosThetaBlock, RelativeCosThetaBlockDefinition
        elif block_def_set == set(AbsoluteCosThetaBlockDefinition.__dict__['__dataclass_fields__'].keys()):
            return AbsoluteCosThetaBlock, AbsoluteCosThetaBlockDefinition
        elif block_def_set == set(RectangularBlockDefinition.__dict__['__dataclass_fields__'].keys()):
            return RectangularBlock, RectangularBlockDefinition

    def with_layer_defs(self, layer_defs: list) -> "GeometryBuilder":
        """ Method initializing layer definitions

        :param layer_defs: a list of dictionaries with layer definitions
        :return: an updated GeometryBuilder instance
        """
        self.layer_defs = self._initialize_layer_defs(layer_defs)
        return self

    def with_layer_df(self, layer_df: pd.DataFrame):
        """ Method initializing layer definitions

        :param layer_defs: a list of dictionaries with layer definitions
        :return: an updated GeometryBuilder instance
        """
        lst_layer_defs = [row.to_dict() for _, row in layer_df.iterrows()]
        self.layer_defs = self._initialize_layer_defs(lst_layer_defs)
        return self

    @classmethod
    def _initialize_layer_defs(cls, dct_layer_defs: list) -> list:
        """ Private method initialiying layer definitions

        :param dct_layer_defs: a list of dictionary layer definitions
        :return: a list of LayerDefinition objects
        """
        return [LayerDefinition(**dct_layer_def) for dct_layer_def in dct_layer_defs]

    def build(self) -> Geometry:
        """ Method building a Geometry class from initialized block and layer definitions

        :return: an intialized Geometry object (either Geometry for absolute cos-theta and rectangular or
        RelativeCosThetaGeometry for a relative cos-theta geometry)
        """
        params = {'blocks': self.blocks, 'layer_defs': self.layer_defs}

        GeometryClass = self._get_geometry_class()
        return GeometryClass(**params)

    def _get_geometry_class(self):
        """ Private method returning a geometry class suitable for blocks and layer definitions. The method performs
        consistency checks prior to returning a geometry object.

        :return: a Geometry class (either Geometry for absolute cos-theta and rectangular or
        RelativeCosThetaGeometry for a relative cos-theta geometry)
        """
        self._check_initialization_consistency()

        are_all_layers_regular = all([isinstance(layer_def, LayerDefinition) for layer_def in self.layer_defs])

        if not are_all_layers_regular:
            raise AttributeError('All layers definitions have to be LayerDefinition for Geometry object.')

        are_all_blocks_relative = all([isinstance(block, RelativeCosThetaBlock) for block in self.blocks])
        are_all_blocks_absolute = all([isinstance(block, (AbsoluteCosThetaBlock, RectangularBlock))
                                       for block in self.blocks])

        if are_all_blocks_relative:
            return RelativeCosThetaGeometry
        elif are_all_blocks_absolute:
            return Geometry
        else:
            raise AttributeError('Geometry definition contains errors:'
                                 '- blocks contain a mix of relative and absolute.')

    def _check_initialization_consistency(self) -> None:
        """ Method checking initialization consistency for a GeometryBuilder. To construct a geometr both blocks and
        layer definitions need to be initialized.

        """
        if not self.blocks:
            raise AttributeError('Blocks are not initialized! Please do so using with_block_defs method.')
        if not self.layer_defs:
            raise AttributeError('Layers are not initialized! Please do so using with_layer_defs method.')


class SlottedGeometryBuilder(GeometryBuilder):
    """ A builder class for SlottedGeometry, either absolute or relative cos-theta geometry.

    """

    def __init__(self) -> None:
        super().__init__()
        self.r_aperture = None

    def with_r_aperture(self, r_aperture: float) -> "GeometryBuilder":
        """ Method setting aperture radius for a GeometryBuilder

        :param r_aperture: aperture radius in mm
        :return: an updated GeometryBuilder instance
        """
        self.r_aperture = r_aperture
        return self

    @classmethod
    def _initialize_layer_defs(cls, dct_layer_defs: list) -> list:
        """ Private method initializing layer definitions for slotted geometry

        :param dct_layer_defs: a dictionary layer definition
        :return: a list of initialized SlottedLayerDefinition objects
        """
        return [SlottedLayerDefinition(**dct_layer_def) for dct_layer_def in dct_layer_defs]

    def build(self) -> Geometry:
        """ Method building a SlottedGeometry class from initialized block and layer definitions as well as aperture
        radius

        :return: an intialized SlottedGeometry object (either SlottedGeometry for absolute cos-theta or
        SlottedRelativeCosThetaGeometry for a relative cos-theta geometry)
        """
        params = {'blocks': self.blocks, 'layer_defs': self.layer_defs, 'r_aperture': self.r_aperture}

        GeometryClass = self._get_geometry_class()
        return GeometryClass(**params)

    def _get_geometry_class(self):
        """ Private method returning a geometry class suitable for blocks and layer definitions. The method performs
        consistency checks prior to returning a geometry object.

        :return: a SlottedGeometry class (either SlottedGeometry for absolute cos-theta or
        SlottedRelativeCosThetaGeometry for a relative cos-theta geometry)
        """
        self._check_initialization_consistency()
        if self.r_aperture is None:
            raise AttributeError('Radius has to be defined for SlottedGeometry object.')

        are_all_layers_slotted = all([isinstance(layer_def, SlottedLayerDefinition) for layer_def in self.layer_defs])

        if not are_all_layers_slotted:
            raise AttributeError('All layers definitions have to be SlottedLayerDefinition for SlottedGeometry object.')

        are_all_blocks_relative = all([isinstance(block, RelativeCosThetaBlock) for block in self.blocks])
        are_all_blocks_absolute_cos_theta = all([isinstance(block, AbsoluteCosThetaBlock) for block in self.blocks])

        if are_all_blocks_relative:
            return SlottedRelativeCosThetaGeometry
        elif are_all_blocks_absolute_cos_theta:
            return SlottedGeometry
        else:
            raise AttributeError('Slotted geometry definition contains errors:'
                                 '- blocks contain a mix of rectangular and/or relative/absolute cos-theta.')
