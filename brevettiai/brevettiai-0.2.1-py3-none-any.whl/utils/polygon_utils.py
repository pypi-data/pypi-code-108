import numpy as np
from shapely.geometry import Point, LinearRing, LineString, Polygon


def cv2_contour_to_shapely(contour, hole=False, resolution=2):
    len_ = len(contour)
    if len_ == 1:
        return Point(contour[0, 0]).buffer(0.5, cap_style=3, resolution=resolution)
    elif len_ == 2:
        return LineString(contour[:, 0]).buffer(0.5, cap_style=3, resolution=resolution)
    elif len_ >= 3:
        p = Polygon(LinearRing(contour[:, 0]).buffer(0.5, cap_style=1, resolution=resolution).exterior)
        # Only polygons may be holes
        return p.buffer(-1) if hole else p
    else:
        return Polygon()


def simplify_polygon(polygon, min_=0.2, max_=3, alpha=0.005, preserve_topology=True):
    tolerance = np.clip(alpha * polygon.length, min_, max_)
    return polygon.simplify(tolerance, preserve_topology=preserve_topology)
