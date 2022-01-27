# -*- mode: python; coding: utf-8 -*-
# Copyright 2013-2022 Chris Beaumont and the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
“Sampler” functions that fetch image data as a function of sky coordinates.

The Sampler Protocol
--------------------

A sampler is a callable object that obeys the following signature: ``func(lon,
lat) -> data``, where *lon* and *lat* are 2D numpy arrays of spherical
coordinates measured in radians, and the returned *data* array is a numpy
array of at least two dimensions whose first two axes have the same shape as
*lon* and *lat*. The *data* array gives the map values sampled at the
corresponding coordinates. Its additional dimensions can be used to encode
color information: one standard is for *data* to have a dtype of
``np.uint8`` and a shape of ``(ny, nx, 3)``, where the final axis samples
RGB colors.

"""
from __future__ import absolute_import, division, print_function

__all__ = """
ChunkedPlateCarreeSampler
plate_carree_sampler
plate_carree_galactic_sampler
plate_carree_ecliptic_sampler
plate_carree_planet_sampler
plate_carree_planet_zeroleft_sampler
plate_carree_zeroright_sampler
healpix_fits_file_sampler
healpix_sampler
""".split()

import numpy as np


def healpix_sampler(data, nest=False, coord="C", interpolation="nearest"):
    """Create a sampler for HEALPix image data.

    Parameters
    ----------
    data : array
        The HEALPix data
    nest : bool (default: False)
        Whether the data is ordered in the nested HEALPix style
    coord : 'C' | 'G'
        Whether the image is in Celestial (C) or Galactic (G) coordinates
    interpolation : 'nearest' | 'bilinear'
        What interpolation scheme to use.

        WARNING: bilinear uses healpy's get_interp_val, which seems prone to segfaults

    Returns
    -------
    A function that samples the HEALPix data; the call signature is
    ``vec2pix(lon, lat) -> data``, where the inputs and output are 2D arrays
    and *lon* and *lat* are in radians.

    """
    from healpy import ang2pix, get_interp_val, npix2nside
    from astropy.coordinates import Galactic, ICRS
    import astropy.units as u

    interp_opts = ["nearest", "bilinear"]
    if interpolation not in interp_opts:
        raise ValueError(
            "Invalid interpolation %s. Must be one of %s" % (interpolation, interp_opts)
        )
    if coord.upper() not in "CG":
        raise ValueError("Invalid coord %s. Must be 'C' or 'G'" % coord)

    galactic = coord.upper() == "G"
    interp = interpolation == "bilinear"
    nside = npix2nside(data.size)

    def vec2pix(l, b):
        if galactic:
            f = ICRS(l * u.rad, b * u.rad)
            g = f.transform_to(Galactic)
            l, b = g.l.rad, g.b.rad

        theta = np.pi / 2 - b
        phi = l

        if interp:
            return get_interp_val(data, theta, phi, nest=nest)

        return data[ang2pix(nside, theta, phi, nest=nest)]

    return vec2pix


def _find_healpix_extension_index(pth):
    """Find the first HEALPIX extension in a FITS file and return the extension
    number. Raises IndexError if none is found.

    """
    for i, hdu in enumerate(pth):
        if hdu.header.get("PIXTYPE") == "HEALPIX":
            return i
    else:
        raise IndexError("No HEALPIX extensions found in %s" % pth.filename())


def healpix_fits_file_sampler(path, extension=None, interpolation="nearest"):
    """Create a sampler for HEALPix data read from a FITS file.

    Parameters
    ----------
    path : string
        The path to the FITS file.
    extension : integer or None (default: None)
        Which extension in the FITS file to read. If not specified, the first
        extension with PIXTYPE = "HEALPIX" will be used.
    interpolation : 'nearest' | 'bilinear'
        What interpolation scheme to use.

        WARNING: bilinear uses healpy's get_interp_val, which seems prone to segfaults

    Returns
    -------
    A function that samples the HEALPix image; the call signature is
    ``vec2pix(lon, lat) -> data``, where the inputs and output are 2D arrays
    and *lon* and *lat* are in radians.

    """
    from astropy.io import fits

    with fits.open(path) as f:
        if extension is None:
            extension = _find_healpix_extension_index(f)

        data, hdr = f[extension].data, f[extension].header

        # grab the first healpix parameter and convert to native endianness if
        # needed.
        data = data[data.dtype.names[0]]
        if data.dtype.byteorder not in "=|":
            data = data.byteswap().newbyteorder()

        nest = hdr.get("ORDERING") == "NESTED"
        coord = hdr.get("COORDSYS", "C")

    return healpix_sampler(data, nest, coord, interpolation)


def plate_carree_sampler(data):
    """Create a sampler function for all-sky data in a “plate carrée” projection.

    In this projection, the X and Y axes of the image correspond to the
    longitude and latitude spherical coordinates, respectively. Both axes map
    linearly, the X axis to the longitude range [2pi, 0] (i.e., longitude
    increases to the left), and the Y axis to the latitude range [pi/2,
    -pi/2]. Therefore the point with lat = lon = 0 corresponds to the image
    center and ``data[0,0]`` is the pixel touching lat = pi/2, lon=pi, one of
    a row adjacent to the North Pole. Typically the image is twice as wide as
    it is tall.

    Parameters
    ----------
    data : array-like, at least 2D
        The map to sample in plate carrée projection.

    Returns
    -------
    A function that samples the image; the call signature is
    ``vec2pix(lon, lat) -> data``, where the inputs and output are 2D arrays
    and *lon* and *lat* are in radians.

    """
    data = np.asarray(data)
    ny, nx = data.shape[:2]

    dx = nx / (2 * np.pi)  # pixels per radian in the X direction
    dy = ny / np.pi  # ditto, for the Y direction
    lon0 = np.pi - 0.5 / dx  # longitudes of the centers of the pixels with ix = 0
    lat0 = 0.5 * np.pi - 0.5 / dy  # latitudes of the centers of the pixels with iy = 0

    def vec2pix(lon, lat):
        lon = (lon + np.pi) % (2 * np.pi) - np.pi  # ensure in range [-pi, pi]
        ix = (lon0 - lon) * dx
        ix = np.round(ix).astype(int)
        ix = np.clip(ix, 0, nx - 1)

        iy = (lat0 - lat) * dy  # *assume* in range [-pi/2, pi/2]
        iy = np.round(iy).astype(int)
        iy = np.clip(iy, 0, ny - 1)

        return data[iy, ix]

    return vec2pix


def plate_carree_galactic_sampler(data):
    """
    Create a sampler function for all-sky data in a “plate carrée” projection
    using Galactic coordinates.

    Parameters
    ----------
    data : array-like, at least 2D
        The map to sample in plate carrée projection.

    Returns
    -------
    A function that samples the image. The call signature is
    ``sampler(lon, lat) -> data``, where the inputs and output are 2D arrays and
    *lon* and *lat* are in radians.

    """
    from astropy.coordinates import Galactic, ICRS
    import astropy.units as u

    data = np.asarray(data)
    ny, nx = data.shape[:2]

    dx = nx / (2 * np.pi)  # pixels per radian in the X direction
    dy = ny / np.pi  # ditto, for the Y direction
    lon0 = np.pi - 0.5 / dx  # longitudes of the centers of the pixels with ix = 0
    lat0 = 0.5 * np.pi - 0.5 / dy  # latitudes of the centers of the pixels with iy = 0

    def vec2pix(lon, lat):
        gal = ICRS(lon * u.rad, lat * u.rad).transform_to(Galactic)
        lon, lat = gal.l.rad, gal.b.rad

        lon = (lon + np.pi) % (2 * np.pi) - np.pi  # ensure in range [-pi, pi]
        ix = (lon0 - lon) * dx
        ix = np.round(ix).astype(int)
        ix = np.clip(ix, 0, nx - 1)

        iy = (lat0 - lat) * dy  # *assume* in range [-pi/2, pi/2]
        iy = np.round(iy).astype(int)
        iy = np.clip(iy, 0, ny - 1)

        return data[iy, ix]

    return vec2pix


def plate_carree_ecliptic_sampler(data):
    """
    Create a sampler function for all-sky data in a “plate carrée” projection
    using ecliptic coordinates.

    Parameters
    ----------
    data : array-like, at least 2D
        The map to sample in plate carrée projection.

    Returns
    -------
    A function that samples the image. The call signature is
    ``sampler(lon, lat) -> data``, where the inputs and output are 2D arrays and
    *lon* and *lat* are in radians.

    """
    from astropy.coordinates import BarycentricTrueEcliptic as Ecliptic, ICRS
    import astropy.units as u

    data = np.asarray(data)
    ny, nx = data.shape[:2]

    dx = nx / (2 * np.pi)  # pixels per radian in the X direction
    dy = ny / np.pi  # ditto, for the Y direction
    lon0 = np.pi - 0.5 / dx  # longitudes of the centers of the pixels with ix = 0
    lat0 = 0.5 * np.pi - 0.5 / dy  # latitudes of the centers of the pixels with iy = 0

    def vec2pix(lon, lat):
        ecl = ICRS(lon * u.rad, lat * u.rad).transform_to(Ecliptic)
        lon, lat = ecl.lon.rad, ecl.lat.rad
        lon = lon % (2 * np.pi) - np.pi  # ensure in range [-pi, pi]

        ix = (lon0 - lon) * dx
        ix = np.round(ix).astype(int)
        ix = np.clip(ix, 0, nx - 1)

        iy = (lat0 - lat) * dy  # *assume* in range [-pi/2, pi/2]
        iy = np.round(iy).astype(int)
        iy = np.clip(iy, 0, ny - 1)

        return data[iy, ix]

    return vec2pix


def plate_carree_planet_sampler(data):
    """
    Create a sampler function for planetary data in a “plate carrée” projection.

    This is the same as :func:`plate_carree_sampler`, except that the X axis
    is mirrored: longitude increases to the right. This is generally what is
    desired for planetary surface maps (looking at a sphere from the outside)
    instead of sky maps (looking at a sphere from the inside).

    Parameters
    ----------
    data : array-like, at least 2D
        The map to sample in plate carrée projection.

    Returns
    -------
    A function that samples the image; the call signature is
    ``vec2pix(lon, lat) -> data``, where the inputs and output are 2D arrays
    and *lon* and *lat* are in radians.
    """

    data = np.asarray(data)
    ny, nx = data.shape[:2]

    dx = nx / (2 * np.pi)  # pixels per radian in the X direction
    dy = ny / np.pi  # ditto, for the Y direction
    lon0 = -np.pi + 0.5 / dx  # longitudes of the centers of the pixels with ix = 0
    lat0 = 0.5 * np.pi - 0.5 / dy  # latitudes of the centers of the pixels with iy = 0

    def vec2pix(lon, lat):
        lon = (lon + np.pi) % (2 * np.pi) - np.pi  # ensure in range [-pi, pi]
        ix = (lon - lon0) * dx
        ix = np.round(ix).astype(int)
        ix = np.clip(ix, 0, nx - 1)

        iy = (lat0 - lat) * dy  # *assume* in range [-pi/2, pi/2]
        iy = np.round(iy).astype(int)
        iy = np.clip(iy, 0, ny - 1)

        return data[iy, ix]

    return vec2pix


def plate_carree_planet_zeroleft_sampler(data):
    """
    Create a sampler function for planetary data in a “plate carrée” projection
    where the ``longitude=0`` line is on the left edge of the image.

    This is the same as :func:`plate_carree_planet_sampler`, except that line of
    zero longitude is at the left edge of the image, not its center. Longitude
    still increases to the right, unlike :func:`plate_carree_sampler` or
    :func:`plate_carree_zeroright_sampler`. Some planetary maps use this
    convention.

    Parameters
    ----------
    data : array-like, at least 2D
        The map to sample in plate carrée projection.

    Returns
    -------
    A function that samples the image; the call signature is
    ``vec2pix(lon, lat) -> data``, where the inputs and output are 2D arrays
    and *lon* and *lat* are in radians.
    """

    data = np.asarray(data)
    ny, nx = data.shape[:2]

    dx = nx / (2 * np.pi)  # pixels per radian in the X direction
    dy = ny / np.pi  # ditto, for the Y direction
    lon0 = 0.5 / dx  # longitudes of the centers of the pixels with ix = 0
    lat0 = 0.5 * np.pi - 0.5 / dy  # latitudes of the centers of the pixels with iy = 0

    def vec2pix(lon, lat):
        lon = lon % (2 * np.pi)  # ensure in range [0, 2pi]
        ix = (lon - lon0) * dx
        ix = np.round(ix).astype(int)
        ix = np.clip(ix, 0, nx - 1)

        iy = (lat0 - lat) * dy  # *assume* in range [-pi/2, pi/2]
        iy = np.round(iy).astype(int)
        iy = np.clip(iy, 0, ny - 1)

        return data[iy, ix]

    return vec2pix


def plate_carree_zeroright_sampler(data):
    """
    Create a sampler function for data in a “plate carrée” projection where the
    ``longitude=0`` line is on the right edge of the image.

    This is the same as :func:`plate_carree_sampler`, except that line of zero
    longitude is at the right edge of the image, not its center.

    Parameters
    ----------
    data : array-like, at least 2D
        The map to sample in plate carrée projection.

    Returns
    -------
    A function that samples the image; the call signature is
    ``vec2pix(lon, lat) -> data``, where the inputs and output are 2D arrays
    and *lon* and *lat* are in radians.
    """

    data = np.asarray(data)
    ny, nx = data.shape[:2]

    dx = nx / (2 * np.pi)  # pixels per radian in the X direction
    dy = ny / np.pi  # ditto, for the Y direction
    lon0 = 2 * np.pi - 0.5 / dx  # longitudes of the centers of the pixels with ix = 0
    lat0 = 0.5 * np.pi - 0.5 / dy  # latitudes of the centers of the pixels with iy = 0

    def vec2pix(lon, lat):
        lon = lon % (2 * np.pi)  # ensure in range [0, 2pi]
        ix = (lon0 - lon) * dx
        ix = np.round(ix).astype(int)
        ix = np.clip(ix, 0, nx - 1)

        iy = (lat0 - lat) * dy  # *assume* in range [-pi/2, pi/2]
        iy = np.round(iy).astype(int)
        iy = np.clip(iy, 0, ny - 1)

        return data[iy, ix]

    return vec2pix


class ChunkedPlateCarreeSampler(object):
    """
    Setup for TOAST sampling of a chunked plate-carree image.

    This only works with the ChunkedJPEG2000Reader image right now, but in
    principle we could extend to accept other chunked formats.

    Assume a typical image coordinate system, where (x,y) = (0,0) is the
    top-left edge of the image. The "global" coordinate system refers to the
    un-chunked image, which is probably too big to fit into memory.

    In the planetary plate carree projection, (global) X and Y measure latitude
    and longitude orthogonally. The left edge of the X=0 column has lon = -pi,
    while the right edge of the X=(W-1) column has lon = +pi. The top edge of
    the Y=0 row has lat = +pi/2, and the bottom edge of the Y=(H-1) row has lat
    = -pi/2.
    """

    def __init__(self, chunked_image, planetary=False):
        self._image = chunked_image

        assert planetary, "XXX non-planetary plate carree not implemented"

        self.sx = 2 * np.pi / self._image.shape[1]  # radians per pixel, X direction
        self.sy = np.pi / self._image.shape[0]  # ditto, for the X direction

    @property
    def n_chunks(self):
        return self._image.n_chunks

    def _chunk_bounds(self, ichunk):
        cx, cy, cw, ch = self._image.chunk_spec(ichunk)

        # Note that the following are all intended to be coordinates at
        # pixel edges, in the appropriate direction, not pixel centers.
        lon_l = self.sx * cx - np.pi
        lon_r = self.sx * (cx + cw) - np.pi
        lat_u = 0.5 * np.pi - self.sy * cy
        lat_d = 0.5 * np.pi - self.sy * (cy + ch)  # note: lat_u > lat_d

        return lon_l, lon_r, lat_d, lat_u

    def filter(self, ichunk):
        """
        Get a TOAST tile-filter function for the specified chunk.

        Parameters
        ----------
        ichunk : :class:`int`
            The index of the chunk to query, between 0 and ``self.n_chunks - 1``
            (inclusive).

        Returns
        -------
        A callable object, ``filter(tile) -> bool``, suitable for use as a tile
        filter function.
        """
        (
            chunk_lon_min1,
            chunk_lon_max1,
            chunk_lat_min1,
            chunk_lat_max1,
        ) = self._chunk_bounds(ichunk)

        def latlon_tile_filter(tile):
            """
            Return true if this tile might contain data from this chunk of the
            source image.
            """
            # Need to copy the outer arguments since we're going to modify them.
            chunk_lon_min = chunk_lon_min1
            chunk_lon_max = chunk_lon_max1
            chunk_lat_min = chunk_lat_min1
            chunk_lat_max = chunk_lat_max1

            corner_lonlats = np.asarray(tile.corners)  # shape (4, 2)

            # Latitudes are easy -- no wrapping.

            tile_lat_min = np.min(corner_lonlats[:, 1])
            tile_lat_max = np.max(corner_lonlats[:, 1])

            if chunk_lat_min > tile_lat_max:
                return False
            if chunk_lat_max < tile_lat_min:
                return False

            # Can't reject based on latitudes. Longitudes are trickier.
            #
            # Step 1: If we hit one of the poles, longitudes become
            # ~meaningless, so all we can really do (in our simplistic approach
            # here) is accept the tile. We compare to ~(pi - 1e-8) here to
            # account for inevitable roundoff. Note that if we don't apply the
            # lat-bounds filter first, every single chunk will accept tiles at
            # the poles, even if it's right on the equator.

            if tile_lat_max > 1.5707963 or tile_lat_min < -1.5707963:
                return True

            # Step 2: get good a coverage range for tile longitudes. Some tiles
            # span a full pi in longitude, and sometimes the "corners"
            # longitudes span all sorts of values from -2pi to 2pi. So just
            # shuffle them around until we get a self-consistent min/max.

            lons = corner_lonlats[:, 0]
            keep_going = True

            while keep_going:
                keep_going = False

                imin = np.argmin(lons)
                tile_lon_min = lons[imin]
                tile_lon_max = np.max(lons)

                if tile_lon_max - tile_lon_min > np.pi:
                    keep_going = True
                    lons[imin] += 2 * np.pi

            # Step 3: Now, shuffle the chunk longitudes by +/-2pi so that they
            # line up with the tile longitude bounds. We know that we'll
            # ultimately be comparing the chunk_lon_min to tile_lon_max, and
            # chunk/max to tile/min, so we can treat those pairs individually.

            while chunk_lon_min - tile_lon_max > np.pi:
                chunk_lon_min -= 2 * np.pi

            while tile_lon_max - chunk_lon_min > np.pi:
                chunk_lon_min += 2 * np.pi

            while chunk_lon_max - tile_lon_min > np.pi:
                chunk_lon_max -= 2 * np.pi

            while tile_lon_min - chunk_lon_max > np.pi:
                chunk_lon_max += 2 * np.pi

            # Finally, we can reject this tile if it lies beyond the boundaries
            # of the chunk we're considering.

            if chunk_lon_min > tile_lon_max:
                return False
            if chunk_lon_max < tile_lon_min:
                return False

            # Well, we couldn't reject it, so we must accept:
            return True

        return latlon_tile_filter

    def sampler(self, ichunk):
        """
        Get a TOAST sampler function for the specified chunk.

        Parameters
        ----------
        ichunk : :class:`int`
            The index of the chunk to query, between 0 and ``self.n_chunks - 1``
            (inclusive).

        Returns
        -------
        A callable object, ``sampler(lon, lat) -> data``, suitable for use as a tile
        sampler function.
        """
        from .image import Image

        chunk_lon_min, chunk_lon_max, chunk_lat_min, chunk_lat_max = self._chunk_bounds(
            ichunk
        )
        data = self._image.chunk_data(ichunk)
        data_img = Image.from_array(data)
        buffer = data_img.mode.make_maskable_buffer(256, 256)
        biy, bix = np.indices((256, 256))

        ny, nx = data.shape[:2]
        dx = nx / (
            chunk_lon_max - chunk_lon_min
        )  # pixels per radian in the X direction
        dy = ny / (chunk_lat_max - chunk_lat_min)  # ditto, for the Y direction
        lon0 = (
            chunk_lon_min + 0.5 / dx
        )  # longitudes of the centers of the pixels with ix = 0
        lat0 = (
            chunk_lat_max - 0.5 / dy
        )  # latitudes of the centers of the pixels with iy = 0

        def plate_carree_planet_sampler(lon, lat):
            lon = (lon + np.pi) % (2 * np.pi) - np.pi  # ensure in range [-pi, pi]
            ix = (lon - lon0) * dx
            ix = np.round(ix).astype(int)
            ok = (ix >= 0) & (ix < nx)

            iy = (lat0 - lat) * dy  # *assume* in range [-pi/2, pi/2]
            iy = np.round(iy).astype(int)
            ok &= (iy >= 0) & (iy < ny)

            data_img.fill_into_maskable_buffer(buffer, iy[ok], ix[ok], biy[ok], bix[ok])
            return buffer.asarray()

        return plate_carree_planet_sampler
