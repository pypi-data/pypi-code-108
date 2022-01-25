# -*- coding: utf-8 -*-
# @Time     : 2021/6/1 11:28
# @Author   : Shigure_Hotaru
# @Email    : minjie96@sencyber.cn
# @File     : geo.py
# @Version  : Python 3.8.5 +
import math


class GeoPoint(object):
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat


def radians(x: float) -> float:
    return x * math.pi / 180


# Unit in M
def distance(a: 'GeoPoint', b: 'GeoPoint') -> float:
    dLon = radians(a.lon - b.lon)
    dLat = radians(a.lat - b.lat)

    asd = math.sin(dLat / 2) * math.sin(dLat / 2) \
        + math.cos(radians(a.lat)) * math.cos(radians(b.lat)) \
        * math.sin(dLon / 2) * math.sin(dLon / 2)

    angle = 2 * math.atan2(math.sqrt(asd), math.sqrt(1 - asd))

    return angle * 6378160


# Geometry distance calculated by coordinates deltas
def distance_value(dir_value: float) -> float:
    a = GeoPoint(0, 0)
    b = GeoPoint(0, dir_value)
    return distance(a, b)


def heading(a: 'GeoPoint', b: 'GeoPoint') -> int:
    dlon = radians(a.lon - b.lon)
    dlat = radians(a.lat - b.lat)

    angle = math.floor(math.atan2(dlon, dlat) / math.pi * 180 + 180)
    return angle
