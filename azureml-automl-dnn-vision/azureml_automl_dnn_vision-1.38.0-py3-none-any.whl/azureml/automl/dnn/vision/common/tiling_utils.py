# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper utiities for image tiling."""

import torch
from typing import Any, cast, List, Optional, Tuple

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException, AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.tiling_dataset_element import Tile

logger = get_logger(__name__)


def validate_tiling_settings(tile_grid_size: Optional[Tuple[int, int]], tile_overlap_ratio: Optional[float]) -> None:
    """ Validate tiling settings.

    :param tile_grid_size: Tuple indicating number of tiles along width and height dimensions.
    :type tile_grid_size: Tuple[int, int]
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
    :type tile_overlap_ratio: float
    """
    if tile_grid_size is None:
        return

    if len(tile_grid_size) != 2:
        raise AutoMLVisionValidationException(
            "tile_grid_size is of size {}, should be of size 2. Cannot use tiling"
            .format(len(tile_grid_size)), has_pii=False)

    if not isinstance(tile_grid_size[0], int) or not isinstance(tile_grid_size[1], int):
        raise AutoMLVisionValidationException(
            "tile_grid_size {} has non-integer values. Cannot use tiling".format(tile_grid_size), has_pii=False)

    if tile_grid_size[0] <= 0 or tile_grid_size[1] <= 0:
        raise AutoMLVisionValidationException(
            "Invalid tile_grid_size {}. Values should be positive integers. Cannot use tiling"
            .format(tile_grid_size), has_pii=False)

    if tile_grid_size[0] == 1 and tile_grid_size[1] == 1:
        raise AutoMLVisionValidationException(
            "Invalid tile_grid_size {}. At least one of dimensions should have value greater than 1."
            "Cannot use tiling".format(tile_grid_size), has_pii=False)

    if not isinstance(tile_overlap_ratio, float):
        raise AutoMLVisionValidationException(
            "Invalid tile_overlap_ratio {}. It should be a float value. "
            "Cannot use tiling".format(tile_overlap_ratio), has_pii=False)

    if tile_overlap_ratio < 0.0 or tile_overlap_ratio >= 1.0:
        raise AutoMLVisionValidationException(
            "Invalid tile_overlap_ratio {}. Value should be >= 0 and < 1. Cannot use tiling."
            .format(tile_overlap_ratio), has_pii=False)


def get_tiles(tile_grid_size: Tuple[int, int], tile_overlap_ratio: float, image_size: Tuple[int, int]) -> Any:
    """Get tiles when image is split using tile_grid_size.

    :param tile_grid_size: Grid size indicating total number of tiles the image is split into along each axis.
    :type tile_grid_size: Tuple[int, int]
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
    :type tile_overlap_ratio: float
    :param image_size: Tuple indicating width and height of the image.
    :type image_size: Tuple[int, int]
    :return: List of tiles.
    :rtype: List[Tile]
    """
    tile_width = image_size[0] / (tile_overlap_ratio + (1 - tile_overlap_ratio) * tile_grid_size[0])
    tile_height = image_size[1] / (tile_overlap_ratio + (1 - tile_overlap_ratio) * tile_grid_size[1])

    # Tiles start at 0.0 and in increments of (1- tile_overlap_ratio) * tile_width
    tile_top_x_list = torch.arange(0.0, image_size[0], (1 - tile_overlap_ratio) * tile_width,
                                   device="cpu")[:tile_grid_size[0]]
    tile_top_y_list = torch.arange(0.0, image_size[1], (1 - tile_overlap_ratio) * tile_height,
                                   device="cpu")[:tile_grid_size[1]]
    tile_top_list = torch.cartesian_prod(tile_top_x_list, tile_top_y_list)
    tile_bottom_list = tile_top_list.add(torch.tensor([tile_width, tile_height], device="cpu").view(1, 2))
    tiles = torch.cat((tile_top_list, tile_bottom_list), dim=1)
    # Round the pixel co-ordinates
    tiles.round_()

    return [Tile(cast(Tuple[float, float, float, float], tuple(tile.tolist()))) for tile in tiles]
