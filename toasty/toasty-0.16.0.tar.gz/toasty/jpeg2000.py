# -*- mode: python; coding: utf-8 -*-
# Copyright 2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Special handling for JPEG2000 files.

This is very primitive support. Implemented for:

https://planetarymaps.usgs.gov/mosaic/Lunar_Kaguya_TC_Ortho_Global_4096ppd_v02.jp2.html

JPEG2000's can be tiled. We refer to these tiles as "chunks" to try to avoid
confusion with Toasty's tiling process (although perhaps this just makes things
worse).
"""

from __future__ import absolute_import, division, print_function

__all__ = '''
ChunkedJPEG2000Reader
HAS_JPEG2000
'''.split()

try:
    import glymur
    HAS_JPEG2000 = True
except ImportError:
    HAS_JPEG2000 = False


class ChunkedJPEG2000Reader(object):
    """
    A simple reader for tiled JPEG2000 files.

    Parameters
    ----------
    path : path-like
        The path of the JP2 input file
    fake_data : optional bool
        The default is false. If true, no data are read from the file. Instead
        an array of 255's is returned. This can be useful for testing, where in
        my large test case (the Kaguya JP2) it can take 15 minutes to read a
        single tile from the file.
    """

    def __init__(self, path, fake_data=False):
        if not HAS_JPEG2000:
            raise Exception('you must install the `glymur` Python package to process JPEG2000 files')

        self._jp2 = glymur.Jp2k(path)
        self._tile_shape = None
        self._fake_data = fake_data

        for seg in self._jp2.codestream.segment:
            if seg.marker_id == 'SIZ':
                self._tile_shape = (seg.ytsiz, seg.xtsiz)

    @property
    def shape(self):
        """
        A tuple of either ``(height, width)`` or ``(height, width, n_components)``.
        """
        return self._jp2.shape

    @property
    def n_chunks(self):
        """
        The number of chunks (tiles) inside the JPEG2000 file.
        """
        th, tw = self._tile_shape
        return ((self._jp2.shape[0] + th - 1) // th) * ((self._jp2.shape[1] + tw - 1) // tw)

    def chunk_spec(self, ichunk):
        """
        Get information about an image chunk that can be loaded.

        Parameters
        ----------
        ichunk : :class:`int`
            The index of the chunk to query, between 0 and ``self.n_chunks - 1``
            (inclusive).

        Returns
        -------
        Tuple of ``(x, y, width, height)``, where the coordinates refer to
        the top-left corner of the chunk relative to the overall image
        (0-based).
        """
        if ichunk < 0 or ichunk >= self.n_chunks:
            raise ValueError(f'got ichunk={ichunk!r}; should be between 0 and {self.n_chunks-1}')

        th, tw = self._tile_shape
        gh, gw = self._jp2.shape[:2]
        chunks_per_row = (gw + tw - 1) // tw
        icol = ichunk // chunks_per_row
        irow = ichunk % chunks_per_row

        x0 = tw * irow
        x1 = min(tw * (irow + 1), gw)
        chunk_width = x1 - x0

        y0 = th * icol
        y1 = min(th * (icol + 1), gh)
        chunk_height = y1 - y0

        return x0, y0, chunk_width, chunk_height

    def chunk_data(self, ichunk):
        """
        Load an image chunk.

        Parameters
        ----------
        ichunk : :class:`int`
            The index of the chunk to query, between 0 and ``self.n_chunks - 1``
            (inclusive).

        Returns
        -------
        A numpy array of image data whose overall shape depends on the image
        format (see :attr:`shape`), but whose width and height will agree with
        the chunk specification.

        Notes
        -----
        This can be extremely slow. With the large chunks used by the Kaguya JPEG2000
        file, it can take ~15 minutes to load a typical chunk.
        """
        # The only way that the glymur package makes it possible to read
        # explicitly tile-by-tile is through a deprecated API, but if we use the
        # newer indexing API, it seems that we get the same effect (including
        # performance) with the following approach.
        x0, y0, w, h = self.chunk_spec(ichunk)

        if self._fake_data:
            import numpy as np
            a = np.empty((h, w), dtype=np.uint8)
            a.fill(255)
            return a

        return self._jp2[y0:y0+h,x0:x0+w]
