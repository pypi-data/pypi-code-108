from ._sfcgal import ffi, lib

# this must be called before anything else
lib.sfcgal_init()


class DimensionError(Exception):
    pass


def sfcgal_version():
    """Returns the version string of SFCGAL"""
    version = ffi.string(lib.sfcgal_version()).decode("utf-8")
    return version


def sfcgal_full_version():
    """Returns the full version string of SFCGAL"""
    version = ffi.string(lib.sfcgal_full_version()).decode("utf-8")
    return version


def read_wkt(wkt):
    return wrap_geom(_read_wkt(wkt))


def _read_wkt(wkt):
    wkt = bytes(wkt, encoding="utf-8")
    return lib.sfcgal_io_read_wkt(wkt, len(wkt))


def write_wkt(geom, decim=-1):
    if isinstance(geom, Geometry):
        geom = geom._geom
    try:
        buf = ffi.new("char**")
        length = ffi.new("size_t*")
        if decim >= 0:
            lib.sfcgal_geometry_as_text_decim(geom, decim, buf, length)
        else:
            lib.sfcgal_geometry_as_text(geom, buf, length)
        wkt = ffi.string(buf[0], length[0]).decode("utf-8")
    finally:
        # we're responsible for free'ing the memory
        if not buf[0] == ffi.NULL:
            lib.free(buf[0])
    return wkt


class Geometry:
    _owned = True

    def distance(self, other):
        return lib.sfcgal_geometry_distance(self._geom, other._geom)

    def distance_3d(self, other):
        return lib.sfcgal_geometry_distance_3d(self._geom, other._geom)

    def area():
        def fget(self):
            return lib.sfcgal_geometry_area(self._geom)

        return locals()

    area = property(**area())

    def is_empty():
        def fget(self):
            return lib.sfcgal_geometry_is_empty(self._geom)

        return locals()

    is_empty = property(**is_empty())

    @property
    def has_z(self):
        return lib.sfcgal_geometry_is_3d(self._geom) == 1

    def convexhull(self):
        geom = lib.sfcgal_geometry_convexhull(self._geom)
        return wrap_geom(geom)

    def convexhull_3d(self):
        geom = lib.sfcgal_geometry_convexhull_3d(self._geom)
        return wrap_geom(geom)

    def difference(self, other):
        geom = lib.sfcgal_geometry_difference(self._geom, other._geom)
        return wrap_geom(geom)

    def intersects(self, other):
        return lib.sfcgal_geometry_intersects(self._geom, other._geom) == 1

    def intersects_3d(self, other):
        return lib.sfcgal_geometry_intersects_3d(self._geom, other._geom) == 1

    def intersection(self, other):
        geom = lib.sfcgal_geometry_intersection(self._geom, other._geom)
        return wrap_geom(geom)

    def intersection_3d(self, other):
        geom = lib.sfcgal_geometry_intersection_3d(self._geom, other._geom)
        return wrap_geom(geom)

    def union(self, other):
        geom = lib.sfcgal_geometry_union(self._geom, other._geom)
        return wrap_geom(geom)

    def union_3d(self, other):
        geom = lib.sfcgal_geometry_union_3d(self._geom, other._geom)
        return wrap_geom(geom)

    def covers(self, other):
        return lib.sfcgal_geometry_covers(self._geom, other._geom) == 1

    def triangulate_2dz(self):
        geom = lib.sfcgal_geometry_triangulate_2dz(self._geom)
        return wrap_geom(geom)

    def tessellate(self):
        tri = lib.sfcgal_geometry_triangulate_2dz(self._geom)
        geom = lib.sfcgal_geometry_intersection(self._geom, tri)

        return wrap_geom(geom)

    def force_lhr(self):
        geom = lib.sfcgal_geometry_force_lhr(self._geom)
        return wrap_geom(geom)

    def force_rhr(self):
        geom = lib.sfcgal_geometry_force_rhr(self._geom)
        return wrap_geom(geom)

    def is_valid(self):
        return lib.sfcgal_geometry_is_valid(self._geom) != 0

    def is_valid_detail(self):
        invalidity_reason = ffi.new("char **")
        invalidity_location = ffi.new("sfcgal_geometry_t **")
        lib.sfcgal_geometry_is_valid_detail(
            self._geom, invalidity_reason, invalidity_location
        )
        return (ffi.string(invalidity_reason[0]).decode("utf-8"), None)

    def round(self, r):
        geom = lib.sfcgal_geometry_round(self._geom, r)
        return wrap_geom(geom)

    def minkowski_sum(self, other):
        geom = lib.sfcgal_geometry_minkowski_sum(self._geom, other._geom)
        return wrap_geom(geom)

    def offset_polygon(self, radius):
        geom = lib.sfcgal_geometry_offset_polygon(self._geom, radius)
        return wrap_geom(geom)

    def straight_skeleton(self):
        geom = lib.sfcgal_geometry_straight_skeleton(self._geom)
        return wrap_geom(geom)

    def straight_skeleton_distance_in_m(self):
        geom = lib.sfcgal_geometry_straight_skeleton_distance_in_m(self._geom)
        return wrap_geom(geom)

    def approximate_medial_axis(self):
        geom = lib.sfcgal_geometry_approximate_medial_axis(self._geom)
        return wrap_geom(geom)

    def alpha_shapes(self, alpha=1, allow_holes=False):
        geom = lib.sfcgal_geometry_alpha_shapes(self._geom, alpha, allow_holes)
        return wrap_geom(geom)

    def optimal_alpha_shapes(self, allow_holes=False, nb_components=1):
        geom = lib.sfcgal_geometry_optimal_alpha_shapes(
            self._geom, allow_holes, nb_components
        )
        return wrap_geom(geom)

    def wkt():
        def fget(self):
            return write_wkt(self._geom)

        return locals()

    wkt = property(**wkt())

    def wktDecim(self, decim=8):
        return write_wkt(self._geom, decim)

    def __del__(self):
        if self._owned:
            # only free geometries owned by the class
            # this isn't the case when working with geometries contained by
            # a collection (e.g. a GeometryCollection)
            lib.sfcgal_geometry_delete(self._geom)


class Point(Geometry):
    def __init__(self, x, y, z=None):
        # TODO: support coordinates as a list
        if z is None:
            self._geom = point_from_coordinates([x, y])
        else:
            self._geom = point_from_coordinates([x, y, z])

    @property
    def x(self):
        return lib.sfcgal_point_x(self._geom)

    @property
    def y(self):
        return lib.sfcgal_point_y(self._geom)

    @property
    def z(self):
        if lib.sfcgal_geometry_is_3d(self._geom):
            return lib.sfcgal_point_z(self._geom)
        else:
            raise DimensionError("This point has no z coordinate.")


class LineString(Geometry):
    def __init__(self, coords):
        self._geom = linestring_from_coordinates(coords)

    def __len__(self):
        return lib.sfcgal_linestring_num_points(self._geom)

    @property
    def coords(self):
        return CoordinateSequence(self)


class Polygon(Geometry):
    def __init__(self, exterior, interiors=None):
        if interiors is None:
            interiors = []
        self._geom = polygon_from_coordinates(
            [
                exterior,
                *interiors,
            ]
        )


class CoordinateSequence:
    def __init__(self, parent):
        # keep reference to parent to avoid garbage collection
        self._parent = parent

    def __len__(self):
        return self._parent.__len__()

    def __iter__(self):
        length = self.__len__()
        for n in range(0, length):
            yield self.__get_coord_n(n)

    def __get_coord_n(self, n):
        point_n = lib.sfcgal_linestring_point_n(self._parent._geom, n)
        return point_to_coordinates(point_n)

    def __getitem__(self, key):
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_coord_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_coord_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )


class GeometryCollectionBase(Geometry):
    @property
    def geoms(self):
        return GeometrySequence(self)

    def __len__(self):
        return len(self.geoms)


class MultiPoint(GeometryCollectionBase):
    def __init__(self, coords=None):
        self._geom = multipoint_from_coordinates(coords)


class MultiLineString(GeometryCollectionBase):
    def __init__(self, coords=None):
        self._geom = multilinestring_from_coordinates(coords)


class MultiPolygon(GeometryCollectionBase):
    def __init__(self, coords=None):
        self._geom = multipolygon_from_coordinates(coords)


class Tin(GeometryCollectionBase):
    def __init__(self, coords=None):
        self._geom = tin_from_coordinates(coords)


class Triangle(GeometryCollectionBase):
    def __init__(self, coords=None):
        self._geom = triangle_from_coordinates(coords)

    @property
    def coords(self):
        return triangle_to_coordinates(self._geom)


class PolyhedralSurface(GeometryCollectionBase):
    def __init__(self, coords=None):
        self._geom = polyhedralsurface_from_coordinates(coords)


class GeometryCollection(GeometryCollectionBase):
    def __init__(self):
        self._geom = lib.sfcgal_geometry_collection_create()

    def addGeometry(self, geometry):
        clone = lib.sfcgal_geometry_clone(geometry._geom)
        lib.sfcgal_geometry_collection_add_geometry(self._geom, clone)


class GeometrySequence:
    def __init__(self, parent):
        # keep reference to parent to avoid garbage collection
        self._parent = parent

    def __iter__(self):
        for n in range(0, len(self)):
            yield wrap_geom(
                lib.sfcgal_geometry_collection_geometry_n(self._parent._geom, n),
                owned=False,
            )

    def __len__(self):
        return lib.sfcgal_geometry_collection_num_geometries(self._parent._geom)

    def __get_geometry_n(self, n):
        return wrap_geom(
            lib.sfcgal_geometry_collection_geometry_n(self._parent._geom, n),
            owned=False,
        )

    def __getitem__(self, key):
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )


def wrap_geom(geom, owned=True):
    geom_type_id = lib.sfcgal_geometry_type_id(geom)
    cls = geom_type_to_cls[geom_type_id]
    geometry = object.__new__(cls)
    geometry._geom = geom
    geometry._owned = owned
    return geometry


geom_type_to_cls = {
    lib.SFCGAL_TYPE_POINT: Point,
    lib.SFCGAL_TYPE_LINESTRING: LineString,
    lib.SFCGAL_TYPE_POLYGON: Polygon,
    lib.SFCGAL_TYPE_MULTIPOINT: MultiPoint,
    lib.SFCGAL_TYPE_MULTILINESTRING: MultiLineString,
    lib.SFCGAL_TYPE_MULTIPOLYGON: MultiPolygon,
    lib.SFCGAL_TYPE_GEOMETRYCOLLECTION: GeometryCollection,
    lib.SFCGAL_TYPE_TRIANGULATEDSURFACE: Tin,
    lib.SFCGAL_TYPE_TRIANGLE: Triangle,
    lib.SFCGAL_TYPE_POLYHEDRALSURFACE: PolyhedralSurface,
}


def shape(geometry):
    """Creates a PySFCGAL geometry from a GeoJSON-like geometry"""
    return wrap_geom(_shape(geometry))


def _shape(geometry):
    """Creates a SFCGAL geometry from a GeoJSON-like geometry"""
    geom_type = geometry["type"].lower()
    try:
        factory = factories_type_from_coords[geom_type]
    except KeyError:
        raise ValueError("Unknown geometry type: {}".format(geometry["type"]))
    if geom_type == "geometrycollection":
        geometries = geometry["geometries"]
        return factory(geometries)
    else:
        coordinates = geometry["coordinates"]
        return factory(coordinates)


def point_from_coordinates(coordinates):
    if len(coordinates) == 2:
        point = lib.sfcgal_point_create_from_xy(*coordinates)
    else:
        point = lib.sfcgal_point_create_from_xyz(*coordinates)
    return point


def linestring_from_coordinates(coordinates, close=False):
    linestring = lib.sfcgal_linestring_create()
    if coordinates:
        for coordinate in coordinates:
            point = point_from_coordinates(coordinate)
            lib.sfcgal_linestring_add_point(linestring, point)
        if close and coordinates[0] != coordinates[-1]:
            point = point_from_coordinates(coordinates[0])
            lib.sfcgal_linestring_add_point(linestring, point)
    return linestring


def triangle_from_coordinates(coordinates):
    triangle = None
    if coordinates and len(coordinates) == 3:
        triangle = lib.sfcgal_triangle_create_from_points(
            coordinates[0], coordinates[1], coordinates[2]
        )
    else:
        lib.sfcgal_triangle_create()

    return triangle


def polygon_from_coordinates(coordinates):
    exterior = linestring_from_coordinates(coordinates[0], True)
    polygon = lib.sfcgal_polygon_create_from_exterior_ring(exterior)
    for n in range(1, len(coordinates)):
        interior = linestring_from_coordinates(coordinates[n], True)
        lib.sfcgal_polygon_add_interior_ring(polygon, interior)
    return polygon


def multipoint_from_coordinates(coordinates):
    multipoint = lib.sfcgal_multi_point_create()
    if coordinates:
        for coords in coordinates:
            point = point_from_coordinates(coords)
            lib.sfcgal_geometry_collection_add_geometry(multipoint, point)
    return multipoint


def multilinestring_from_coordinates(coordinates):
    multilinestring = lib.sfcgal_multi_linestring_create()
    if coordinates:
        for coords in coordinates:
            linestring = linestring_from_coordinates(coords)
            lib.sfcgal_geometry_collection_add_geometry(multilinestring, linestring)
    return multilinestring


def multipolygon_from_coordinates(coordinates):
    multipolygon = lib.sfcgal_multi_polygon_create()
    if coordinates:
        for coords in coordinates:
            polygon = polygon_from_coordinates(coords)
            lib.sfcgal_geometry_collection_add_geometry(multipolygon, polygon)
    return multipolygon


def tin_from_coordinates(coordinates):
    tin = lib.sfcgal_triangulated_surface_create()
    if coordinates:
        for coords in coordinates:
            triangle = triangle_from_coordinates(coords)
            lib.sfcgal_tringulated_surface_add_trianle(tin, triangle)
    return tin


def geometry_collection_from_coordinates(geometries):
    collection = lib.sfcgal_geometry_collection_create()
    for geometry in geometries:
        geom = _shape(geometry)
        lib.sfcgal_geometry_collection_add_geometry(collection, geom)
    return collection


def polyhedralsurface_from_coordinates(coordinates):
    polyhedralsurface = lib.sfcgal_polyhedral_surface_create()
    if coordinates:
        for coords in coordinates:
            polygon = polygon_from_coordinates(coords)
            lib.sfcgal_polyhedral_surface_add_polygon(polyhedralsurface, polygon)
    return polyhedralsurface


factories_type_from_coords = {
    "point": point_from_coordinates,
    "linestring": linestring_from_coordinates,
    "polygon": polygon_from_coordinates,
    "multipoint": multipoint_from_coordinates,
    "multilinestring": multilinestring_from_coordinates,
    "multipolygon": multipolygon_from_coordinates,
    "geometrycollection": geometry_collection_from_coordinates,
    "TIN": multipolygon_from_coordinates,
    "PolyhedralSurface": polyhedralsurface_from_coordinates,
    "Triangle": triangle_from_coordinates,
}

geom_types = {
    "Point": lib.SFCGAL_TYPE_POINT,
    "LineString": lib.SFCGAL_TYPE_LINESTRING,
    "Polygon": lib.SFCGAL_TYPE_POLYGON,
    "MultiPoint": lib.SFCGAL_TYPE_MULTIPOINT,
    "MultiLineString": lib.SFCGAL_TYPE_MULTILINESTRING,
    "MultiPolygon": lib.SFCGAL_TYPE_MULTIPOLYGON,
    "GeometryCollection": lib.SFCGAL_TYPE_GEOMETRYCOLLECTION,
    "TIN": lib.SFCGAL_TYPE_TRIANGULATEDSURFACE,
    "Triangle": lib.SFCGAL_TYPE_TRIANGLE,
    "PolyhedralSurface": lib.SFCGAL_TYPE_POLYHEDRALSURFACE,
}
geom_types_r = dict((v, k) for k, v in geom_types.items())


def mapping(geometry):
    geom_type_id = lib.sfcgal_geometry_type_id(geometry._geom)
    try:
        geom_type = geom_types_r[geom_type_id]
    except KeyError:
        raise ValueError("Unknown geometry type: {}".format(geom_type_id))
    if geom_type == "GeometryCollection":
        ret = {
            "type": geom_type,
            "geometries": factories_type_to_coords[geom_type](geometry._geom),
        }
    else:
        ret = {
            "type": geom_type,
            "coordinates": factories_type_to_coords[geom_type](geometry._geom),
        }
    return ret


def point_to_coordinates(geometry):
    x = lib.sfcgal_point_x(geometry)
    y = lib.sfcgal_point_y(geometry)
    if lib.sfcgal_geometry_is_3d(geometry):
        z = lib.sfcgal_point_z(geometry)
        return (x, y, z)
    else:
        return (x, y)


def linestring_to_coordinates(geometry):
    num_points = lib.sfcgal_linestring_num_points(geometry)
    coords = []
    for n in range(0, num_points):
        point = lib.sfcgal_linestring_point_n(geometry, n)
        coords.append(point_to_coordinates(point))
    return coords


def polygon_to_coordinates(geometry):
    coords = []
    exterior = lib.sfcgal_polygon_exterior_ring(geometry)
    coords.append(linestring_to_coordinates(exterior))
    num_interior = lib.sfcgal_polygon_num_interior_rings(geometry)
    for n in range(0, num_interior):
        interior = lib.sfcgal_polygon_interior_ring_n(geometry, n)
        coords.append(linestring_to_coordinates(interior))
    return coords


def multipoint_to_coordinates(geometry):
    num_geoms = lib.sfcgal_geometry_collection_num_geometries(geometry)
    coords = []
    for n in range(0, num_geoms):
        point = lib.sfcgal_geometry_collection_geometry_n(geometry, n)
        coords.append(point_to_coordinates(point))
    return coords


def multilinestring_to_coordinates(geometry):
    num_geoms = lib.sfcgal_geometry_collection_num_geometries(geometry)
    coords = []
    for n in range(0, num_geoms):
        linestring = lib.sfcgal_geometry_collection_geometry_n(geometry, n)
        coords.append(linestring_to_coordinates(linestring))
    return coords


def multipolygon_to_coordinates(geometry):
    num_geoms = lib.sfcgal_geometry_collection_num_geometries(geometry)
    coords = []
    for n in range(0, num_geoms):
        polygon = lib.sfcgal_geometry_collection_geometry_n(geometry, n)
        coords.append(polygon_to_coordinates(polygon))
    return coords


def geometrycollection_to_coordinates(geometry):
    num_geoms = lib.sfcgal_geometry_collection_num_geometries(geometry)
    geoms = []
    for n in range(0, num_geoms):
        geom = lib.sfcgal_geometry_collection_geometry_n(geometry, n)
        geom_type_id = lib.sfcgal_geometry_type_id(geom)
        geom_type = geom_types_r[geom_type_id]
        coords = factories_type_to_coords[geom_type](geom)
        geoms.append({"type": geom_type, "coordinates": coords})
    return geoms


def triangle_to_coordinates(geometry):
    coords = []
    for n in range(0, 3):
        point = lib.sfcgal_triangle_vertex(geometry, n)
        coords.append(point_to_coordinates(point))
    return coords


def tin_to_coordinates(geometry):
    num_geoms = lib.sfcgal_triangulated_surface_num_triangles(geometry)
    coords = []
    for n in range(0, num_geoms):
        triangle = lib.sfcgal_triangulated_surface_triangle_n(geometry, n)
        coords.append(triangle_to_coordinates(triangle))
    return coords


def polyhedralsurface_to_coordinates(geometry):
    num_geoms = lib.sfcgal_polyhedral_surface_num_polygons(geometry)
    coords = []
    for n in range(0, num_geoms):
        polygon = lib.sfcgal_polyhedral_surface_polygon_n(geometry, n)
        coords.append(polygon_to_coordinates(polygon))
    return coords


factories_type_to_coords = {
    "Point": point_to_coordinates,
    "LineString": linestring_to_coordinates,
    "Polygon": polygon_to_coordinates,
    "MultiPoint": multipoint_to_coordinates,
    "MultiLineString": multilinestring_to_coordinates,
    "MultiPolygon": multipolygon_to_coordinates,
    "GeometryCollection": geometrycollection_to_coordinates,
    "Triangle": triangle_to_coordinates,
    "TIN": tin_to_coordinates,
    "PolyhedralSurface": polyhedralsurface_to_coordinates,
}


def triangle_to_polygon(geometry, wrapped=False):
    exterior = lib.sfcgal_linestring_create()
    for n in range(0, 4):
        lib.sfcgal_linestring_add_point(
            exterior, lib.sfcgal_triangle_vertex(geometry, n)
        )
    polygon = lib.sfcgal_polygon_create_from_exterior_ring(exterior)
    return wrap_geom(polygon) if wrapped else polygon


def tin_to_multipolygon(geometry, wrapped=False):
    multipolygon = lib.sfcgal_multi_polygon_create()
    num_geoms = lib.sfcgal_triangulated_surface_num_triangles(geometry)
    for n in range(0, num_geoms):
        polygon = triangle_to_polygon(
            lib.sfcgal_triangulated_surface_triangle_n(geometry, n)
        )
        lib.sfcgal_geometry_collection_add_geometry(multipolygon, polygon)
    return wrap_geom(multipolygon) if wrapped else multipolygon
