# -*- mode: python; coding: utf-8 -*-
# Copyright 2013-2021 Chris Beaumont and the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""Computations for the TOAST projection scheme and tile pyramid format.

For all TOAST maps, the north pole is in the dead center of the virtual image
square, the south pole is at all four of its corners, and the equator is a
diamond connecting the midpoints of the four sides of the square. (See Figure 3
of McGlynn+ 2019, DOI:10.3847/1538-4365/aaf79e).

For TOAST maps of the sky, the line of RA (lon) = 0 in the northern hemisphere
extends from the center of the square to the right, as in the Figure 3 mentioned
above. The RA = 90 line goes from the center up, and so on counter-clockwise
around the square.

For TOAST planetary maps, the lon = 0 line in the northern hemisphere extends
from the center of the square to the *left*. The lon = 90 line extends
downwards, and increasing longitude results in counter-clockwise motion around
the square as for sky maps. In other words, the longitudinal orientation is
rotated by 180 degrees.

"""
from __future__ import absolute_import, division, print_function

__all__ = '''
count_tiles_matching_filter
create_single_tile
generate_tiles
generate_tiles_filtered
sample_layer
sample_layer_filtered
Tile
ToastCoordinateSystem
toast_pixel_for_point
toast_tile_area
toast_tile_for_point
toast_tile_get_coords
'''.split()

from collections import namedtuple
from enum import Enum
import numpy as np
from tqdm import tqdm

from ._libtoasty import subsample, mid
from .image import Image
from .pyramid import Pos, tiles_at_depth

HALFPI = 0.5 * np.pi
THREEHALFPI = 1.5 * np.pi
TWOPI = 2 * np.pi


def _arclength(lat1, lon1, lat2, lon2):
    """Compute the length of an arc along the great circle defined by spherical
    latitude and longitude coordinates. Inputs and return value are all in
    radians.

    """
    c = np.sin(lat1) * np.sin(lat2) + np.cos(lon1 - lon2) * np.cos(lat1) * np.cos(lat2)
    return np.arccos(c)


def _spherical_triangle_area(lat1, lon1, lat2, lon2, lat3, lon3):
    """Compute the area of the specified spherical triangle in steradians. Inputs
    are in radians. From https://math.stackexchange.com/a/66731 . My initial
    implementation used unit vectors on the sphere instead of latitudes and
    longitudes; there might be a faster way to do things in lat/lon land.

    """
    c = _arclength(lat1, lon1, lat2, lon2)
    a = _arclength(lat2, lon2, lat3, lon3)
    b = _arclength(lat3, lon3, lat1, lon1)
    s = 0.5 * (a + b + c)
    tane4 = np.sqrt(np.tan(0.5 * s) * np.tan(0.5 * (s - a)) * np.tan(0.5 * (s - b)) * np.tan(0.5 * (s - c)))
    e = 4 * np.arctan(tane4)
    return e


class ToastCoordinateSystem(Enum):
    """
    Different TOAST coordinate systems that are in use.
    """

    ASTRONOMICAL = 'astronomical'
    """The default TOAST coordinate system, where the ``lat = lon = 0`` point
    lies at the middle right edge of the TOAST projection square."""

    PLANETARY = 'planetary'
    """The planetary TOAST coordinate system. This is rotated 180 degrees in
    longitude from the astronomical system, such that the ``lat = lon = 0``
    point lies at the middle left edge of the TOAST projection square."""


Tile = namedtuple('Tile', 'pos corners increasing')

_level1_astronomical_lonlats = np.radians([
    [(0, -90), (90, 0), (0, 90), (180, 0)],
    [(90, 0), (0, -90), (0, 0), (0, 90)],
    [(180, 0), (0, 90), (270, 0), (0, -90)],
    [(0, 90), (0, 0), (0, -90), (270, 0)],
])
_level1_astronomical_lonlats.flags.writeable = False


def _create_level1_tiles(coordsys):
    lonlats = _level1_astronomical_lonlats

    if coordsys == ToastCoordinateSystem.PLANETARY:
        lonlats = lonlats.copy()
        lonlats[...,0] = (lonlats[...,0] + np.pi) % TWOPI

    return [
        Tile(Pos(n=1, x=0, y=0), lonlats[0], True),
        Tile(Pos(n=1, x=1, y=0), lonlats[1], False),
        Tile(Pos(n=1, x=0, y=1), lonlats[2], False),
        Tile(Pos(n=1, x=1, y=1), lonlats[3], True),
    ]


def toast_tile_area(tile):
    """Calculate the area of a TOAST tile in steradians.

    Parameters
    ----------
    tile : :class:`Tile`
        A TOAST tile.

    Returns
    -------
    The area of the tile in steradians.

    Notes
    -----
    This computation is not very fast.

    """
    ul, ur, lr, ll = tile.corners

    if tile.increasing:
        a1 = _spherical_triangle_area(ul[1], ul[0], ur[1], ur[0], ll[1], ll[0])
        a2 = _spherical_triangle_area(ur[1], ur[0], lr[1], lr[0], ll[1], ll[0])
    else:
        a1 = _spherical_triangle_area(ul[1], ul[0], ur[1], ur[0], lr[1], lr[0])
        a2 = _spherical_triangle_area(ul[1], ul[0], ll[1], ll[0], lr[1], lr[0])

    return a1 + a2


def _equ_to_xyz(lat, lon):
    """
    Convert equatorial to cartesian coordinates. Lat and lon are in radians.
    Output is on the unit sphere.

    """
    clat = np.cos(lat)
    return np.array([
        np.cos(lon) * clat,
        np.sin(lat),
        np.sin(lon) * clat,
    ])


def _left_of_half_space_score(point_a, point_b, test_point):
    """
    A variant of WWT Window's IsLeftOfHalfSpace.

    When determining which tile a given RA/Dec lives in, it is inevitable that
    rounding errors can make seem that certain coordinates are not contained by
    *any* tile. Unlike IsLeftOfHalf space, which returns a boolean based on the
    dot product calculated here, we return a number <= 0, where 0 indicates that
    the test point is *definitely* in the left half-space defined by the A and B
    points. Negative values tell us how far into the right space the point is;
    when rounding errors are biting us, that value might be something like
    -1e-16.

    """
    return min(np.dot(np.cross(point_a, point_b), test_point), 0)


def _toast_tile_containment_score(tile, lat, lon):
    """
    Assess whether a TOAST tile contains a given point.

    Parameters
    ----------
    tile : :class:`Tile`
        A TOAST tile
    lat : number
        The latitude (declination) of the point, in radians.
    lon : number
        The longitude (RA) of the point, in radians. This value must
        have already been normalied to lie within the range [0, 2pi]
        (inclusive on both ends.)

    Returns
    -------
    A floating-point "containment score" number. If this number is zero, the
    point definitely lies within the tile. Otherwise, the number will be
    negative, with more negative values indicating a greater distance from the
    point to the nearest tile boundary. Due to inevitable roundoff errors, there
    are situations where, given a certain point and tile, the point "should" be
    contained in the tile, but due to roundoff errors, its score will not be
    exactly zero.

    """
    # Derived from ToastTile.IsPointInTile.

    if tile.pos.n == 0:
        return 0

    # Note that our labeling scheme is different than that used in WWT proper.
    if tile.pos.n == 1:
        if lon >= 0 and lon <= HALFPI and tile.pos.x == 1 and tile.pos.y == 0:
            return 0
        if lon > HALFPI and lon <= np.pi and tile.pos.x == 0 and tile.pos.y == 0:
            return 0
        if lon > np.pi and lon < THREEHALFPI and tile.pos.x == 0 and tile.pos.y == 1:
            return 0
        if lon >= THREEHALFPI and lon <= TWOPI and tile.pos.x == 1 and tile.pos.y == 1:
            return 0
        return -100

    test_point = _equ_to_xyz(lat, lon)
    ul = _equ_to_xyz(tile.corners[0][1], tile.corners[0][0])
    ur = _equ_to_xyz(tile.corners[1][1], tile.corners[1][0])
    lr = _equ_to_xyz(tile.corners[2][1], tile.corners[2][0])
    ll = _equ_to_xyz(tile.corners[3][1], tile.corners[3][0])

    upper = _left_of_half_space_score(ul, ur, test_point)
    right = _left_of_half_space_score(ur, lr, test_point)
    lower = _left_of_half_space_score(lr, ll, test_point)
    left = _left_of_half_space_score(ll, ul, test_point)
    return upper + right + lower + left


def toast_tile_for_point(depth, lat, lon, coordsys=ToastCoordinateSystem.ASTRONOMICAL):
    """
    Identify the TOAST tile at a given depth that contains the given point.

    Parameters
    ----------
    depth : non-negative integer
        The TOAST tile pyramid depth to drill down to. For any given depth,
        there exists a tile containing the input point. As the depth gets
        larger, the precision of the location gets more precise.
    lat : number
        The latitude (declination) of the point, in radians.
    lon : number
        The longitude (RA) of the point, in radians. This value must
        have already been normalized to lie within the range [0, 2pi]
        (inclusive on both ends.)
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.

    Returns
    -------
    The :class:`Tile` at the given depth that best contains the specified
    point.

    """
    lon = lon % TWOPI

    if depth == 0:
        return Tile(Pos(n=0, x=0, y=0), (None, None, None, None), False)

    for tile in _create_level1_tiles(coordsys):
        if _toast_tile_containment_score(tile, lat, lon) == 0.:
            break

    while tile.pos.n < depth:
        # Due to inevitable roundoff errors in the tile construction process, it
        # can arise that we find that the point is contained in a certain tile
        # but not contained in any of its children. We deal with this reality by
        # using the "containment score" rather than a binary in/out
        # classification. If no sub-tile has a containment score of zero, we
        # choose whichever tile has the least negative score. In typical
        # roundoff situations that score will be something like -1e-16.
        best_score = -np.inf

        for child in _div4(tile):
            score = _toast_tile_containment_score(child, lat, lon)

            if score == 0.:
                tile = child
                break

            if score > best_score:
                tile = child
                best_score = score

    return tile


def toast_tile_get_coords(tile):
    """
    Get the coordinates of the pixel centers of a TOAST Tile.

    Parameters
    ----------
    tile : :class:`Tile`
        A TOAST tile

    Returns
    -------
    A tuple ``(lons, lats)``, each of which is a 256x256 array of longitudes and
    latitudes of the tile pixel centers, in radians.
    """

    return subsample(
        tile.corners[0],
        tile.corners[1],
        tile.corners[2],
        tile.corners[3],
        256,
        tile.increasing,
    )


def toast_pixel_for_point(depth, lat, lon, coordsys=ToastCoordinateSystem.ASTRONOMICAL):
    """
    Identify the pixel within a TOAST tile at a given depth that contains the
    given point.

    Parameters
    ----------
    depth : non-negative integer
        The TOAST tile pyramid depth to drill down to. For any given depth,
        there exists a tile containing the input point. As the depth gets
        larger, the precision of the location gets more precise.
    lat : number
        The latitude (declination) of the point, in radians.
    lon : number
        The longitude (RA) of the point, in radians. This value must
        have already been normalized to lie within the range [0, 2pi]
        (inclusive on both ends.)
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.

    Returns
    -------
    A tuple ``(tile, x, y)``. The *tile* is the :class:`Tile` at the given depth
    that best contains the specified point. The *x* and *y* values are
    floating-point numbers giving the pixel location within the 256×256 tile.
    The returned values are derived from a quadratic fit to the TOAST
    coordinates of the pixels nearest the specified coordinates *lat* and *lon*.

    """
    tile = toast_tile_for_point(depth, lat, lon, coordsys=coordsys)

    # Now that we have the tile, get its pixel locations and identify the pixel
    # that is closest to the input position.

    lons, lats = toast_tile_get_coords(tile)
    dist2 = (lons - lon)**2 + (lats - lat)**2
    min_y, min_x = np.unravel_index(np.argmin(dist2), (256, 256))

    # Now, identify a postage stamp around that best-fit pixel and fit a biquadratic
    # mapping lat/lon to y/x.

    halfsize = 4
    x0 = max(min_x - halfsize, 0)
    y0 = max(min_y - halfsize, 0)
    x1 = min(min_x + halfsize + 1, 256)
    y1 = min(min_y + halfsize + 1, 256)

    dist2_stamp = dist2[y0:y1,x0:x1]
    lons_stamp = lons[y0:y1,x0:x1]
    lats_stamp = lats[y0:y1,x0:x1]

    flat_lons = lons_stamp.flatten()
    flat_lats = lats_stamp.flatten()

    A = np.array([
        flat_lons * 0 + 1,
        flat_lons,
        flat_lats,
        flat_lons**2,
        flat_lons * flat_lats,
        flat_lats**2,
    ]).T

    ygrid, xgrid = np.indices(dist2_stamp.shape)
    x_coeff, _r, _rank, _s = np.linalg.lstsq(A, xgrid.flatten(), rcond=None)
    y_coeff, _r, _rank, _s = np.linalg.lstsq(A, ygrid.flatten(), rcond=None)

    # Evaluate the polynomial to get the refined pixel coordinates.

    pt = np.array([
        1,
        lon,
        lat,
        lon**2,
        lon * lat,
        lat**2,
    ])
    x = np.dot(x_coeff, pt)
    y = np.dot(y_coeff, pt)
    return tile, x0 + x, y0 + y


def _postfix_corner(tile, depth, filter, bottom_only):
    """
    Yield subtiles of a given tile, in postfix (deepest-first) order.

    Parameters
    ----------
    tile : Tile
        Parameters of the current tile.
    depth : int
        The depth to descend to.
    filter : function(Tile)->bool
        A filter function; only tiles for which the function returns True will
        be investigated.
    bottom_only : bool
        If True, only yield tiles at max_depth.

    """
    n = tile[0].n
    if n > depth:
        return

    if n > 1 and not filter(tile):
        return

    for child in _div4(tile):
        for item in _postfix_corner(child, depth, filter, bottom_only):
            yield item

    if n == depth or not bottom_only:
        yield tile


def _div4(tile):
    """Return the four child tiles of an input tile."""
    n, x, y = tile.pos.n, tile.pos.x, tile.pos.y
    ul, ur, lr, ll = tile.corners
    increasing = tile.increasing

    to = mid(ul, ur)
    ri = mid(ur, lr)
    bo = mid(lr, ll)
    le = mid(ll, ul)
    ce = mid(ll, ur) if increasing else mid(ul, lr)

    n += 1
    x *= 2
    y *= 2

    return [
        Tile(Pos(n=n, x=x,     y=y    ), (ul, to, ce, le), increasing),
        Tile(Pos(n=n, x=x + 1, y=y    ), (to, ur, ri, ce), increasing),
        Tile(Pos(n=n, x=x,     y=y + 1), (le, ce, bo, ll), increasing),
        Tile(Pos(n=n, x=x + 1, y=y + 1), (ce, ri, lr, bo), increasing),
    ]


def create_single_tile(pos, coordsys=ToastCoordinateSystem.ASTRONOMICAL):
    """
    Create a single TOAST tile.

    Parameters
    ----------
    pos : :class:`~toasty.pyramid.Pos`
        The position of the tile that will be created. The depth of the
        tile must be at least 1.
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.

    Returns
    -------
    :class:`Tile`

    Notes
    -----
    This function should only be used for one-off investigations and debugging.
    It is much more efficient to use :func:`generate_tiles` for bulk computations.
    """

    if pos.n == 0:
        raise ValueError('cannot create a Tile for the n=0 tile')

    children = _create_level1_tiles(coordsys)
    cur_n = 0

    while True:
        cur_n += 1
        ix = (pos.x >> (pos.n - cur_n)) & 0x1
        iy = (pos.y >> (pos.n - cur_n)) & 0x1
        tile = children[iy * 2 + ix]

        if cur_n == pos.n:
            return tile

        children = _div4(tile)


def generate_tiles(depth, bottom_only=True, coordsys=ToastCoordinateSystem.ASTRONOMICAL):
    """Generate a pyramid of TOAST tiles in deepest-first order.

    Parameters
    ----------
    depth : int
        The tile depth to recurse to.
    bottom_only : bool
        If True, then only the lowest tiles will be yielded.
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.

    Yields
    ------
    tile : Tile
        An individual tile to process. Tiles are yielded deepest-first.

    The ``n = 0`` depth is not included.

    """
    return generate_tiles_filtered(depth, lambda t: True, bottom_only, coordsys=coordsys)


def generate_tiles_filtered(depth, filter, bottom_only=True, coordsys=ToastCoordinateSystem.ASTRONOMICAL):
    """Generate a pyramid of TOAST tiles in deepest-first order, filtering out subtrees.

    Parameters
    ----------
    depth : int
        The tile depth to recurse to.
    filter : function(Tile)->bool
        A filter function; only tiles for which the function returns True will
        be investigated.
    bottom_only : optional bool
        If True, then only the lowest tiles will be yielded.
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.

    Yields
    ------
    tile : Tile
        An individual tile to process. Tiles are yielded deepest-first.

    The ``n = 0`` depth is not included.

    """
    for t in _create_level1_tiles(coordsys):
        for item in _postfix_corner(t, depth, filter, bottom_only):
            yield item


def count_tiles_matching_filter(depth, filter, bottom_only=True, coordsys=ToastCoordinateSystem.ASTRONOMICAL):
    """
    Count the number of tiles matching a filter.

    Parameters
    ----------
    depth : int
        The tile depth to recurse to.
    filter : function(Tile)->bool
        A filter function; only tiles for which the function returns True will
        be investigated.
    bottom_only : bool
        If True, then only the lowest tiles will be processed.
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.

    Returns
    ------
    The number of tiles matching the filter. Even if ``bottom_only`` is false,
    the ``n = 0`` tile is not counted.

    Notes
    -----
    This function's call signature and tree-exploration semantics match
    :func:`generate_tiles_filtered`.
    """
    # With a generic filter function, brute force is our only option:
    n = 0

    for _tile in generate_tiles_filtered(depth, filter, bottom_only=bottom_only, coordsys=coordsys):
        n += 1

    return n


def sample_layer(
    pio,
    sampler,
    depth,
    coordsys=ToastCoordinateSystem.ASTRONOMICAL,
    format=None,
    parallel=None,
    cli_progress=False,
):
    """Generate a layer of the TOAST tile pyramid through direct sampling.

    Parameters
    ----------
    pio : :class:`toasty.pyramid.PyramidIO`
        A :class:`~toasty.pyramid.PyramidIO` instance to manage the I/O with
        the tiles in the tile pyramid.
    sampler : callable
        The sampler callable that will produce data for tiling.
    depth : int
        The depth of the layer of the TOAST tile pyramid to generate. The
        number of tiles in each layer is ``4**depth``. Each tile is 256×256
        TOAST pixels, so the resolution of the pixelization at which the
        data will be sampled is a refinement level of ``2**(depth + 8)``.
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.
    format : optional :class:`str`
        If provided, override the default data storage format of *pio* with the
        named format, one of the values in ``toasty.image.SUPPORTED_FORMATS``.
    parallel : integer or None (the default)
        The level of parallelization to use. If unspecified, defaults to using
        all CPUs. If the OS does not support fork-based multiprocessing,
        parallel processing is not possible and serial processing will be
        forced. Pass ``1`` to force serial processing.
    cli_progress : optional boolean, defaults False
        If true, a progress bar will be printed to the terminal using tqdm.
    """

    from .par_util import resolve_parallelism
    parallel = resolve_parallelism(parallel)

    if parallel > 1:
        _sample_layer_parallel(pio, format, sampler, depth, coordsys, cli_progress, parallel)
    else:
        _sample_layer_serial(pio, format, sampler, depth, coordsys, cli_progress)


def _sample_layer_serial(pio, format, sampler, depth, coordsys, cli_progress):
    with tqdm(total=tiles_at_depth(depth), disable=not cli_progress) as progress:
        for tile in generate_tiles(depth, bottom_only=True, coordsys=coordsys):
            lon, lat = toast_tile_get_coords(tile)
            sampled_data = sampler(lon, lat)
            pio.write_image(tile.pos, Image.from_array(sampled_data), format=format)
            progress.update(1)

    if cli_progress:
        print()


def _sample_layer_parallel(pio, format, sampler, depth, coordsys, cli_progress, parallel):
    import multiprocessing as mp

    done_event = mp.Event()
    queue = mp.Queue(maxsize = 2 * parallel)
    workers = []

    for _ in range(parallel):
        w = mp.Process(target=_mp_sample_worker, args=(queue, done_event, pio, sampler, format))
        w.daemon = True
        w.start()
        workers.append(w)

    # Send out tiles:

    with tqdm(total=tiles_at_depth(depth), disable=not cli_progress) as progress:
        for tile in generate_tiles(depth, bottom_only=True, coordsys=coordsys):
            queue.put(tile)
            progress.update(1)

    # OK, we're done!

    queue.close()
    queue.join_thread()
    done_event.set()

    for w in workers:
        w.join()

    if cli_progress:
        print()


def _mp_sample_worker(queue, done_event, pio, sampler, format):
    """
    Process tiles on the queue.
    """
    from queue import Empty

    while True:
        try:
            tile = queue.get(True, timeout=1)
        except Empty:
            if done_event.is_set():
                break
            continue

        lon, lat = toast_tile_get_coords(tile)
        sampled_data = sampler(lon, lat)
        pio.write_image(tile.pos, Image.from_array(sampled_data), format=format)


def sample_layer_filtered(
    pio,
    tile_filter,
    sampler,
    depth,
    coordsys=ToastCoordinateSystem.ASTRONOMICAL,
    parallel=None,
    cli_progress=False,
):
    """Populate a subset of a layer of the TOAST tile pyramid through direct sampling.

    Parameters
    ----------
    pio : :class:`toasty.pyramid.PyramidIO`
        A :class:`~toasty.pyramid.PyramidIO` instance to manage the I/O with
        the tiles in the tile pyramid.
    tile_filter : callable
        A tile filtering function, suitable for passing to
        :func:`toasty.toast.generate_tiles_filtered`.
    sampler : callable
        The sampler callable that will produce data for tiling.
    depth : int
        The depth of the layer of the TOAST tile pyramid to generate. The
        number of tiles in each layer is ``4**depth``. Each tile is 256×256
        TOAST pixels, so the resolution of the pixelization at which the
        data will be sampled is a refinement level of ``2**(depth + 8)``.
    coordsys : optional :class:`ToastCoordinateSystem`
        The TOAST coordinate system to use. Default is
        :attr:`ToastCoordinateSystem.ASTRONOMICAL`.
    parallel : integer or None (the default)
        The level of parallelization to use. If unspecified, defaults to using
        all CPUs. If the OS does not support fork-based multiprocessing,
        parallel processing is not possible and serial processing will be
        forced. Pass ``1`` to force serial processing.
    cli_progress : optional boolean, defaults False
        If true, a progress bar will be printed to the terminal using tqdm.
    """

    from .par_util import resolve_parallelism
    parallel = resolve_parallelism(parallel)

    if parallel > 1:
        _sample_filtered_parallel(pio, tile_filter, sampler, depth, coordsys, cli_progress, parallel)
    else:
        _sample_filtered_serial(pio, tile_filter, sampler, depth, coordsys, cli_progress)


def _sample_filtered_serial(pio, tile_filter, sampler, depth, coordsys, cli_progress):
    n_todo = count_tiles_matching_filter(depth, tile_filter, bottom_only=True, coordsys=coordsys)

    with tqdm(total=n_todo, disable=not cli_progress) as progress:
        for tile in generate_tiles_filtered(depth, tile_filter, bottom_only=True, coordsys=coordsys):
            lon, lat = toast_tile_get_coords(tile)
            sampled_data = sampler(lon, lat)
            img = Image.from_array(sampled_data)

            with pio.update_image(tile.pos, masked_mode=img.mode, default='masked') as basis:
                img.update_into_maskable_buffer(basis, slice(None), slice(None), slice(None), slice(None))

            progress.update(1)

    if cli_progress:
        print()

    # do not clean lockfiles, for HPC contexts where we're processing different
    # chunks in parallel.


def _sample_filtered_parallel(pio, tile_filter, sampler, depth, coordsys, cli_progress, parallel):
    import multiprocessing as mp

    n_todo = count_tiles_matching_filter(depth, tile_filter, bottom_only=True, coordsys=coordsys)

    done_event = mp.Event()
    queue = mp.Queue(maxsize = 2 * parallel)
    workers = []

    for _ in range(parallel):
        w = mp.Process(target=_mp_sample_filtered, args=(queue, done_event, pio, sampler))
        w.daemon = True
        w.start()
        workers.append(w)

    # Here we go:

    with tqdm(total=n_todo, disable=not cli_progress) as progress:
        for tile in generate_tiles_filtered(depth, tile_filter, bottom_only=True, coordsys=coordsys):
            queue.put(tile)
            progress.update(1)

    # OK, we're done!

    queue.close()
    queue.join_thread()
    done_event.set()

    for w in workers:
        w.join()

    if cli_progress:
        print()

    # do not clean lockfiles, for HPC contexts where we're processing different
    # chunks in parallel.


def _mp_sample_filtered(queue, done_event, pio, sampler):
    """
    Process tiles on the queue.

    We use ``pio.update_image`` in case we are in an HPC-type context where
    other chunks may be trying to write out the populate the same tiles as us at
    the same time.
    """

    from queue import Empty

    while True:
        try:
            tile = queue.get(True, timeout=1)
        except Empty:
            if done_event.is_set():
                break
            continue

        lon, lat = toast_tile_get_coords(tile)
        sampled_data = sampler(lon, lat)
        img = Image.from_array(sampled_data)

        with pio.update_image(tile.pos, masked_mode=img.mode, default='masked') as basis:
            img.update_into_maskable_buffer(basis, slice(None), slice(None), slice(None), slice(None))
