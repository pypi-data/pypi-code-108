import numpy as np
import os
from math import radians, cos, sin, asin, sqrt
import geopandas as geopd
import scipy.optimize
import itertools

R = 6378

##########################################################
def haversine(p1, p2, unit='km'):
    """Calculate the great circle distance (in meters) between two points
    on the earth (specified in decimal degrees). It expects points in the
    format (lon, lat)"""
    lonrad1, latrad1 = np.radians(p1)
    lonrad2, latrad2 = np.radians(p2)

    dlon = lonrad2 - lonrad1
    dlat = latrad2 - latrad1
    a = np.sin(dlat/2)**2 + np.cos(latrad1) * np.cos(latrad2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    if unit in ['m', 'meters']: return c * R * 1000
    else: return c * R

##########################################################
def haversine_all(points, unit='km'):
    """Calculate the great circle distance (in meters) between two points
    on the earth (specified in decimal degrees) between every pair of points
    in @points. It expects points in the format (lon, lat)"""
    n = len(points)
    combs = np.array(list(itertools.combinations(list(range(n)), 2)))
    points = np.radians((points.copy()))

    lon1 = points[combs[:, 0], 0]
    lat1 = points[combs[:, 0], 1]
    lon2 = points[combs[:, 1], 0]
    lat2 = points[combs[:, 1], 1]

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    if unit in ['m', 'meters']: return combs, c * R * 1000
    else: return combs, c * R

##########################################################
def get_shp_points(shppath):
    """Get points from @shppath and returns list of points, x and y """

    geodf = geopd.read_file(shppath)
    shapefile = geodf.geometry.values[0]
    if shapefile.geom_type == 'Polygon': return shapefile.exterior.xy
    elif shapefile.geom_type == 'MultiPolygon':
        polys = list(shapefile)
        areas = [p.area for p in polys]
        poly = polys[np.argmax(areas)]
        return poly.exterior.xy

##########################################################
def deg2num(lon_deg, lat_deg, zoom, imgsize=256):
    """From the (lat,lon) in degrees, get the (x, y) of the tile,
    as well as the pixel in the image."""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = ((lon_deg + 180.0) / 360.0 * n)
    ytile = ((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (int(xtile), int(ytile),
            int(math.modf(xtile)[0]*imgsize), int(math.modf(ytile)[0]*imgsize))

##########################################################
def num2deg(xtile, ytile, zoom):
    """From the tile x and y, get the (lat,lon) in degrees"""
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)

##########################################################
def dist_to_deltalonlat(dist, lonref, latref):
    """Get the deltalon and deltalat based on a reference lat and lon.
    For the same distance, lon varies more than lat."""
    def get_delta_lon_from_d(lon1, lat1=latref, lon2=lonref, lat2=latref):
        return dist - haversine([lon1, lat1], [lon2, lat2])

    def get_delta_lat_from_d(lat1, lon1=lonref, lat2=latref, lon2=lonref):
        return dist - haversine([lon1, lat1], [lon2, lat2])

    lon2 = lonref + 20 # a large enough diff in lon to contain the @dist
    lon2 = scipy.optimize.bisect(get_delta_lon_from_d, lonref, lon2,
            xtol=0.000001, rtol=0.000001)

    lat2 = latref + 20 # a large enough diff in lon to contain the @dist
    lat2 = scipy.optimize.bisect(get_delta_lat_from_d, latref, lat2,
            xtol=0.000001, rtol=0.000001)

    return np.abs(lon2 - lonref), np.abs(lat2 - latref)

