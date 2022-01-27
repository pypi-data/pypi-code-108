# some example geometries

data = {}

data["point1"] = {
    "type": "Point",
    "coordinates": (54.1305020, -23.64328494)
}

data["point2"] = {
    "type": "Point",
    "coordinates": (54.1305020, -23.64328494, 50.20204)
}

data["multipoint"] = {
    "type": "MultiPoint",
    "coordinates": [
        data["point1"]["coordinates"],
        data["point2"]["coordinates"],
    ]
}

data["line1"] = {
    "type": "LineString",
    "coordinates": [(0, 0), (1, 2), (-5, -3.5)]
}

data["line2"] = {
    "type": "LineString",
    "coordinates": [(3.4, 6.4, 3.7), (5.6, 2.5, 3.6),
                    (4.5, 6.7, 2.4), (-6.7, 6.5, 1.2)]
}

data["multilinestring1"] = {
    "type": "MultiLineString",
    "coordinates": [
        data["line1"]["coordinates"],
        data["line2"]["coordinates"],
    ]
}

data["polygon1"] = {
    "type": "Polygon",
    "coordinates": [[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]]
}

data["multipolygon1"] = {
    "type": "MultiPolygon",
    "coordinates": [
        [[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]],
        [[(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)]],
    ]
}

data["gc1"] = {
    "type": "GeometryCollection",
    "geometries": [
        data["point1"],
        data["line1"],
        data["polygon1"],
    ]
}
