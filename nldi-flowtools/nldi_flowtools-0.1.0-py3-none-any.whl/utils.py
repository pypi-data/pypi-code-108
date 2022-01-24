"""Utility script containing functions used for flowtrace and splitcatchment modules."""
import json
import math
import sys
from typing import Any

import numpy as np
import pyflwdir
import pyproj
import rasterio.mask
import requests
import shapely.geometry
from shapely.geometry import GeometryCollection
from shapely.geometry import LineString
from shapely.geometry import mapping
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import shape
from shapely.ops import snap
from shapely.ops import split
from shapely.ops import transform

# arguments
NLDI_URL = "https://labs.waterdata.usgs.gov/api/nldi/linked-data/comid/"
NLDI_GEOSERVER_URL = "https://labs.waterdata.usgs.gov/geoserver/wmadata/ows"
IN_FDR_COG = (
    "/vsicurl/https://prod-is-usgs-sb-prod-publish.s3.amazonaws.com"
    "/5fe0d98dd34e30b9123eedb0/fdr.tif"
)


# functions
def geom_to_geojson(geom: shapely.geometry) -> dict[Any, Any]:
    """Return a geojson object from an OGR geom object."""
    geojson_dict: dict[Any, Any] = mapping(geom)

    return geojson_dict


def transform_geom(proj: object, geom: shapely.geometry) -> shapely.geometry:
    """Transform geometry to input projection."""
    projected_geom = transform(proj, geom)

    return projected_geom


def get_local_catchment(x: float, y: float) -> tuple[str, shapely.geometry]:
    """Perform point in polygon query to NLDI geoserver to get local catchment geometry."""
    print("requesting local catchment...")

    wkt_point = f"POINT({x} {y})"
    cql_filter = f"INTERSECTS(the_geom, {wkt_point})"

    payload = {
        "service": "wfs",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": "wmadata:catchmentsp",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "CQL_FILTER": cql_filter,
    }

    # request catchment geometry from point in polygon query from NLDI geoserver
    try:
        r: requests.models.Response = requests.get(NLDI_GEOSERVER_URL, params=payload)

        resp = r.json()

        # get catchment id
        catchment_id = json.dumps(resp["features"][0]["properties"]["featureid"])

    except ValueError:
        if r.status_code == 200:
            print(
                "Get local catchment request failed. Check to make sure query was "
                "submitted with lon, lat coords. Quiting nldi_flowtools query."
            )

        else:
            print(
                "Quiting nldi_flowtools query. Error requesting catchment from Geoserver:",
                r.status_code,
            )

        # Kill program if request fails or if the response is not what is expected.
        sys.exit(1)

    features = resp["features"][0]
    if (
        len(features["geometry"]["coordinates"]) > 1
    ):  # If the catchment is multipoly (I know, this is SUPER annoying)
        i: int = 0
        catchment_geom = []
        while i < len(features["geometry"]["coordinates"]):
            print(
                "Multipolygon catchment found:",
                json.dumps(features["properties"]["featureid"]),
            )
            catchment_geom.append(Polygon(features["geometry"]["coordinates"][i][0]))
            i += 1
        catchment_geom = MultiPolygon(catchment_geom)
    else:  # Else, the catchment is a single polygon (as it should be)
        catchment_geom = Polygon(features["geometry"]["coordinates"][0][0])

    print("got local catchment:", catchment_id)
    return catchment_id, catchment_geom


def get_local_flowline(catchment_id: str) -> tuple[dict[Any, Any], shapely.geometry]:
    """Request NDH Flowline from NLDI with Catchment ID."""
    cql_filter = f"comid={catchment_id}"

    payload = {
        "service": "wfs",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": "wmadata:nhdflowline_network",
        "maxFeatures": "500",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "CQL_FILTER": cql_filter,
    }

    # request flowline geometry from NLDI geoserver using catchment ID
    try:
        r: requests.models.Response = requests.get(NLDI_GEOSERVER_URL, params=payload)

        flowline = r.json()
        # check json response for geometry
        nhd_geom = flowline["features"][0]["geometry"]

    except ValueError:
        if r.status_code == 200:
            print(
                "Get local flowline request failed. Check to make sure query "
                "was submitted with lon, lat coords. Quiting nldi_flowtools query."
            )

        else:
            print(
                "Quiting nldi_flowtools query. Error requesting flowline from Geoserver:",
                r.status_code,
            )

        # Kill program if request fails.
        sys.exit(1)

    print("got local flowline")

    # Convert the flowline to a geometry colelction to be exported

    nhd_flowline = GeometryCollection([shape(nhd_geom)]).geoms[0]
    nhd_flowline = LineString(
        [xy[0:2] for xy in list(nhd_flowline.geoms[0].coords)]
    )  # Convert xyz to xy

    return flowline, nhd_flowline


def get_total_basin(catchment_id: str) -> shapely.geometry:
    """Use local catchment identifier to get local upstream basin geometry from NLDI."""
    print("getting upstream basin...")

    # request upstream basin
    payload = {"f": "json", "simplified": "false"}

    # request upstream basin from NLDI using comid of catchment point is in
    try:
        r: requests.models.Response = requests.get(
            NLDI_URL + catchment_id + "/basin", params=payload
        )

        resp = r.json()

        # convert geojson to ogr geom
        features = resp["features"]
        total_basin_geom = GeometryCollection(
            [shape(feature["geometry"]).buffer(0) for feature in features]
        )

    except ValueError:
        if r.status_code == 200:
            print(
                "Get upstream basin request failed. Check to make sure query "
                "was submitted with lon, lat coords. Quiting nldi_flowtools query."
            )

        else:
            print(
                "Quiting nldi_flowtools query. Error requesting upstream basin from the NLDI:",
                r.status_code,
            )

        # Kill program if request fails.
        sys.exit(1)

    print("finished getting upstream basin")
    return total_basin_geom


def get_upstream_basin(
    catchment: shapely.geometry, total_basin_geom: shapely.geometry
) -> shapely.geometry:
    """Get the upstream basin geometry.

    This is done by subtracting the local catchment from the total_basin_geom.
    """
    d = 0.00045
    cf = 1.3  # cofactor

    upstream_basin_geom = (
        total_basin_geom.symmetric_difference(catchment)
        .buffer(-d)
        .buffer(d * cf)
        .simplify(d)
    )
    return upstream_basin_geom


def merge_geometry(
    catchment: shapely.geometry,
    split_catchment: shapely.geometry,
    upstream_basin: shapely.geometry,
) -> shapely.geometry:
    """Attempt at merging geometries."""
    print("merging geometries...")
    d = 0.00045
    # d2 = 0.00015 # distance
    cf = 1.3  # cofactor

    split_catchment = split_catchment.simplify(d)

    diff = catchment.difference(split_catchment).buffer(-d).buffer(d * cf).simplify(d)
    merged_catchment_geom = (
        upstream_basin.difference(diff).buffer(-d).buffer(d * cf).simplify(d)
    )

    print("finished merging geometries")

    return merged_catchment_geom


def get_coordsys() -> tuple[object, object]:
    """Get coordinate system of input flow direction raster."""
    with rasterio.open(IN_FDR_COG, "r") as ds:
        # get raster crs
        dest_crs = ds.crs

        # create wgs84 crs
        wgs84 = pyproj.CRS("EPSG:4326")

        # check to see if raster is already wgs84
        # latlon = dest_crs == wgs84

        transform_to_raster = pyproj.Transformer.from_crs(
            wgs84, dest_crs, always_xy=True
        ).transform
        transform_to_wgs84 = pyproj.Transformer.from_crs(
            dest_crs, wgs84, always_xy=True
        ).transform

    return transform_to_raster, transform_to_wgs84


def project_point(x: float, y: float, transform_to_raster: object) -> shapely.geometry:
    """Project point to flow direction raster crs."""
    point_geom = Point(x, y)
    print("original point:", point_geom)

    projected_point = transform_geom(transform_to_raster, point_geom)
    print("projected point:", projected_point)

    projected_xy = projected_point.coords[:][0]

    # Test if one of the project point coordinates is infinity. If this is the case
    # then the point was not properly projected to the CRS of the DEM. This has happened
    # when proj version is greater than 6.2.1
    projected_x = projected_point.coords[:][0][0]
    if math.isinf(projected_x) is True:
        print(
            "Input point was not properly projected. This could be an error caused by PROJ."
        )

    return projected_xy


def get_flowgrid(
    catchment_geom: shapely.geometry,
    transform_to_raster: object,
) -> tuple[pyflwdir.pyflwdir.FlwdirRaster, object]:
    """Get the FDR for the local catchment area.

    Use a 90 meter buffer of the local catchment to clip the
    NHD Plus v2 flow direction raster.
    """
    print("start clip raster")
    with rasterio.open(IN_FDR_COG, "r") as ds:

        # get raster crs
        dest_crs = ds.crs

        # create wgs84 crs
        wgs84 = pyproj.CRS("EPSG:4326")

        # check to see if raster is already wgs84
        latlon = dest_crs == wgs84

        # transform catchment geometry to use for clip
        projected_catchment_geom = transform_geom(transform_to_raster, catchment_geom)

        # buffer catchment geometry by 90m before clipping flow direction raster
        buffer_projected_catchment_geom = GeometryCollection(
            [projected_catchment_geom.buffer(90)]
        )

        # clip input fd
        flwdir, flwdir_transform = rasterio.mask.mask(
            ds, buffer_projected_catchment_geom, crop=True
        )
        print("finish clip raster")

    # import clipped fdr into pyflwdir
    flw = pyflwdir.from_array(
        flwdir[0], ftype="d8", transform=flwdir_transform, latlon=latlon
    )

    return flw, flwdir_transform


def split_catchment(
    catchment_geom: shapely.geometry,
    projected_xy: shapely.geometry,
    transform_to_raster: object,
    transform_to_wgs84: object,
) -> shapely.geometry:
    """Produce split catchment delienation from X,Y."""
    print("start split catchment...")

    with rasterio.open(IN_FDR_COG, "r") as ds:
        # print fdr value at click point
        for val in ds.sample([projected_xy]):
            print("FDR Value at Click Point:", val)

        # get raster crs
        dest_crs = ds.crs

        # create wgs84 crs
        wgs84 = pyproj.CRS("EPSG:4326")

        # check to see if raster is already wgs84
        latlon = dest_crs == wgs84

        # transform catchment geometry to use for clip
        projected_catchment_geom = transform_geom(transform_to_raster, catchment_geom)

        # buffer catchment geometry by 0m before clipping flow direction raster
        buffer_projected_catchment_geom = GeometryCollection(
            [projected_catchment_geom.buffer(0)]
        )

        # clip input fd
        flwdir, flwdir_transform = rasterio.mask.mask(
            ds, buffer_projected_catchment_geom, crop=True
        )
        print("finish clip raster")

    # import clipped fdr into pyflwdir
    flw = pyflwdir.from_array(
        flwdir[0], ftype="d8", transform=flwdir_transform, latlon=latlon
    )

    # used for snapping click point
    stream_order = flw.stream_order()
    print("Calculated Stream Order")

    # delineate subbasins
    subbasins = flw.basins(
        xy=projected_xy, streams=stream_order > 1
    )  # streams=stream_order>4

    # convert subbasins from uint32
    subbasins = subbasins.astype(np.int32)

    # convert raster to features
    mask = subbasins != 0
    polys = rasterio.features.shapes(subbasins, transform=flwdir_transform, mask=mask)

    # just get one we want [not sure why we need to grab this]
    poly = next(polys)

    # project back to wgs84
    split_geom = transform(transform_to_wgs84, shape(poly[0]))

    print("finish split catchment.")
    return split_geom


def get_on_flowline(
    projected_xy: shapely.geometry,
    flowline: dict[Any, Any],
    transform_to_raster: object,
) -> bool:
    """Determine if x,y is on a NHD Flowline (within 15m)."""
    linestring_list = []
    for pair in flowline["features"][0]["geometry"]["coordinates"][0]:
        linestring_list.append((pair[0], pair[1]))

    linestring = LineString(linestring_list)

    # Project the flowline to the same crs as the flw raster
    projected_nhd = transform_geom(transform_to_raster, linestring)

    # What is the distance from the Click Point to the NHD Flowline?
    click_pnt = Point(projected_xy)
    click_dist = click_pnt.distance(projected_nhd)

    # Is the Click Point on a flowline?
    if click_dist < 15:
        print("Clickpoint is on a NHD Flowline")
        on_flowline: bool = True

    else:
        print("Clickpoint is NOT on a NHD Flowline")
        on_flowline = False

    return on_flowline


def get_raindrop_path(  # noqa C901
    flw: pyflwdir.pyflwdir.FlwdirRaster,
    projected_xy: shapely.geometry,
    nhd_flowline: shapely.geometry,
    flowline: dict[Any, Any],
    transform_to_raster: object,
    transform_to_wgs84: object,
) -> shapely.geometry.linestring.LineString:
    """Trace the flowpath from the X,Y point to the first NHD Flowline."""
    print("Getting raindrop path.")
    # Convert the flowline to a linestring
    linestring_list = []
    for pair in flowline["features"][0]["geometry"]["coordinates"][0]:
        linestring_list.append((pair[0], pair[1]))

    linestring = LineString(linestring_list)

    # Project the flowline to the same crs as the flw raster
    projected_nhd = transform_geom(
        transform_to_raster, linestring
    )  # dfNHD.geometry[0][0]

    # Convert the flowline coordinates to a format that can be iterated
    line = list(projected_nhd.coords)
    print("created list of nhd coords  ")

    # Loop thru the flowline coordinates, grab the xy coordinantes and put them in
    # separate lists. Use these lists in the index function of pyflwdir to grap the
    # ids of the cell in which these points fall
    # lastID = len(line) - 1
    x_list = []
    y_list = []
    nhd_cell_list = []
    for i in line:
        # if i == line[lastID]:    # Pass the last point in the flowline. Sometimes
        #     pass                 # this point is outside of the flw raster and this
        # if i != line[lastID]:    # will cause flw.index() to fail.
        x_list = i[0]
        y_list = i[1]
        cell_index = flw.index(x_list, y_list)
        nhd_cell_list.append(cell_index)
    print("nhd converted to raster  ")

    # create mask from in the same of the flw raster
    nhd_mask = np.zeros(flw.shape, dtype=bool)

    # Set the flowline cells to true
    nhd_mask.flat[nhd_cell_list] = True

    # trace downstream
    path, dist = flw.path(xy=projected_xy, mask=nhd_mask)

    # get points on raindrop_path
    path_pnts = flw.xy(path)

    # loop thru the downstream path points and create a dict of coords
    last_pnt_id = path_pnts[0][0].size - 1
    i = 0
    coord_list: dict[str, list[Any]] = {"type": "LineString", "coordinates": []}
    while i <= last_pnt_id:
        x: float = path_pnts[0][0][i]
        y: float = path_pnts[1][0][i]
        coord_list["coordinates"].append([x, y])
        i += 1

    if len(coord_list["coordinates"]) < 2:
        print("Failed to trace raindrop path! Try another point. ")
    if len(coord_list["coordinates"]) >= 2:
        print("traced raindrop path   ")

    # Convert the dict of coords to ogr geom
    path_geom = GeometryCollection([shape(coord_list)])

    # Project the ogr geom to WGS84
    projected_path_geom = transform(transform_to_wgs84, path_geom)

    # Snap raindrop_path points to the flowline within a ~35m buffer
    snap_path = snap(projected_path_geom.geoms[0], nhd_flowline, 0.00045)

    # Convert snap_path to a geometry collection
    snap_path = GeometryCollection([snap_path])

    # Grap all the points of intersection between the raindrop_path and the flowline
    intersection_pnts = nhd_flowline.intersection(snap_path)

    # Filter the intersecting points by geometry type. The downstream path
    # will then be split by each point in the intersection_pnts geom.
    if type(intersection_pnts) == shapely.geometry.multipoint.MultiPoint:
        for i in intersection_pnts:
            split_pnt = snap(Point(i.coords), snap_path, 0.0002)
            snap_path = split(snap_path.geoms[0], split_pnt)
    if type(intersection_pnts) == shapely.geometry.linestring.LineString:
        for i in intersection_pnts.coords:
            split_pnt = snap(Point(i), snap_path, 0.0002)
            snap_path = split(snap_path.geoms[0], split_pnt)
    if type(intersection_pnts) == shapely.geometry.point.Point:
        split_pnt = snap(intersection_pnts, snap_path, 0.0002)
        snap_path = split(snap_path.geoms[0], split_pnt)
    if (
        type(intersection_pnts) == shapely.geometry.multilinestring.MultiLineString
        or type(intersection_pnts) == shapely.geometry.collection.GeometryCollection
    ):
        for i in intersection_pnts:
            for j in i.coords:
                split_pnt = snap(Point(j), snap_path, 0.0002)
                snap_path = split(snap_path.geoms[0], split_pnt)

    # The first linestring in the snap_path geometry collection in the raindrop_path
    raindrop_path = snap_path.geoms[0]

    return raindrop_path


def get_intersection_point(
    x: float,
    y: float,
    on_flowline: bool,
    *raindrop_path: shapely.geometry.linestring.LineString,
) -> shapely.geometry.point.Point:
    """Return the intersection point between the NHD Flowline and the raindrop_path."""
    print("Looking for intersection point")
    if on_flowline is True:
        intersection_point = Point(x, y)

    if on_flowline is False:
        # raindrop_path is returned as a tuple, reset it to the first part of the tuple
        raindrop_path: shapely.coords.CoordinateSequence = raindrop_path[0]
        # The last point on the raindrop_path is the intersection_point
        coord_id: int = len(raindrop_path.coords) - 1
        intersection_point = Point(
            raindrop_path.coords[coord_id][0], raindrop_path.coords[coord_id][1]
        )  # The first two coords of the point are used incase the point has a Z value
        print("Found intersection point")

    return intersection_point


def get_reach_measure(
    intersection_point: shapely.geometry.point.Point,
    flowline: dict[Any, Any],
    *raindrop_path: shapely.geometry.linestring.LineString,
) -> dict[str, Any]:
    """Collect NHD Flowline Reach Code and Measure."""
    print("intersection_point: ", intersection_point)

    # Set Geoid to measure distances in meters
    geod = pyproj.Geod(ellps="WGS84")

    # Convert the flowline to a geometry colelction to be exported
    nhd_geom = flowline["features"][0]["geometry"]
    nhd_flowline = GeometryCollection([shape(nhd_geom)]).geoms[0]

    # Select the stream name from the NHD Flowline
    stream_name = flowline["features"][0]["properties"]["gnis_name"]
    if stream_name == " ":
        stream_name = "none"

    # Create stream_info dict and add some data
    stream_info = {
        "gnis_name": stream_name,
        "comid": flowline["features"][0]["properties"][
            "comid"
        ],  # 'lengthkm': flowline['features'][0]['properties']['lengthkm'],
        "intersection_point": (
            intersection_point.coords[0][1],
            intersection_point.coords[0][0],
        ),
        "reachcode": flowline["features"][0]["properties"]["reachcode"],
    }

    # Add more data to the stream_info dict
    if raindrop_path:
        stream_info["raindrop_pathDist"] = round(
            geod.geometry_length(raindrop_path[0]), 2
        )

    # If the intersection_point is on the NHD Flowline, split the flowline at the point
    if nhd_flowline.intersects(intersection_point) is True:
        split_nhd_flowline = split(nhd_flowline, intersection_point)

    # If they don't intersect (weird right?) buffer the intersection_point
    # and then split the flowline
    if nhd_flowline.intersects(intersection_point) is False:
        buff_dist = intersection_point.distance(nhd_flowline) * 1.01
        buff_intersection_point = intersection_point.buffer(buff_dist)
        split_nhd_flowline = split(nhd_flowline, buff_intersection_point)

    # If the NHD Flowline was split, then calculate measure
    if len(split_nhd_flowline.geoms) > 1:
        last_line_id = len(split_nhd_flowline.geoms) - 1
        dist_to_outlet = round(
            geod.geometry_length(split_nhd_flowline.geoms[last_line_id]), 2
        )
        flowline_leng = round(geod.geometry_length(nhd_flowline), 2)
        stream_info["measure"] = round((dist_to_outlet / flowline_leng) * 100, 2)
    else:  # If NHDFlowline was not split, then the intersection_point is either the
        # first or last point on the NHDFlowline
        start_pnt = Point(nhd_flowline[0].coords[0][0], nhd_flowline[0].coords[0][1])
        last_pnt_id = len(nhd_flowline[0].coords) - 1
        last_pnt = Point(
            nhd_flowline[0].coords[last_pnt_id][0],
            nhd_flowline[0].coords[last_pnt_id][1],
        )
        if intersection_point == start_pnt:
            stream_info["measure"] = 100
            error = "The point of intersection is the first point on the NHD Flowline."
        elif intersection_point == last_pnt:
            stream_info["measure"] = 0
            error = "The point of intersection is the last point on the NHD Flowline."
        elif intersection_point != start_pnt and intersection_point != last_pnt:
            error = "Error: NHD Flowline measure not calculated"
            stream_info["measure"] = "null"
        print(error)

    print("calculated measure and reach")

    return stream_info


def split_flowline(
    intersection_point: shapely.geometry.point.Point, flowline: dict[Any, Any]
) -> tuple[
    shapely.geometry.linestring.LineString, shapely.geometry.linestring.LineString
]:
    """Split the NHD Flowline at the intersection point."""
    # Convert the flowline to a geometry colelction to be exported
    nhd_geom = flowline["features"][0]["geometry"]
    nhd_flowline = GeometryCollection([shape(nhd_geom)]).geoms[0]
    nhd_flowline = LineString(
        [xy[0:2] for xy in list(nhd_flowline.geoms[0].coords)]
    )  # Convert xyz to xy

    # If the intersection_point is on the NHD Flowline, split the flowline at the point
    if nhd_flowline.intersects(intersection_point) is True:
        split_nhd_flowline = split(nhd_flowline, intersection_point)

    # If they don't intersect (weird right?), buffer the intersection_point
    # and then split the flowline
    if nhd_flowline.intersects(intersection_point) is False:
        buff_dist = intersection_point.distance(nhd_flowline) * 1.01
        buff_intersection_point = intersection_point.buffer(buff_dist)
        split_nhd_flowline = split(nhd_flowline, buff_intersection_point)

    # If the NHD Flowline was split, then calculate measure
    if len(split_nhd_flowline.geoms) > 1:
        last_line_id = len(split_nhd_flowline.geoms) - 1
        upstream_flowline = split_nhd_flowline.geoms[0]
        downstream_flowline = split_nhd_flowline.geoms[last_line_id]

    else:  # If NHDFlowline was not split, then the intersection_point is either the
        # first or last point on the NHDFlowline
        start_pnt = Point(nhd_flowline[0].coords[0][0], nhd_flowline[0].coords[0][1])
        last_pnt_id = len(nhd_flowline[0].coords) - 1
        last_pnt = Point(
            nhd_flowline[0].coords[last_pnt_id][0],
            nhd_flowline[0].coords[last_pnt_id][1],
        )
        if intersection_point == start_pnt:
            upstream_flowline = GeometryCollection()
            downstream_flowline = split_nhd_flowline
            error = "The point of intersection is the first point on the NHD Flowline."
        elif intersection_point == last_pnt:
            downstream_flowline = GeometryCollection()
            upstream_flowline = split_nhd_flowline
            error = "The point of intersection is the last point on the NHD Flowline."
        elif intersection_point != start_pnt and intersection_point != last_pnt:
            error = "Error: NHD Flowline measure not calculated"
            downstream_flowline = GeometryCollection()
            upstream_flowline = GeometryCollection()
        print(error)

    print("split NHD Flowline")

    return upstream_flowline, downstream_flowline


def merge_downstream_path(
    raindrop_path: shapely.geometry.linestring.LineString,
    downstream_flowline: shapely.geometry.linestring.LineString,
) -> shapely.geometry.linestring.LineString:
    """Merge downstream_flowline and raindrop_path."""
    # Pull out coords, place in a list and convert to a Linestring. This ensures
    # that the returned geometry is a single Linestring and not a Multilinestring
    lines = MultiLineString([raindrop_path, downstream_flowline])
    outcoords = [list(i.coords) for i in lines]
    downstream_path = LineString([i for sublist in outcoords for i in sublist])
    return downstream_path
