"""
Utilities for handling geometry operations.
"""
import copy
import math
from typing import Generator, List, Callable

import geojson
import mercantile
from mercantile import Tile
import numpy as np
import rasterio as rio
from area import area
from shapely.geometry import box, mapping, shape
from shapely.validation import explain_validity
from shapely.ops import unary_union

from .exceptions import SupportedErrors, UP42Error
from .logging import get_logger
from .stac import BoundingBox, STACQuery

logger = get_logger(__name__)


def filter_tiles_intersect_with_geometry(
    tiles: List[mercantile.Tile], geometry: geojson.geometry.Geometry
) -> Generator[mercantile.Tile, None, None]:
    """
    Given a list of WMTS tiles, this function filters out all tiles which
    don't intersect with the supplied geojson geometry.

    Arguments:
        tiles: List of tiles to filter from.
        geometry: Geometry to use for filtering.

    Returns:
        Tile generator with only tiles that intersect geometry.
    """
    geometry = shape(geometry)
    for tile in tiles:
        tile_bbox = box(*mercantile.bounds(tile)._asdict().values())
        if geometry.intersects(tile_bbox) and not geometry.touches(tile_bbox):
            yield tile


def intersect_geojson_polygons(
    geom1: geojson.geometry.Geometry, geom2: geojson.geometry.Geometry
) -> geojson.geometry.Geometry:
    """
    Convenience method for intersecting two geojson polygons.

    Arguments:
        geom1: A geometry.
        geom2: A different geometry to intersect with.

    Returns:
        Geometry of the intersection.
    """
    geometry1 = shape(geom1)
    geometry2 = shape(geom2)
    intersection = geometry1.intersection(geometry2)

    return mapping(intersection)


def get_query_bbox(query: STACQuery) -> BoundingBox:
    """
    From a STACQuery object return the bounding box of the query.

    Arguments:
        query: A STACQuery object.

    Returns:
        A bounding box object of the query.

    Important:
        If the geometry type is Point or a very small area, a very small buffer
        will be computed and the bounding box of the buffered geometry returned.
    """

    bbox: BoundingBox = query.bounds()

    poly = box(*bbox)
    if poly.area == 0.0:
        # If the geometry in the query was just a point (rather than a box),
        # then make a very small polygon around it so we can derive a
        # bounding box for the OABM API.
        bbox = poly.buffer(0.0001).bounds

    return bbox


def aoi_size_check(
    query: STACQuery,
    min_sqkm: float = None,
    max_sqkm: float = None,
    ignore_missing_geometry: bool = False,
) -> bool:
    """
    Checks if the query geometry is within set AOI size bounds.

    Arguments:
        query: A STACQuery object.
        min_sqkm: The minimum size in square kilometers.
        max_sqkm: The maximum size in square kilometers.
        ignore_missing_geometry: Return True even if the
            STACQuery object does not include a geometry.

    Returns:
        Is the query within AOI size bounds.

    Raises:
        UP42Error: If query has no geometry and
            ignore_missing_geometry is False (default).
    """
    valid = True
    try:
        geom = query.geometry()
        area_sqkm = area(geom) / (10 ** 6)

        if min_sqkm is not None:
            if area_sqkm < min_sqkm:
                valid = False

        if max_sqkm is not None:
            if area_sqkm > max_sqkm:
                valid = False
    except UP42Error:
        if not ignore_missing_geometry:
            raise

    return valid


# pylint: disable=chained-comparison
def get_utm_zone_epsg(lon: float, lat: float) -> int:
    """
    Calculates the suitable UTM crs epsg code for an input geometry point.

    Adapted from https://stackoverflow.com/a/55781862/6400555.

    Arguments:
        lon : Longitude of point in degrees (WGS84)
        lat : Latitude of point in degrees (WGS84)

    Returns:
        EPSG code of suitable UTM zone for given (lon, lat). i.e. 32658
    """
    zone_number = int((math.floor((lon + 180) / 6) % 60) + 1)

    # Special zones for Norway
    if lat >= 56.0 and lat < 64.0 and lon >= 3.0 and lon < 12.0:
        zone_number = 32
    # Special zones for Svalbard
    elif lat >= 72.0 and lat < 84.0:
        if lon >= 0.0 and lon < 9.0:
            zone_number = 31
        elif lon >= 9.0 and lon < 21.0:
            zone_number = 33
        elif lon >= 21.0 and lon < 33.0:
            zone_number = 35
        elif lon >= 33.0 and lon < 42.0:
            zone_number = 37

    if lat > 0:
        utm_code = zone_number + 32600
    else:
        utm_code = zone_number + 32700

    return utm_code


def count_vertices(geojson_geom: dict) -> int:
    """Method for counting number of vertices in any kind of geojson geometry\n
    Works for all geometry types:\n
    1. (Multi)Point\n
    2. (Multi)Linestring\n
    3. (Multi)Polygon\n

    Args:
        geojson_geom (dict): e.g. `{"type": "Polygon", "coordinates": [[...]]}`

    Returns:
        int: number of vertices in a geometry
    """
    total_vertices = 0

    coords = geojson_geom["coordinates"]
    if "Multi" in geojson_geom["type"]:
        for c in coords:
            num_vertices = len(c[0])
            total_vertices += num_vertices
    else:
        total_vertices = len(coords[0])

    assert total_vertices > 0, "no vertices were in geometry, check again!"

    return total_vertices


def isclose(
    transform1: rio.Affine,
    transform2: rio.Affine,
    rtol: float = 1e-05,
    atol: float = 1e-08,
) -> bool:
    """
    Operator to compare two Affine transformations. Returns true if equal under
    tolerances.

    The tolerance values are positive, typically very small numbers.
    The relative difference (rtol * abs(b)) and the absolute difference
    atol are added together to compare against the absolute difference
    between a and b.

    Arguments:
        transform1: A rasterio transform object.
        transform2: Another rasterio transform object.
        rtol: Relative tolerance for comparison.
        atol: Absolute tolerance for comparison.

    Returns:
        If the two transforms are equal within the given tolerances.

    """
    transform1_ar = np.array(transform1)
    transform2_ar = np.array(transform2)
    return np.allclose(transform1_ar, transform2_ar, rtol=rtol, atol=atol)


def meta_is_equal(meta1: dict, meta2: dict, rtol=1e-05, atol=1e-08) -> bool:
    """
    Operator for comparing two metadata tags provided by a rasterio dataset.

    Compares affine transformations with isclose method.

    Arguments:
        meta1: A meta object.
        meta2: Another meta object.
        rtol: Relative tolerance for comparison.
        atol: Absolute tolerance for comparison.

    Returns:
        If the two meta objects are equal within the given tolerances.

    """
    meta1_transform = meta1.get("transform")
    meta2_transform = meta2.get("transform")

    meta1 = copy.deepcopy(meta1)
    meta2 = copy.deepcopy(meta2)

    del meta1["transform"]
    del meta2["transform"]

    return isclose(meta1_transform, meta2_transform, rtol, atol) and meta1 == meta2


def check_validity(query_geom: dict):
    """checks for validity of the input geometry supplied by user

    Args:
        query_geom (dict): geojson like dict

    Raises:
        UP42Error: raises up42 INPUT_PARAMETERS_ERROR with validity explanation
    """
    shapely_geom = shape(query_geom)

    if not shapely_geom.is_valid:
        explanation = explain_validity(shapely_geom)
        raise UP42Error(
            SupportedErrors.INPUT_PARAMETERS_ERROR,
            f"Input geometry is not valid due to following reason: {explanation}",
        )


def tiles_to_geom(tiles: List[Tile], func: Callable = mercantile):
    """Apply unary_union function on the list of tiles.
    Args:
        tiles: List of tiles.
        func: A callable used for working with tiles. By defauld it is mercantile. Any other custom
              module can be used.
    """
    return_poly = unary_union([box(*tuple(func.bounds(tile))) for tile in tiles])
    return return_poly
