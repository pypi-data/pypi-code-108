# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class to process the images in a dataset with tiling."""

import time
from typing import Any, cast, Optional, Tuple

from azureml.automl.dnn.vision.common.logging_utils import get_logger

logger = get_logger(__name__)


class Tile:
    """Class representing an image tile."""

    def __init__(self, coordinates: Tuple[float, float, float, float]) -> None:
        """
        :param coordinates: Tile pixel co-ordinates in (left, top, right, bottom) format.
        :type coordinates: Tuple[float, float, float, float]
        """
        self._x0 = coordinates[0]
        self._y0 = coordinates[1]
        self._x1 = coordinates[2]
        self._y1 = coordinates[3]

    def as_tuple(self) -> Tuple[float, float, float, float]:
        """Get tile in tuple format.

        :return: Tile as a tuple
        :rtype: Tuple[float, float, float, float]
        """
        return (self._x0, self._y0, self._x1, self._y1)

    @property
    def top_left_x(self) -> float:
        """Get top left x in pixel co-ordinates.

        :return: x coordinate of top left corner
        :rtype: float
        """
        return self._x0

    @property
    def top_left_y(self) -> float:
        """Get top left y in pixel co-ordinates.

        :return: y coordinate of top left corner
        :rtype: float
        """
        return self._y0

    @property
    def bottom_right_x(self) -> float:
        """Get bottom right x in pixel co-ordinates.

        :return: x coordinate of bottom right corner
        :rtype: float
        """
        return self._x1

    @property
    def bottom_right_y(self) -> float:
        """Get bottom right y in pixel co-ordinates.

        :return: y coordinate of bottom right corner
        :rtype: float
        """
        return self._y1

    def __hash__(self) -> int:
        """Define hash function so that class objects can be used as keys in a dictionary.

        :return: Hash of the object.
        :rtype: int
        """
        return hash(self.as_tuple())

    def __eq__(self, other: Any) -> bool:
        """Define eq function so that class objects can be used as keys in a dictionary.

        :param other: Other tile to compare.
        :type other: Tile
        :return: Comparison result.
        :rtype: bool
        """
        if other is None:
            return False

        return cast(bool, self.as_tuple() == other.as_tuple())

    def __lt__(self, other: Any) -> bool:
        """Define lt function so that class objects can be used with sort functions.

        :param other: Other tile to compare.
        :type other: Tile
        :return: Comparison result
        :rtype: bool
        """
        return cast(bool, self.as_tuple() < other.as_tuple())


class TilingDatasetElement:
    """Class representing dataset elements for tiling. These can be either an entire image or image tile,
    that is input to the model in training/validation."""

    def __init__(self, image_url: str, tile: Optional[Tile]) -> None:
        """
        :param image_url: Url of the image.
        :type image_url: str
        :param tile: Tile if a tile within an image should be processed, None otherwise.
        :type tile: Optional[Tile]
        """
        self._image_url = image_url
        self._tile = tile

    def __hash__(self) -> int:
        """Define hash function so that class objects can be used as keys in a dictionary.

        :return: Hash of the object.
        :rtype: int
        """
        return hash((self.image_url, self.tile))

    def __eq__(self, other: Any) -> bool:
        """Define eq function so that class objects can be used as keys in a dictionary.

        :param other: Other tiling dataset element to compare.
        :type other: TilingDatasetElement
        :return: Comparison result.
        :rtype: bool
        """
        return (self.image_url, self.tile) == (other.image_url, other.tile)

    def __lt__(self, other: Any) -> bool:
        """Define lt function so that class objects can be used with sort functions.

        :param other: Other tiling dataset element to compare.
        :type other: TilingDatasetElement
        :return: Comparison result
        :rtype: bool
        """
        if self.image_url < other.image_url:
            return True
        elif self.image_url == other.image_url:
            if self.tile is None and other.tile is None:
                return False
            elif self.tile is None and other.tile is not None:
                # When tile is None, entire image is processed. Treating entire image as the lesser entity
                return True
            elif self.tile is not None and other.tile is None:
                return False
            else:
                return cast(bool, self.tile < other.tile)

        return False

    @property
    def image_url(self) -> str:
        """Get the image url

        :return: Image Url
        :rtype: str
        """
        return self._image_url

    @property
    def tile(self) -> Optional[Tile]:
        """Get tile info.

        :return: Tile or None
        :rtype: Optional[Tile]
        """
        return self._tile
