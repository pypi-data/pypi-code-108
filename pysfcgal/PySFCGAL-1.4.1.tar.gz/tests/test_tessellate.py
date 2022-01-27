import pysfcgal.sfcgal as sfcgal
from pysfcgal.sfcgal import (Point, LineString, Polygon, MultiLineString,
                             GeometryCollection)


def test_simple_polygon():
    print("\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]))")
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    print(poly.wktDecim(1))
    geom = GeometryCollection()
    geom.addGeometry(poly)
    tesselation = geom.tessellate()
    geom2 = sfcgal.read_wkt("""GEOMETRYCOLLECTION(
    TRIANGLE((1.0 0.0,1.0 1.0,0.0 1.0,1.0 0.0)),
    TRIANGLE((0.0 0.0,1.0 0.0,0.0 1.0,0.0 0.0)))""")
    assert tesselation.covers(geom2)


def test_polygon_with_an_hole():
    print(
        """\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)],
        [[(.2,.2),(.2,.8),(.8,.8),(.8,.2)]]))""")
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [
                [(.2, .2), (.2, .8), (.8, .8), (.8, .2)]])
    geom = GeometryCollection()
    geom.addGeometry(poly)
    tesselation = geom.tessellate()
    geom2 = sfcgal.read_wkt("""GEOMETRYCOLLECTION(
    TRIANGLE((0.2 0.2,1.0 0.0,0.8 0.2,0.2 0.2)),
    TRIANGLE((0.0 0.0,1.0 0.0,0.2 0.2,0.0 0.0)),
    TRIANGLE((0.0 0.0,0.2 0.2,0.0 1.0,0.0 0.0)),
    TRIANGLE((0.2 0.8,1.0 1.0,0.0 1.0,0.2 0.8)),
    TRIANGLE((0.2 0.2,0.2 0.8,0.0 1.0,0.2 0.2)),
    TRIANGLE((0.8 0.8,1.0 1.0,0.2 0.8,0.8 0.8)),
    TRIANGLE((0.8 0.2,1.0 1.0,0.8 0.8,0.8 0.2)),
    TRIANGLE((1.0 0.0,1.0 1.0,0.8 0.2,1.0 0.0)))""")
    assert tesselation.covers(geom2)


def test_polygon_with_breaklines():
    print(
        """\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]),
        [LineString([(.2, .6), (.8,.6)]), LineString([(.2, .4), (.8,.4)])])""")
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    lines = [LineString([(.2, .6), (.8, .6)]),
             LineString([(.2, .4), (.8, .4)])]
    geom = GeometryCollection()
    geom.addGeometry(poly)
    for line in lines:
        geom.addGeometry(line)
    tesselation = geom.tessellate()
    geom2 = sfcgal.read_wkt("""GEOMETRYCOLLECTION(
    TRIANGLE((0.2 0.4,1.0 0.0,0.8 0.4,0.2 0.4)),
    TRIANGLE((1.0 0.0,1.0 1.0,0.8 0.6,1.0 0.0)),
    TRIANGLE((0.8 0.4,1.0 0.0,0.8 0.6,0.8 0.4)),
    TRIANGLE((0.2 0.4,0.2 0.6,0.0 1.0,0.2 0.4)),
    TRIANGLE((0.2 0.6,1.0 1.0,0.0 1.0,0.2 0.6)),
    TRIANGLE((0.0 0.0,1.0 0.0,0.2 0.4,0.0 0.0)),
    TRIANGLE((0.0 0.0,0.2 0.4,0.0 1.0,0.0 0.0)),
    TRIANGLE((0.8 0.6,1.0 1.0,0.2 0.6,0.8 0.6)),
    TRIANGLE((0.8 0.4,0.8 0.6,0.2 0.6,0.8 0.4)),
    TRIANGLE((0.2 0.4,0.8 0.4,0.2 0.6,0.2 0.4)))""")
    assert tesselation.covers(geom2)


def test_polygon_with_breaklines_point():
    print(
        """\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]),
        MultiLineString([LineString([(.2, .6), (.8,.6)]), LineString([(.2, .4),
        (.8,.4)])]), [Point(.9, .9)])""")
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    multiline = MultiLineString([[(.2, .6), (.8, .6)], [(.2, .4), (.8, .4)]])
    point = Point(.9, .9)
    geom = GeometryCollection()
    geom.addGeometry(poly)
    geom.addGeometry(multiline)
    geom.addGeometry(point)
    tesselation = geom.tessellate()
    geom2 = sfcgal.read_wkt("""GEOMETRYCOLLECTION(
    TRIANGLE((0.0 0.0,1.0 0.0,0.2 0.4,0.0 0.0)),
    TRIANGLE((1.0 0.0,1.0 1.0,0.8 0.6,1.0 0.0)),
    TRIANGLE((0.8 0.4,1.0 0.0,0.8 0.6,0.8 0.4)),
    TRIANGLE((0.2 0.4,0.2 0.6,0.0 1.0,0.2 0.4)),
    TRIANGLE((0.0 0.0,0.2 0.4,0.0 1.0,0.0 0.0)),
    TRIANGLE((0.9 0.9,1.0 1.0,0.0 1.0,0.9 0.9)),
    TRIANGLE((0.2 0.6,0.9 0.9,0.0 1.0,0.2 0.6)),
    TRIANGLE((0.8 0.6,0.9 0.9,0.2 0.6,0.8 0.6)),
    TRIANGLE((0.2 0.4,0.8 0.4,0.2 0.6,0.2 0.4)),
    TRIANGLE((0.8 0.4,0.8 0.6,0.2 0.6,0.8 0.4)),
    TRIANGLE((0.2 0.4,1.0 0.0,0.8 0.4,0.2 0.4)),
    TRIANGLE((0.8 0.6,1.0 1.0,0.9 0.9,0.8 0.6)))""")
    assert tesselation.covers(geom2)


def test_polygon_with_points():
    print(
        """\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)]), lines=None,
        points=[Point(.9, .9)])""")
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    point = Point(.9, .9)
    geom = GeometryCollection()
    geom.addGeometry(poly)
    geom.addGeometry(point)
    tesselation = geom.tessellate()
    geom2 = sfcgal.read_wkt("""GEOMETRYCOLLECTION(
    TRIANGLE((0.9 0.9,1.0 1.0,0.0 1.0,0.9 0.9)),
    TRIANGLE((0.0 0.0,1.0 0.0,0.9 0.9,0.0 0.0)),
    TRIANGLE((0.0 0.0,0.9 0.9,0.0 1.0,0.0 0.0)),
    TRIANGLE((1.0 0.0,1.0 1.0,0.9 0.9,1.0 0.0)))""")
    assert tesselation.covers(geom2)


def test_polygon_with_quasi_collinear_points():
    print("""\n\ntessellate(Polygon(((-4.165589, -29.100525),
    (8.623957000000001, -28.461553), (21.413503, -27.822581), (10.706928,
    -13.90117), (0.000353, 0.020242), (-2.082618, -14.540141), (-4.165589,
    -29.100525))))""")
    poly = Polygon([(-4.165589, -29.100525),
                    (8.623957000000001, -28.461553),
                    (21.413503, -27.822581),
                    (10.706928, -13.90117),
                    (0.000353, 0.020242),
                    (-2.082618, -14.540141),
                    (-4.165589, -29.100525)])
    geom = GeometryCollection()
    geom.addGeometry(poly)
    tesselation = geom.tessellate()
    geom2 = sfcgal.read_wkt("""GEOMETRYCOLLECTION(
    TRIANGLE((-4.1656 -29.1005,8.6240 -28.4616,-2.0826 -14.5401,
    -4.1656 -29.1005)),
    TRIANGLE((8.6240 -28.4616,10.7069 -13.9012,-2.0826 -14.5401,
    8.6240 -28.4616)),
    TRIANGLE((-2.0826 -14.5401,10.7069 -13.9012,0.0004 0.0202,
    -2.0826 -14.5401)),
    TRIANGLE((8.6240 -28.4616,21.4135 -27.8226,10.7069
    -13.9012,8.6240 -28.4616)))""")
    geom1 = sfcgal.read_wkt(tesselation.wktDecim(4))
    assert geom1.covers(geom2)


def test_polygon_with_hole_and_break_lines():
    print("""\n\ntessellate(Polygon([(0,0), (1,0), (1,1), (0,1)], [[(.2,.2),
    (.2,.8), (.8,.8), (.8, .2)]]), lines=[LineString([(.1, .1), (.9,.1)]),
    LineString([(.9, .1), (.9,.9)]), LineString([(.9, .9), (.1,.9)]),
    LineString([(.1, .9), (.1,.1)])])""")
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], [
                [(.2, .2), (.2, .8), (.8, .8), (.8, .2)]])
    lines = [LineString([(.1, .1), (.9, .1)]),
             LineString([(.9, .1), (.9, .9)]),
             LineString([(.9, .9), (.1, .9)]),
             LineString([(.1, .9), (.1, .1)])]
    geom = GeometryCollection()
    geom.addGeometry(poly)
    for line in lines:
        geom.addGeometry(line)
    tesselation = geom.tessellate()
    geom2 = sfcgal.read_wkt("""GEOMETRYCOLLECTION(
    TRIANGLE((0.0 0.0,1.0 0.0,0.1 0.1,0.0 0.0)),
    TRIANGLE((0.0 0.0,0.1 0.1,0.0 1.0,0.0 0.0)),
    TRIANGLE((0.1 0.9,1.0 1.0,0.0 1.0,0.1 0.9)),
    TRIANGLE((0.1 0.1,0.1 0.9,0.0 1.0,0.1 0.1)),
    TRIANGLE((0.1 0.1,0.9 0.1,0.2 0.2,0.1 0.1)),
    TRIANGLE((0.1 0.1,1.0 0.0,0.9 0.1,0.1 0.1)),
    TRIANGLE((0.2 0.8,0.9 0.9,0.1 0.9,0.2 0.8)),
    TRIANGLE((0.1 0.1,0.2 0.2,0.1 0.9,0.1 0.1)),
    TRIANGLE((0.2 0.2,0.2 0.8,0.1 0.9,0.2 0.2)),
    TRIANGLE((0.9 0.9,1.0 1.0,0.1 0.9,0.9 0.9)),
    TRIANGLE((0.2 0.2,0.9 0.1,0.8 0.2,0.2 0.2)),
    TRIANGLE((0.8 0.8,0.9 0.9,0.2 0.8,0.8 0.8)),
    TRIANGLE((0.9 0.1,0.9 0.9,0.8 0.2,0.9 0.1)),
    TRIANGLE((0.8 0.2,0.9 0.9,0.8 0.8,0.8 0.2)),
    TRIANGLE((0.9 0.1,1.0 1.0,0.9 0.9,0.9 0.1)),
    TRIANGLE((1.0 0.0,1.0 1.0,0.9 0.1,1.0 0.0)))""")
    assert tesselation.covers(geom2)
