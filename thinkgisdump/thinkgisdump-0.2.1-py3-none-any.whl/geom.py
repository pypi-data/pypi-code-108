import math

from geojson_rewind import rewind

# Returned coordinates default to zoom of 19
WINDOW_ZOOM = 19


def window_point_to_lon_lat(wx, wy):
    """
    Based on w2LL function in https://richlandil.wthgis.com/tgis/tgisServer2.js
    """
    x = wx / (2 ** WINDOW_ZOOM)
    y = wy / (2 ** WINDOW_ZOOM)
    # Static values from code
    origin_x = 128.0
    origin_y = 128.0
    pixels_per_lon = 256 / 360
    pixels_per_lon_radian = 256 / (2 * math.pi)

    lon = (x - origin_x) / pixels_per_lon
    lat_radians = (y - origin_y) / (-pixels_per_lon_radian)
    lat = (2 * math.atan(math.exp(lat_radians)) - math.pi / 2) / (math.pi / 180)
    return lon, lat


def parse_coords(geom_str):
    """
    Based on drawPoly function https://richlandil.wthgis.com/tgis/tgisServer2.js
    """
    geom_split = geom_str.split(",")
    point_count = int((len(geom_split) - 2) / 2)

    x_points = [int(geom_split[2])]
    y_points = [int(geom_split[3])]

    for i in range(1, point_count):
        x_points.append(x_points[i - 1] + int(geom_split[2 + i * 2]))
        y_points.append(y_points[i - 1] + int(geom_split[2 + i * 2 + 1]))

    window_points = zip(x_points, y_points)

    return [window_point_to_lon_lat(wx, wy) for wx, wy in window_points]


def is_point(geom_str):
    return set([str(i) for i in range(-5, 11)]).issuperset(set(geom_str.split(",")[4:]))


def point_coords(coords):
    """Pull the center of a circle returned for points"""
    return [
        (max(c[0] for c in coords) + min(c[0] for c in coords)) / 2,
        (max(c[1] for c in coords) + min(c[1] for c in coords)) / 2,
    ]


def parse_geometry(geom_strs):
    """Lines not used"""
    coord_lists = [parse_coords(geom_str) for geom_str in geom_strs]

    if len(coord_lists) == 0:
        return

    if all(is_point(geom_str) for geom_str in geom_strs):
        if len(geom_strs) == 1:
            return {"type": "Point", "coordinates": point_coords(coord_lists[0])}
        else:
            return {
                "type": "MultiPoint",
                "coordinates": [point_coords(c) for c in coord_lists],
            }

    if len(coord_lists) == 1:
        return rewind({"type": "Polygon", "coordinates": coord_lists})
    else:
        return rewind(
            {"type": "MultiPolygon", "coordinates": [[cl] for cl in coord_lists]}
        )
