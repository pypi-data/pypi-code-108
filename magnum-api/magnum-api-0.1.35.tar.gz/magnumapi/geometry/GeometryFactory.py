from typing import List, Dict, Type

import pandas as pd

from magnumapi.geometry.GeometryBuilder import GeometryBuilder, SlottedGeometryBuilder
from magnumapi.geometry.SlottedGeometry import SlottedGeometry, SlottedRelativeCosThetaGeometry
from magnumapi.geometry.blocks.CosThetaBlock import AbsoluteCosThetaBlock, RelativeCosThetaBlock
from magnumapi.geometry.Geometry import Geometry, RelativeCosThetaGeometry
from magnumapi.geometry.blocks.RectangularBlock import RectangularBlock
from magnumapi.geometry.definitions.LayerDefinition import LayerDefinition, SlottedLayerDefinition
from magnumapi.geometry.definitions.AbsoluteCosThetaBlockDefinition import AbsoluteCosThetaBlockDefinition
from magnumapi.geometry.definitions.RectangularBlockDefinition import RectangularBlockDefinition
from magnumapi.geometry.definitions.RelativeCosThetaBlockDefinition import RelativeCosThetaBlockDefinition
from magnumapi.cadata.CableDatabase import CableDatabase
import magnumapi.commons.json_file as json_file
import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI


class GeometryFactory:
    """ GeometryFactory implements a factory design pattern and is used to produce:
    - rectangular geometry
    - absolute cos-theta geometry
    - relative cos-theta geometry
    - slotted absolute cos-theta geometry
    - slotted relative cos-theta geometry

    """

    @classmethod
    def init_with_json(cls, json_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a JSON file.

        :param json_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        json_content = json_file.read(json_file_path)
        block_dct_defs = json_content['block_defs']
        layer_dct_defs = json_content['layer_defs']
        return cls.init_with_dict(block_dct_defs, layer_dct_defs, cadata)

    @classmethod
    def init_with_dict(cls,
                       block_dct_defs: List[Dict],
                       layer_dct_defs: List[Dict],
                       cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a list of dictionaries with block definition.

        :param block_dct_defs: a list of dictionaries with geometry definition (block definition)
        :param layer_dct_defs: a list of dictionaries with layer definitions
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        return GeometryBuilder() \
            .with_block_defs(block_dct_defs, cadata) \
            .with_layer_defs(layer_dct_defs) \
            .build()

    @classmethod
    def init_slotted_with_json(cls, json_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a JSON file.

        :param json_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        json_content = json_file.read(json_file_path)
        block_dct_defs = json_content['block_defs']
        layer_dct_defs = json_content['layer_defs']
        r_aperture = json_content['r_aperture']
        return cls.init_slotted_with_dict(block_dct_defs, layer_dct_defs, cadata, r_aperture=r_aperture)

    @classmethod
    def init_slotted_with_dict(cls,
                               block_dct_defs: List[Dict],
                               layer_dct_defs: List[Dict],
                               cadata: CableDatabase,
                               r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a list of dictionaries with block definition.

        :param block_dct_defs: a list of dictionaries with geometry definition (block definition)
        :param layer_dct_defs: a list of dictionaries with layer definitions
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        return SlottedGeometryBuilder() \
            .with_block_defs(block_dct_defs, cadata) \
            .with_layer_defs(layer_dct_defs) \
            .with_r_aperture(r_aperture) \
            .build()

    @classmethod
    def init_with_data(cls, data_file_path: str, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a DATA ROXIE file.

        :param data_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        block_df = RoxieAPI.read_bottom_header_table(data_file_path, keyword='BLOCK')
        layer_df = RoxieAPI.read_nested_bottom_header_table(data_file_path, keyword='LAYER')
        return cls.init_with_df(block_df, layer_df, cadata)

    @classmethod
    def init_with_csv(cls,
                      block_csv_file_path: str,
                      layer_csv_file_path: str,
                      cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a CSV file.

        :param block_csv_file_path: a path to a csv file with block definitions
        :param layer_csv_file_path: a path to a csv file with layer definitions
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        block_df = pd.read_csv(block_csv_file_path, index_col=0)
        layer_df = pd.read_csv(layer_csv_file_path, index_col=0)
        return cls.init_with_df(block_df, layer_df, cadata)

    @classmethod
    def init_with_df(cls, block_df: pd.DataFrame, layer_df, cadata: CableDatabase) -> Geometry:
        """ Class method initializing a Geometry instance from a dataframe with block definition.

        :param block_df: a dataframe with geometry definition (block definition)
        :param cadata: a CableDatabase instance
        :return: initialized geometry instance
        """
        return GeometryBuilder() \
            .with_block_df(block_df, cadata) \
            .with_layer_df(layer_df) \
            .build()

    @classmethod
    def init_slotted_with_data(cls, data_file_path: str, cadata: CableDatabase, r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a DATA ROXIE file.

        :param data_file_path: a path to a json file
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        block_df = RoxieAPI.read_bottom_header_table(data_file_path, keyword='BLOCK')
        layer_df = RoxieAPI.read_nested_bottom_header_table(data_file_path, keyword='LAYER')
        return cls.init_slotted_with_df(block_df, layer_df, cadata, r_aperture)

    @classmethod
    def init_with_csv_slotted(cls,
                      block_csv_file_path: str,
                      layer_csv_file_path: str,
                      cadata: CableDatabase,
                      r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a CSV file.

        :param block_csv_file_path: a path to a csv file with block definitions
        :param layer_csv_file_path: a path to a csv file with layer definitions
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        block_df = pd.read_csv(block_csv_file_path, index_col=0)
        layer_df = pd.read_csv(layer_csv_file_path, index_col=0)
        return cls.init_slotted_with_df(block_df, layer_df, cadata, r_aperture)

    @classmethod
    def init_slotted_with_df(cls,
                             block_df: pd.DataFrame,
                             layer_df: pd.DataFrame,
                             cadata: CableDatabase,
                             r_aperture: float) -> Geometry:
        """ Class method initializing a Geometry instance from a dataframe with block definition.

        :param block_df: a dataframe with geometry definition (block definition)
        :param cadata: a CableDatabase instance
        :param r_aperture: aperture radius in mm
        :return: initialized geometry instance
        """
        return SlottedGeometryBuilder() \
            .with_block_df(block_df, cadata) \
            .with_layer_df(layer_df) \
            .with_r_aperture(r_aperture) \
            .build()
