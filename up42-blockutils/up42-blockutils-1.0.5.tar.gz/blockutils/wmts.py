"""
Helper for downloading, processing and merging tiles from tile based data sources.
"""
import io
import uuid
import time
from pathlib import Path
from typing import List, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field

import concurrent.futures
import numpy as np
import rasterio
from rasterio import merge as riomerge
from rasterio.enums import ColorInterp
import mercantile
from mercantile import Tile
import requests


from .logging import get_logger
from .raster import to_cog, create_multiband_tif
from .exceptions import UP42Error, SupportedErrors

logger = get_logger(__name__)


class TileIsEmptyError(TypeError):
    pass


class TileNotFetchedError(TypeError):
    pass


@dataclass
class TileMergeHelperSettings:
    """
    This class wraps all defaultable attributes of the TileMergeHelper.
    """

    req_kwargs: dict = field(default_factory=dict)
    tile_size: int = field(default=256)
    crs: str = field(default="EPSG:4326")
    parallelize: bool = field(default=False)
    retries_for_no_fetched_tiles: int = field(default=3)
    max_threads: int = field(default=10)
    polling_cycle: int = field(default=5)


class TileMergeHelper(TileMergeHelperSettings):
    """
    This class is a helper class that allows to fetch tiles via a req function, process them via a process function
    (a custom process function can be called, or the default process function will be used) ,and finally merge them
    into a single image in COG format.
    """

    def __init__(
        self,
        tiles: List[Tile],
        req: Callable,
        process: Callable = None,
        **kwargs,
    ):
        self.tiles = tiles
        self.req = req
        self.process = process
        super().__init__(**kwargs)

    @staticmethod
    def _process(response: requests.Response, tile: Tile) -> Path:
        """
        This method is default method for processing a tile. It simply writes a tile which can be in
        different formats such as "png", "jpeg", or etc in the tif format to make sure all metadata and transform
        information are saved so that merging process can be performed.
        Args:
            response: response from API side after fetching a tile
            tile: A tuple of x,y,z information for the tile. For instance: Tile(x=41955, y=101467, z=18)
        """
        temp_tile_filename = Path(f"/tmp/output/{str(uuid.uuid4())}.tif")

        bands: list = []
        try:
            with rasterio.io.MemoryFile(io.BytesIO(response.content)) as mem_file:
                with mem_file.open() as image:
                    for i in range(image.count):
                        bands.append(image.read(i + 1))
                    tile_meta = image.meta
        except rasterio.errors.RasterioIOError as err:
            raise UP42Error(SupportedErrors.API_CONNECTION_ERROR, err) from err

        tile_transform = rasterio.transform.from_bounds(
            *mercantile.xy_bounds(tile),
            width=tile_meta.get("width"),
            height=tile_meta.get("height"),
        )

        tile_meta.update(driver="GTiff", crs="EPSG:3857", transform=tile_transform)
        if np.any(bands):
            with rasterio.open(temp_tile_filename, "w", **tile_meta) as output_tile:
                for idx, band in enumerate(bands):
                    output_tile.write(band, idx + 1)
        else:
            raise TileIsEmptyError

        return temp_tile_filename

    def tile_worker(
        self,
        tile: Tile,
        tile_tif_list: List[Path],
        valid_tiles: List[Tile],
        tiles_not_fetched: List[Tile],
    ):
        """
        This method fetches the tile from a specific url and applies processing on it.
        Final result should be a path to the tile written in tif format. If user did not specify a process
        method, the default _process method will called.
        Args:
            tile: A tuple of x,y,z information for the tile. For instance: Tile(x=41955, y=101467, z=18)
            tile_tif_list: List for saving the tiles that were fetched and stored in the tif format.
            valid_tiles: List of tiles that are NOT empty.
            tiles_not_fetched: List of tiles that were not fetched due to API issues.
        """
        try:
            response = self.req(tile, **self.req_kwargs)
            try:
                if self.process:
                    if "tile_size" in self.process.__code__.co_varnames:
                        tile_tif_list.append(
                            self.process(response, tile, tile_size=self.tile_size)
                        )
                    else:
                        tile_tif_list.append(self.process(response, tile))
                else:
                    tile_tif_list.append(self._process(response, tile))
                valid_tiles.append(tile)
            except TileIsEmptyError:
                logger.info(f"{tile} is emtpy, Skipping ...")
        except TileNotFetchedError:
            tiles_not_fetched.append(tile)

    def loop_over_tiles(self):
        """
        This method iterates over a list of tiles and applies tile_worker method to fetch and process them.
        In the case of not being able to fetch the tile (API issues) a retrying mechanism will happen to
        retry fetching those tiles again. Also for speeding up the fetching process a parallelization option
        has been implemented. Moreover, if a tile is empty, it will be skipped.
        Returns:
            tile_tif_list: List of path to tiles which are written in tif format.
            valid_tiles: List of tiles that are NOT empty.
        """
        tile_tif_list = []
        valid_tiles = []
        tiles_not_fetched = []

        active_tiles = self.tiles.copy()

        retry_round = 0
        while retry_round <= self.retries_for_no_fetched_tiles:
            # It initially starts with active_tiles, and among them, there are some tiles that are not fetched
            # which will be saved to tiles_not_fetched list. Then when retrying started, the tile in this list
            # will be assigned to active_tiles (active_tiles will be rewritten) to do the whole fetching process again.
            if retry_round:
                if tiles_not_fetched:
                    time.sleep(self.polling_cycle)
                    active_tiles = tiles_not_fetched.copy()
                    tiles_not_fetched = []
                    logger.info(
                        f"Now starting {retry_round}. round of retrying failures"
                    )
                    logger.info(f"{len(active_tiles)}. tiles will be retried")
                else:
                    break

            if not self.parallelize:
                for tile in active_tiles:
                    self.tile_worker(
                        tile, tile_tif_list, valid_tiles, tiles_not_fetched
                    )
            else:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.max_threads
                ) as executor:
                    future_list = []
                    for tile in active_tiles:
                        logger.info(f"Tile {tile} added to executor...")
                        future_list.append(
                            executor.submit(
                                lambda t: self.tile_worker(*t),
                                [tile, tile_tif_list, valid_tiles, tiles_not_fetched],
                            )
                        )
                    for future in concurrent.futures.as_completed(future_list):
                        try:
                            future.result()
                        except Exception as e:
                            raise e
            retry_round += 1

        logger.info(
            f"There are {len(valid_tiles)} valid data tiles out of {len(self.tiles)}"
        )
        if tiles_not_fetched:
            raise UP42Error(
                SupportedErrors.API_CONNECTION_ERROR,
                "Retrying was unsuccessful. API returned error code 500",  # TODO: Is this assumption from empty list?
            )
        return tile_tif_list, valid_tiles

    @contextmanager
    def tile_dataset(self):

        tile_tif_list, valid_tiles = self.loop_over_tiles()

        try:
            yield tile_tif_list, valid_tiles
        finally:
            for tile_tif in tile_tif_list:
                tile_tif.unlink()

    @staticmethod
    def merge_tiles(tile_file_list):
        """
        This method merges the list of tif files and returns the merged array,
        transform and meta for the final writing.
        Args:
            tile_file_list: List of path to tif files. For instance: ["/a/b/1234.tif", "/a/c/5678.tif"]
        """
        if not tile_file_list:
            raise UP42Error(SupportedErrors.NO_INPUT_ERROR, "All tiles are empty.")

        tile_file_list_str = [str(tif_file) for tif_file in tile_file_list]
        merged_array, merged_transform = riomerge.merge(tile_file_list_str)
        with rasterio.open(tile_file_list[0]) as src:
            temp_meta = src.meta.copy()

        return merged_array, merged_transform, temp_meta

    def write_merged_tiles(
        self,
        output_path,
        merged_array,
        merged_transform,
        meta,
        tile_size,
        apply_to_cog: bool = True,
    ):
        """
        This method writes the merged tiles in a file. The final result will be in COG format.
        Args:
            output_path: Path to save the final image.
            merged_array: Numpy array of merged tiles.
            merged_transform: Transform for merged tiles.
            meta: Metadata for writing the final image.
            tile_size: Size of the tile. In most cases 256.
            apply_to_cog: Whether convert a tif to cog tif. Default is true.

        """
        _merged_shape: List = list(merged_array.shape)
        if _merged_shape[1] > tile_size and _merged_shape[2] > tile_size:
            while _merged_shape[1] % tile_size != 0:
                # X dimension not divisible by tile_size
                _merged_shape[1] -= 1
                # Remove one pixel
            while _merged_shape[2] % tile_size != 0:
                # Y dimension not divisible by tile_size
                _merged_shape[2] -= 1
                # Remove one pixel

        merged_shape = tuple(_merged_shape)

        meta.update(
            {
                "driver": "GTiff",
                "height": merged_shape[1],
                "width": merged_shape[2],
                "transform": merged_transform,
                "crs": self.crs,
            }
        )
        with rasterio.open(output_path, "w", **meta) as output:
            output.write(merged_array[:, : merged_shape[1], : merged_shape[2]])

        if apply_to_cog:
            to_cog(output_path)

    def get_final_image(self, output_path: Path, return_cog: bool = True):
        """The main method which merges list of tiles and produces the final merged image."""
        with self.tile_dataset() as (tile_tif_list, valid_tiles):
            merged_array, merged_transform, meta = self.merge_tiles(tile_tif_list)

        self.write_merged_tiles(
            output_path,
            merged_array,
            merged_transform,
            meta,
            self.tile_size,
            return_cog,
        )
        return valid_tiles


class MultiTileMergeHelper:
    """
    This class is a helper class that allows to pass list of TileMergeHelper object. This is mostly relevant
    when the datasets has multiple layers (e.g. SENTINEL1GRD with two polarization). Via this object, each layer will
    be handled separately (fetching tiles, processing them, and merging them) with an additional final step which
    appends this layers to one tif file to a create a single multi-bands tif. Also, the end result will be in COG
    format.
    """

    def __init__(self, tilemergehelper_list: List[TileMergeHelper]):
        self.tilemergehelper_list = tilemergehelper_list

    def get_multiband_tif(
        self,
        filename_path: Path,
        band_descriptions: List[str] = None,
        drop_nodata: bool = False,
        colorinterp: List[ColorInterp] = None,
        return_cog=True,
    ):
        outputs_path = []
        valid_tiles = {}
        for i, tilemergehelper in enumerate(self.tilemergehelper_list):
            tmp = f"/tmp/output/{str(uuid.uuid4())}.tif"
            valid_tiles[i] = tilemergehelper.get_final_image(
                Path(tmp), return_cog=False
            )
            outputs_path.append(Path(tmp))

        if band_descriptions:
            for old_key, new_key in zip(list(valid_tiles.keys()), band_descriptions):
                valid_tiles[new_key] = valid_tiles.pop(old_key)

        create_multiband_tif(
            outputs_path,
            filename_path,
            band_descriptions,
            drop_nodata,
            colorinterp,
            return_cog=return_cog,
        )
        for tmp_path in outputs_path:
            tmp_path.unlink()

        return valid_tiles

    @classmethod
    def from_req_kwargs(
        cls,
        tiles: List[Tile],
        req: Callable,
        kwargs_list: List[dict],
        process: Callable = None,
    ):
        tilemergehelper_list = []
        for kwargs in kwargs_list:
            tilemergehelper_list.append(TileMergeHelper(tiles, req, process, **kwargs))

        return cls(tilemergehelper_list)
