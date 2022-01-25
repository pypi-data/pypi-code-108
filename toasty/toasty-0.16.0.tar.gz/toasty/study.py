# -*- mode: python; coding: utf-8 -*-
# Copyright 2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""Common routines for tiling images anchored to the sky in a gnomonic
(tangential) projection.

"""
from __future__ import absolute_import, division, print_function

__all__ = '''
StudyTiling
tile_study_image
'''.split()

import numpy as np
from tqdm import tqdm

from .pyramid import Pos, next_highest_power_of_2, tiles_at_depth


class StudyTiling(object):
    """
    Information about how a WWT "study" image is broken into tiles.

    In WWT a "study" is a large astronomical image projected onto the sky
    using a gnomonic (tangential or TAN) projection. The image may have many
    pixels, so it is broken up into tiles for efficient visualization.

    Note that this class doesn't know anything about how the image is
    projected onto the sky, or whether it is projected at all. The core tiling
    functionality doesn't need to care about that.

    """
    _width = None
    "The width of the region in which image data are available, in pixels (int)."

    _height = None
    "The height of the region in which image data are available, in pixels (int)."

    _p2n = None
    "The size of the study when tiled, in pixels - a power of 2."

    _tile_size = None
    "The number of tiles wide and high in the tiled study - a power of 2."

    _tile_levels = None
    "The number of levels in the tiling - ``log2(tile_size)``."

    _img_gx0 = None
    """The pixel position of the image data within the global (tiled)
    pixelization, in pixels right from the left edge (int). Nonnegative.

    """
    _img_gy0 = None
    """The pixel position of the image data within the global (tiled)
    pixelization, in pixels down from the top edge (int). Nonnegative.

    """
    def __init__(self, width, height):
        """Set up the tiling information.

        Parameters
        ----------
        width : positive integer
            The width of the full-resolution image, in pixels.
        height : positive integer
            The height of the full-resolution image, in pixels.

        """
        width = int(width)
        height = int(height)

        if width <= 0:
            raise ValueError('bad width value: %r' % (width, ))
        if height <= 0:
            raise ValueError('bad height value: %r' % (height, ))

        self._width = width
        self._height = height
        p2w = next_highest_power_of_2(self._width)
        p2h = next_highest_power_of_2(self._height)
        self._p2n = max(p2w, p2h)
        self._tile_size = self._p2n // 256
        self._tile_levels = int(np.log2(self._tile_size))
        self._img_gx0 = (self._p2n - self._width) // 2
        self._img_gy0 = (self._p2n - self._height) // 2


    def compute_for_subimage(self, subim_ix, subim_iy, subim_width, subim_height):
        """
        Create a new compatible tiling whose underlying image is a subset of this one.

        Parameters
        ----------
        subim_ix : integer
            The 0-based horizontal pixel position of the left edge of the sub-image,
            relative to this tiling's image.
        subim_iy : integer
            The 0-based vertical pixel position of the top edge of the sub-image,
            relative to this tiling's image.
        subim_width : nonnegative integer
            The width of the sub-image, in pixels.
        subim_height : nonnegative integer
            The height of the sub-image, in pixels.

        Returns
        -------
        A new :class:`~StudyTiling` with the same number of tile levels as this one.
        However, the internal information about where the available data land within
        that tiling will be appropriate for the specified sub-image. Methods like
        :meth:`count_populated_positions`, :meth:`generate_populated_positions`, and
        :meth:`tile_image` will behave differently.

        """
        if subim_width < 0 or subim_width > self._width:
            raise ValueError('bad subimage width value {!r}'.format(subim_width))
        if subim_height < 0 or subim_height > self._height:
            raise ValueError('bad subimage height value {!r}'.format(subim_height))
        if subim_ix < 0 or subim_ix + subim_width > self._width:
            raise ValueError('bad subimage ix value {!r}'.format(subim_ix))
        if subim_iy < 0 or subim_iy + subim_height > self._height:
            raise ValueError('bad subimage iy value {!r}'.format(subim_iy))

        sub_tiling = StudyTiling(self._width, self._height)
        sub_tiling._width = subim_width
        sub_tiling._height = subim_height
        sub_tiling._img_gx0 += subim_ix
        sub_tiling._img_gy0 += subim_iy
        return sub_tiling


    def n_deepest_layer_tiles(self):
        """Return the number of tiles in the highest-resolution layer."""
        return 4**self._tile_levels


    def apply_to_imageset(self, imgset):
        """Fill the specific ``wwt_data_formats.imageset.ImageSet`` object
        with parameters defined by this tiling,

        Parameters
        ----------
        imgset : ``wwt_data_formats.imageset.ImageSet``
            The object to modify

        Notes
        -----
        The settings currently transferred are the number of tile levels and
        the projection type.

        """
        from wwt_data_formats.enums import ProjectionType

        imgset.tile_levels = self._tile_levels

        if self._tile_levels == 0:
          imgset.projection = ProjectionType.SKY_IMAGE
        else:
          imgset.projection = ProjectionType.TAN


    def image_to_tile(self, im_ix, im_iy):
        """Convert an image pixel position to a tiled pixel position.

        Parameters
        ----------
        im_ix : integer
            A 0-based horizontal pixel position in the image coordinate system.
        im_iy : integer
            A 0-based vertical pixel position in the image coordinate system.

        Notes
        -----
        ``(0, 0)`` is the top-left corner of the image. The input values need
        not lie on the image. (I.e., they may be negative.)

        Returns ``(tile_ix, tile_iy, subtile_ix, subtile_iy)``, where

        - *tile_ix* is X index of the matched tile in the tiling, between 0
          and 2**tile_size - 1. Measured right from the left edge of the
          tiling.

        - *tile_iy* is Y index of the matched tile in the tiling, between 0
          and 2**tile_size - 1. Measured down from the top of the tiling.

        - *subtile_ix* is the pixel X position within that tile, between 0 and
          255. Measured right from the left edge of the tiling.

        - *subtile_iy* is the pixel Y position within that tile, between 0 and
          255. Measured down from the top edge of the tiling.

        """
        gx = im_ix + self._img_gx0
        gy = im_iy + self._img_gy0
        tile_ix = np.floor(gx // 256).astype(int)
        tile_iy = np.floor(gy // 256).astype(int)
        return (tile_ix, tile_iy, gx % 256, gy % 256)


    def count_populated_positions(self):
        """
        Count how many tiles contain image data.

        This is used for progress reporting.

        """
        img_gx1 = self._img_gx0 + self._width - 1
        img_gy1 = self._img_gy0 + self._height - 1
        tile_start_tx = self._img_gx0 // 256
        tile_start_ty = self._img_gy0 // 256
        tile_end_tx = img_gx1 // 256
        tile_end_ty = img_gy1 // 256
        return (tile_end_ty + 1 - tile_start_ty) * (tile_end_tx + 1 - tile_start_tx)


    def generate_populated_positions(self):
        """Generate information about tiles containing image data.

        Generates a sequence of tuples ``(pos, width, height, image_x,
        image_y, tile_x, tile_y)`` where:

        - *pos* is a :class:`toasty.pyramid.Pos` tuple giving parameters of a tile
        - *width* is the width of the rectangle of image data contained in this tile,
          between 1 and 256.
        - *height* is the height of the rectangle of image data contained in this tile,
          between 1 and 256.
        - *image_x* is the pixel X coordinate of the left edge of the image data in this tile
          in the image rectangle, increasing from the left edge of the tile. Between 0 and
          ``self._width - 1`` (inclusive).
        - *image_y* is the pixel Y coordinate of the *top* edge of the image data in this tile
          in the image rectangle, increasing from the top edge of the tile. Between 0 and
          ``self._height - 1`` (inclusive).
        - *tile_x* is the pixel X coordinate of the left edge of the image data in this tile
          in the tile rectangle, increasing from the left edge of the tile. Between 0 and
          255 (inclusive).
        - *tile_y* is the pixel Y coordinate of the *top* edge of the image data in this tile
          in the tile rectangle, increasing from the top edge of the tile. Between 0 and
          255 (inclusive).

        Tiles that do not overlap the image at all are not generated. Tiles
        that are completely filled with image data will yield tuples of the
        form ``(pos, 256, 256, im_x, im_y, 0, 0)``. An image that fits
        entirely in one tile will yield a tuple of the form ``(Pos(n=0, x=0,
        y=0), width, height, 0, 0, tx, ty)``.

        """
        # Get the position of the actual image data in "global pixel
        # coordinates", which span the whole tiled region (a superset of the
        # image itself) with x=0, y=0 being the left-top corner of the tiled
        # region.

        img_gx1 = self._img_gx0 + self._width - 1  # inclusive: there are image data in this column
        img_gy1 = self._img_gy0 + self._height - 1  # ditto

        tile_start_tx = self._img_gx0 // 256
        tile_start_ty = self._img_gy0 // 256
        tile_end_tx = img_gx1 // 256  # inclusive; there are image data in this column of tiles
        tile_end_ty = img_gy1 // 256  # ditto

        for ity in range(tile_start_ty, tile_end_ty + 1):
            for itx in range(tile_start_tx, tile_end_tx + 1):
                # (inclusive) tile bounds in global pixel coords
                tile_gx0 = itx * 256
                tile_gy0 = ity * 256
                tile_gx1 = tile_gx0 + 255
                tile_gy1 = tile_gy0 + 255

                # overlap (= intersection) of the image and the tile in global pixel coords
                overlap_gx0 = max(tile_gx0, self._img_gx0)
                overlap_gy0 = max(tile_gy0, self._img_gy0)
                overlap_gx1 = min(tile_gx1, img_gx1)
                overlap_gy1 = min(tile_gy1, img_gy1)

                # coordinates of the overlap in image pixel coords
                img_overlap_x0 = overlap_gx0 - self._img_gx0
                img_overlap_x1 = overlap_gx1 - self._img_gx0
                img_overlap_y0 = overlap_gy0 - self._img_gy0
                img_overlap_y1 = overlap_gy1 - self._img_gy0

                # shape of the overlap
                overlap_width = img_overlap_x1 + 1 - img_overlap_x0
                overlap_height = img_overlap_y1 + 1 - img_overlap_y0

                # coordinates of the overlap in this tile's coordinates
                tile_overlap_x0 = overlap_gx0 - tile_gx0
                tile_overlap_y0 = overlap_gy0 - tile_gy0

                yield (
                    Pos(self._tile_levels, itx, ity),
                    overlap_width,
                    overlap_height,
                    img_overlap_x0,
                    img_overlap_y0,
                    tile_overlap_x0,
                    tile_overlap_y0,
                )


    def tile_image(self, image, pio, cli_progress=False):
        """Tile an in-memory image as a study.

        Parameters
        ----------
        image : :class:`toasty.image.Image`
            In-memory image data. The image's dimensions must match the ones
            for which this tiling was computed.
        pio : :class:`toasty.pyramid.PyramidIO`
            A handle for doing I/O on the tile pyramid
        cli_progress : optional boolean, defaults False
            If true, a progress bar will be printed to the terminal using tqdm.

        Returns
        -------
        Self.

        """
        if image.height != self._height:
            raise ValueError('height of image to be sampled does not match tiling')
        if image.width != self._width:
            raise ValueError('width of image to be sampled does not match tiling')

        # For tiled FITS, the overall input image and tiling coordinate system
        # need to have negative (JPEG-like) parity, but the individal tiles need
        # to be saved with positive (FITS-like) parity. The upshot is that we
        # have to vertically flip the data layout in our tile buffers.
        invert_into_tiles = pio.get_default_vertical_parity_sign() == 1

        # TODO: ideally make_maskable_buffer should be a method
        # on the Image class which could then avoid having to
        # manually transfer _format.
        buffer = image.mode.make_maskable_buffer(256, 256)
        buffer._default_format = image._default_format

        with tqdm(total=self.count_populated_positions(), disable=not cli_progress) as progress:
            for pos, width, height, image_x, image_y, tile_x, tile_y in self.generate_populated_positions():
                if invert_into_tiles:
                    flip_tile_y1 = 255 - tile_y
                    flip_tile_y0 = flip_tile_y1 - height

                    if flip_tile_y0 == -1:
                        flip_tile_y0 = None  # with a slice, -1 does the wrong thing

                    by_idx = slice(flip_tile_y1, flip_tile_y0, -1)
                else:
                    by_idx = slice(tile_y, tile_y + height)

                iy_idx = slice(image_y, image_y + height)
                ix_idx = slice(image_x, image_x + width)
                bx_idx = slice(tile_x, tile_x + width)

                image.fill_into_maskable_buffer(buffer, iy_idx, ix_idx, by_idx, bx_idx)
                pio.write_image(pos, buffer)
                progress.update(1)

        if cli_progress:
            print()

        return self


def tile_study_image(image, pio, cli_progress=False):
    """Tile an image as a study, loading the whole thing into memory.

    Parameters
    ----------
    image : :class:`toasty.image.Image`
        The image to tile.
    pio : :class:`toasty.pyramid.PyramidIO`
        A handle for doing I/O on the tile pyramid
    cli_progress : optional boolean, defaults False
        If true, a progress bar will be printed to the terminal using tqdm.

    Returns
    -------
    A :class:`StudyTiling` defining the tiling of the image.

    """
    tiling = StudyTiling(image.width, image.height)
    tiling.tile_image(image, pio, cli_progress=cli_progress)
    return tiling
