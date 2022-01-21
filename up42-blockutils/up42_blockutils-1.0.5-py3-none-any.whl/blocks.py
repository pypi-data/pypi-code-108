"""
Base classes for building data and processing blocks. Includes basic functionality
including [exception handling](exceptions.md).

Example:
    ```python
    class AProcessingBlock(ProcessingBlock):
        def __init__(self, a_var):
            super().__init__()
            self.a_var = a_var

        def process(
            self, input_fc: FeatureCollection, process_dir: Path = Path("/tmp")
        ):
            self.a_var = 2
            return input_fc
    ```
    This class takes the input feature collection and return the same feature
    collection unchanged. The entrypoint would always be the `run` method.
"""

from abc import ABC, abstractmethod
from geojson import FeatureCollection, Feature

from .common import (
    load_query,
    load_params,
    load_metadata,
    save_metadata,
    ensure_data_directories_exist,
    BlockModes,
    get_block_mode,
)
from .exceptions import catch_exceptions

from .geometry import check_validity
from .stac import STACQuery


class DataBlock(ABC):
    """
    Base class for data blocks.
    """

    @abstractmethod
    def fetch(self, query: STACQuery, dry_run: bool = False) -> FeatureCollection:
        """
        Main worker method, for the given STAC query, fetch the results and save
        to output.

        Important:
            This method is an [abstract method](https://docs.python.org/3/library/abc.html)
            which means you are required to implement it in any inherited class.
        """
        raise NotImplementedError

    @classmethod
    @catch_exceptions()
    def run(cls, **kwargs):
        """
        This method is the main entry point for the data block.

        Allows for arbitrary kwargs that will be passed directy to the
        data block instance.

        Example:
            ```python3
            a_data_block.run(an_argument=15)
            ```
        """
        ensure_data_directories_exist()
        query: STACQuery = load_query()
        # check for geometry validity
        if query.bbox or query.intersects or query.contains:
            check_validity(query_geom=query.geometry())
        dry_run: bool = get_block_mode() == BlockModes.DRY_RUN.value
        result: FeatureCollection = cls(**kwargs).fetch(query=query, dry_run=dry_run)
        save_metadata(result)


class ProcessingBlock(ABC):
    """
    Base class for processing blocks.
    """

    @abstractmethod
    def process(self, input_fc: FeatureCollection) -> FeatureCollection:
        """
        Main worker method, for each input feature, process it and save to output.

        Important:
            This method is an [abstract method](https://docs.python.org/3/library/abc.html)
            which means you are required to implement it in any inherited class.
        """
        raise NotImplementedError

    @staticmethod
    def get_metadata(feature: Feature) -> dict:
        """
        Extracts metadata elements that need to be propagated to the output tif.
        """
        prop_dict = feature["properties"]
        meta_dict = {
            k: v
            for k, v in prop_dict.items()
            if not (k.startswith("up42.") or k.startswith("custom."))
        }
        return meta_dict

    @classmethod
    def from_dict(cls, kwargs):
        """
        Instantiate a class with a dictionary of parameters
        """
        return cls(**kwargs)

    @classmethod
    @catch_exceptions()
    def run(cls):
        """
        This method is the main entry point for the processing block.
        """
        ensure_data_directories_exist()
        params: dict = load_params()
        input_metadata: FeatureCollection = load_metadata()
        processing_block = cls.from_dict(params)
        result: FeatureCollection = processing_block.process(input_metadata)
        save_metadata(result)
