"""
Utilities for handling [SpatioTemporal Asset Catalog (STAC)](https://stacspec.org/) queries.
"""

from dataclasses import dataclass, field

import json
from decimal import Decimal
from typing import Union, Tuple, List, Iterable, Optional, Callable, Any

import shapely.geometry
import geojson

from geojson.geometry import Geometry
import ciso8601

from .logging import get_logger
from .exceptions import UP42Error, SupportedErrors

logger = get_logger(__name__)

Number = Union[int, Decimal, float]
Coordinates = Iterable[Number]
BoundingBox = Tuple[Number, Number, Number, Number]


@dataclass
class STACQuery:
    """
    Object representing a STAC query as used by data blocks. Standardized
    arguments are:

    Arguments:
        ids: Unique identifiers to search for.
        bbox: A bounding box type geometry.
        intersects: A geometry to use for searching with intersection operator.
        contains: A geometry to use for searching with contains operator.
        time: Time string in RFC3339 (for points in time) or RFC3339/RFC3339
            (for datetime ranges).
        limit: Maximum number of returned elements.
        time_series: List of time strings in RFC3339 (for points in time) or RFC3339/RFC3339
            (for datetime ranges).

    Additional arguments can be passed to the constructor.
    """

    ids: Optional[List[str]] = field(default=None)
    bbox: Optional[BoundingBox] = field(default=None)
    intersects: Optional[Geometry] = field(default=None)
    contains: Optional[Geometry] = field(default=None)
    time: Optional[str] = field(default=None)
    time_series: Optional[List[str]] = field(default=None)
    limit: Optional[int] = field(default=1)

    def __new__(cls, **kwargs):
        """
        Inspired by https://stackoverflow.com/a/63291704/14236301
        Adds attributes to the data class if they are passed in
        input dict in __init__, even if they are not explicitly defined as
        field attributes.
        """
        try:
            initializer = cls.__initializer
        except AttributeError:
            # Store the original init on the class in a different place
            cls.__initializer = initializer = cls.__init__
            # replace init with something harmless
            cls.__init__ = lambda *a, **k: None

        # code from adapted from Arne
        added_args = {}
        for name in list(kwargs.keys()):
            if name not in cls.__annotations__:
                added_args[name] = kwargs.pop(name)

        ret = object.__new__(cls)
        initializer(ret, **kwargs)
        # ... and add the new ones by hand
        for new_name, new_val in added_args.items():
            setattr(ret, new_name, new_val)

        return ret

    def __post_init__(self):
        """
        Post processes the passed arguments to make sure they are valid,
        i.e. only one of "bbox", "intersects" or "contains" is passed.
        """
        if (
            self.bbox
            and self.intersects
            or self.intersects
            and self.contains
            or self.contains
            and self.bbox
        ):
            raise UP42Error(
                SupportedErrors.WRONG_INPUT_ERROR,
                """Only one of the following query parameters is
                allowed at a query at any given time:
                * bbox
                * intersects
                * contains.""",
            )

        if self.time and self.time_series:
            raise UP42Error(
                SupportedErrors.WRONG_INPUT_ERROR,
                """Only one of the following query parameters is
                allowed at a query at any given time:
                * time
                * time_series
                """,
            )

        if not self.validate_datetime_str(self.time):
            raise UP42Error(
                SupportedErrors.WRONG_INPUT_ERROR,
                """Time string could not be validated.
                It must be one of the following formats:
                <RFC3339> (for points in time)
                <RFC3339>/<RFC3339> (for datetime ranges)""",
            )

        if self.limit is not None and self.limit < 1:
            logger.warning(
                "WARNING: limit parameter cannot be < 1, and has been automatically set to 1"
            )
            self.limit = 1

        if self.time_series is not None:
            for datestr in self.time_series:
                if not self.validate_datetime_str(datestr):
                    raise UP42Error(
                        SupportedErrors.WRONG_INPUT_ERROR,
                        """Time string from time_series could not be validated.
                        It must be one of the following formats:
                        <RFC3339> (for points in time)
                        <RFC3339>/<RFC3339> (for datetime ranges)""",
                    )

    def bounds(self) -> BoundingBox:
        """
        Get the bounding box of the query AOI(s) as a BoundingBox object.

        Returns:
            A bounding box object.
        """
        if self.bbox:
            return self.bbox
        elif self.intersects:
            return shapely.geometry.shape(self.intersects).bounds
        elif self.contains:
            return shapely.geometry.shape(self.contains).bounds
        else:
            raise UP42Error(
                SupportedErrors.WRONG_INPUT_ERROR,
                """STACQuery does not contain any of the following query parameters:
                * bbox
                * intersects
                * contains.""",
            )

    def geometry(self) -> Geometry:
        """
        Get the geometry of the query AOI(s) as a GeoJson Polygon object.

        Returns:
            A GeoJson Polygon object
        """
        if self.bbox:
            return json.loads(
                json.dumps(shapely.geometry.mapping(shapely.geometry.box(*self.bbox)))
            )
        elif self.intersects:
            return self.intersects
        elif self.contains:
            return self.contains
        else:
            raise UP42Error(
                SupportedErrors.WRONG_INPUT_ERROR,
                """STACQuery does not contain any of the following query parameters:
                * bbox
                * intersects
                * contains.""",
            )

    def get_param_if_exists(self, key: str, default_value: Any = None) -> Any:
        """
        Get a query parameter if exists in he STAC query object. Returns
        default_value if not in the query.

        Arguments:
            key: An identifier of the parameter
            default_value: The default return value if the parameter does not exist.
        """
        return getattr(self, key, default_value)

    def set_param_if_not_exists(self, key: str, value: Any):
        """
        Set a query parameter if it does not exist in the STAC query object.

        Arguments:
            key: An identifier of the parameter
            value: The parameter value to set.
        """
        if self.get_param_if_exists(key) is None:
            setattr(self, key, value)

    @classmethod
    def from_json(cls, json_data: str):
        """
        Get a STACQuery from a json string representation of a query.

        Arguments:
            json_data: String representation of the query.

        Returns:
            A STACQuery object/
        """
        return STACQuery.from_dict(json.loads(json_data))

    @classmethod
    def from_dict(
        cls, dict_data: dict, validator: Callable[[dict], bool] = lambda x: True
    ):
        """
        Get a STACQuery from a dict representation of a query.

        Arguments:
            dict_data: Dictionary representation of the query.
            validator: Function used to validate the query.

        Returns:
            A STACQuery object.
        """

        if not validator(dict_data):
            raise UP42Error(
                SupportedErrors.WRONG_INPUT_ERROR,
                """Input Query did not pass validation. Please refer
                to the official block documentation or block specification.""",
            )

        if ("intersects" or "contains") in dict_data:
            dict_data = cls.handle_z_coordinate(dict_data)

        return STACQuery(**dict_data)

    @staticmethod
    def validate_datetime_str(string: Optional[str]) -> bool:
        """
        Validate a datetime string.

        Arguments:
            string: A datetime string representation.

        Returns:
            If datetime string is valid.
        """
        try:
            if string is None:
                return True
            elif len(str(string).split("/")) == 2:
                ciso8601.parse_datetime(str(string).split("/", maxsplit=1)[0])
                ciso8601.parse_datetime(str(string).split("/")[1])
            else:
                ciso8601.parse_datetime(str(string))
        except ValueError:
            return False
        return True

    @staticmethod
    def handle_z_coordinate(query: dict):
        """
        Checks if a geometry of a qury has z coordinate or not. if they exist, they will be removed.
        Args:
            query: Dictionary representation of the query.

        Returns:
            A new dictionary without z coordinates (if they exist).

        """
        query_geom = query[("intersects" or "contains")]
        if query_geom:
            geom_drop_z = geojson.loads(
                geojson.dumps(
                    geojson.utils.map_tuples(lambda c: [c[0], c[1]], query_geom)
                )
            )

            query[("intersects" or "contains")] = geom_drop_z
        return query
