"""Main module."""
import geojson

from .flowtrace import Flowtrace
from .splitcatchment import SplitCatchment


def splitcatchment(
    lon: float, lat: float, upstream: bool
) -> geojson.feature.FeatureCollection:
    """Delineate the drainage basin from the pour point.

    Parameters
    ----------
    lon : float
        The longitude coordinate of the pour point in decimal degrees
    lat : float
        The latitude coordinate of the pour point in decimal degrees
    upstream : bool
        Determines whether to return the portion of the drainage basin
        that falls outside of the local catchment. If True, then the
        entire drainage basin is returned. If False, then only the portion
        within the local catchment is returned.

    Returns
    -------
    catchment : geojson
        This is the local NHD catchment that the pour point falls within.
        This is also the catchment that gets 'split'.

    splitCatchment : geojson
        This polygon can either be a portion or the entire drainage basin for
        the pour point, and this depends on if the pour  point falls on an NHD
        flowline or not. It gets returned if the drainage basin fits only within
        the local catchment, or if the upstream variable is set to False.

    mergedCatchment : geojson
        This is the entire drainage basin which flows to the pour point. It
        will include area outside of the local catchment, and it will only be
        returned if the upstream variable is set to True.
    """
    results = SplitCatchment(lon, lat, upstream)
    results = results.serialize()
    print("results type: ", type(results))
    return results


def flowtrace(
    lon: float, lat: float, direction: str
) -> geojson.feature.FeatureCollection:
    """Trace the flowpath to the nearest NHD flowline.

    Parameters
    ----------
    lon : float
        The longitude coordinate of the pour point in decimal degrees
    lat : float
        The latitude coordinate of the pour point in decimal degrees
    direction : str
        This variable determines which portion of the NHD flowline will be returned.
        'up' returns the portion of the flowline that is upstream from the
        intersection between the raindropPath and the flowline. 'down' returns the
        downstream portion of the flowline from the intersection point. And 'none'
        returns the entire flowline.

    Returns
    -------
    upstreamFlowline : geojson
        The portion of the NHD flowline upstream from the intersection point. This line
        will only be returned in the variable direction is set to 'up'.
    downstreamFlowline : geojson
        The portion of the NHD flowline downstream from the intersection point. This line
        will only be returned in the variable direction is set to 'down'.
    nhdFlowline : geojson
        This is the entire NHD flowline that the raindropPath intersects with. This line
        will only be returned in the variable direction is set to 'none'.
    raindropPath : geojson
        This is the path that water will follow from the input point to the nearest NHD
        flowline. This line will only be returned if the input point does not fall on
        an NHD flowline.

    """
    results = Flowtrace(lon, lat, direction)
    results = results.serialize()
    return results
