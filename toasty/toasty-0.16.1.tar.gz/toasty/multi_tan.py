# -*- mode: python; coding: utf-8 -*-
# Copyright 2019-2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Generate tiles from a collection of images on a common TAN projection.
"""

__all__ = """
MultiTanProcessor
""".split()

from astropy.wcs import WCS
import numpy as np
from tqdm import tqdm
import warnings

from .study import StudyTiling

MATCH_HEADERS = [
    "CTYPE1",
    "CTYPE2",
    "CRVAL1",
    "CRVAL2",
    "CDELT1",
    "CDELT2",
]

# In my sample set, some of these files vary minutely from one header to the
# next, so we save them but don't demand exact matching. We should use
# np.isclose() or whatever it is.
SAVE_HEADERS = [
    "PC1_1",
    "PC2_2",
]


class MultiTanDescriptor(object):
    ident = None
    in_shape = None

    crxmin = None
    crxmax = None
    crymin = None
    crymax = None

    imin = None
    imax = None
    jmin = None
    jmax = None

    sub_tiling = None


class MultiTanProcessor(object):
    """
    Generate tiles from a collection of images on a common TAN projection.

    Some large astronomical images are stored as a collection of sub-images that
    share a common tangential projection, a format is that is nice and easy to
    convert into a WWT "study" tile pyramid. This class can process a collection
    of such images and break them into the highest-resolution layer of such a
    tile pyramid.
    """

    def __init__(self, collection):
        self._collection = collection

    def compute_global_pixelization(self, builder):
        """
        Read the input images to determine the global pixelation of this data
        set.

        This function reads the FITS headers of all of the input data files to
        determine the overall image size and the parameters of its tiling as a
        WWT study. This should be pretty easy, because we've been assured that
        everything is on a nice common TAN, which is exactly what we need to end
        up with anyway.
        """

        self._descs = []
        ref_headers = None
        global_crxmin = None

        for desc in self._collection.descriptions():
            # For figuring out the tiling properties, we need to ensure that
            # we're working in top-down mode everywhere.
            desc.ensure_negative_parity()

            # Build up information for the common TAN projection.
            header = desc.wcs.to_header()

            if ref_headers is None:
                ref_headers = {}

                for h in MATCH_HEADERS:
                    ref_headers[h] = header[h]

                for h in SAVE_HEADERS:
                    ref_headers[h] = header[h]

                if ref_headers["CTYPE1"] != "RA---TAN":
                    raise Exception(
                        "all inputs must be in a TAN projection, but {} is not".format(
                            desc.collection_id
                        )
                    )
                if ref_headers["CTYPE2"] != "DEC--TAN":
                    raise Exception(
                        "all inputs must be in a TAN projection, but {} is not".format(
                            desc.collection_id
                        )
                    )
            else:
                for h in MATCH_HEADERS:
                    expected = ref_headers[h]
                    observed = header[h]

                    if observed != expected:
                        raise Exception(
                            "inputs are not on uniform WCS grid; in file {}, expected "
                            "value {} for header {} but observed {}".format(
                                desc.collection_id, expected, h, observed
                            )
                        )

            this_crpix1 = header["CRPIX1"] - 1
            this_crpix2 = header["CRPIX2"] - 1

            mtdesc = MultiTanDescriptor()
            mtdesc.ident = desc.collection_id
            mtdesc.in_shape = desc.shape

            mtdesc.crxmin = 0 - this_crpix1
            mtdesc.crxmax = (desc.shape[1] - 1) - this_crpix1
            mtdesc.crymin = 0 - this_crpix2
            mtdesc.crymax = (desc.shape[0] - 1) - this_crpix2

            if global_crxmin is None:
                global_crxmin = mtdesc.crxmin
                global_crxmax = mtdesc.crxmax
                global_crymin = mtdesc.crymin
                global_crymax = mtdesc.crymax
            else:
                global_crxmin = min(global_crxmin, mtdesc.crxmin)
                global_crxmax = max(global_crxmax, mtdesc.crxmax)
                global_crymin = min(global_crymin, mtdesc.crymin)
                global_crymax = max(global_crymax, mtdesc.crymax)

            self._descs.append(mtdesc)

        # We can now compute the global properties of the tiled TAN representation:

        width = int(global_crxmax - global_crxmin) + 1
        height = int(global_crymax - global_crymin) + 1
        self._tiling = StudyTiling(width, height)

        ref_headers["CRPIX1"] = this_crpix1 + 1 + (mtdesc.crxmin - global_crxmin)
        ref_headers["CRPIX2"] = this_crpix2 + 1 + (mtdesc.crymin - global_crymin)
        wcs = WCS(ref_headers)

        self._tiling.apply_to_imageset(builder.imgset)
        builder.apply_wcs_info(wcs, width, height)

        # While we're here, figure out how each input will map onto the global
        # tiling. This makes sure that nothing funky happened during the
        # computation and allows us to know how many tiles we'll have to visit.

        self._n_todo = 0

        for desc in self._descs:
            desc.imin = int(np.floor(desc.crxmin - global_crxmin))
            desc.imax = int(np.ceil(desc.crxmax - global_crxmin))
            desc.jmin = int(np.floor(desc.crymin - global_crymin))
            desc.jmax = int(np.ceil(desc.crymax - global_crymin))

            # Compute the sub-tiling now so that we can count how many total
            # tiles we'll need to process.

            if desc.imax < desc.imin or desc.jmax < desc.jmin:
                raise Exception(
                    f"segment {desc.ident} maps to zero size in the global mosaic"
                )

            desc.sub_tiling = self._tiling.compute_for_subimage(
                desc.imin,
                desc.jmin,
                desc.imax + 1 - desc.imin,
                desc.jmax + 1 - desc.jmin,
            )

            self._n_todo += desc.sub_tiling.count_populated_positions()

        return self  # chaining convenience

    def tile(self, pio, parallel=None, cli_progress=False, **kwargs):
        """
        Tile the input images into the deepest layer of the pyramid.

        Parameters
        ----------
        pio : :class:`toasty.pyramid.PyramidIO`
            A :class:`~toasty.pyramid.PyramidIO` instance to manage the I/O with
            the tiles in the tile pyramid.
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
            self._tile_parallel(pio, cli_progress, parallel, **kwargs)
        else:
            self._tile_serial(pio, cli_progress, **kwargs)

        # Since we used `pio.update_image()`, we should clean up the lockfiles
        # that were generated.
        pio.clean_lockfiles(self._tiling._tile_levels)

    def _tile_serial(self, pio, cli_progress, **kwargs):
        tile_parity_sign = pio.get_default_vertical_parity_sign()

        with tqdm(total=self._n_todo, disable=not cli_progress) as progress:
            for image, desc in zip(self._collection.images(), self._descs):
                # Ensure that the image and the eventual tile agree on parity
                if image.get_parity_sign() != tile_parity_sign:
                    image.flip_parity()

                for (
                    pos,
                    width,
                    height,
                    image_x,
                    image_y,
                    tile_x,
                    tile_y,
                ) in desc.sub_tiling.generate_populated_positions():
                    # Tiling coordinate systems are always negative (top-down)
                    # parity, with the Y=0 tile at the top. But the actual data
                    # buffers might be positive (bottoms-up) parity -- this is
                    # the case for FITS. In those situations, we have to flip
                    # the vertical positioning. Because we have ensured that the
                    # source image and tile layouts agree, the needed tweak is
                    # actually quite minimal:

                    if tile_parity_sign == 1:
                        image_y = image.height - (image_y + height)
                        tile_y = 256 - (tile_y + height)

                    ix_idx = slice(image_x, image_x + width)
                    bx_idx = slice(tile_x, tile_x + width)
                    iy_idx = slice(image_y, image_y + height)
                    by_idx = slice(tile_y, tile_y + height)

                    with pio.update_image(
                        pos, masked_mode=image.mode, default="masked"
                    ) as basis:
                        image.update_into_maskable_buffer(
                            basis, iy_idx, ix_idx, by_idx, bx_idx
                        )

                    progress.update(1)

        if cli_progress:
            print()

    def _tile_parallel(self, pio, cli_progress, parallel, **kwargs):
        import multiprocessing as mp

        # Start up the workers

        done_event = mp.Event()
        queue = mp.Queue(maxsize=2 * parallel)
        workers = []

        for _ in range(parallel):
            w = mp.Process(
                target=_mp_tile_worker, args=(queue, done_event, pio, kwargs)
            )
            w.daemon = True
            w.start()
            workers.append(w)

        # Send out them segments

        with tqdm(total=len(self._descs), disable=not cli_progress) as progress:
            for image, desc in zip(self._collection.images(), self._descs):
                queue.put((image, desc))
                progress.update(1)

        # Finish up

        queue.close()
        queue.join_thread()
        done_event.set()

        for w in workers:
            w.join()

        if cli_progress:
            print()


def _mp_tile_worker(queue, done_event, pio, _kwargs):
    """
    Generate and enqueue the tiles that need to be processed.
    """
    from queue import Empty

    tile_parity_sign = pio.get_default_vertical_parity_sign()

    while True:
        try:
            # un-pickling WCS objects always triggers warnings right now
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                image, desc = queue.get(True, timeout=1)
        except Empty:
            if done_event.is_set():
                break
            continue

        if image.get_parity_sign() != tile_parity_sign:
            image.flip_parity()

        for (
            pos,
            width,
            height,
            image_x,
            image_y,
            tile_x,
            tile_y,
        ) in desc.sub_tiling.generate_populated_positions():
            if tile_parity_sign == 1:
                image_y = image.height - (image_y + height)
                tile_y = 256 - (tile_y + height)

            ix_idx = slice(image_x, image_x + width)
            bx_idx = slice(tile_x, tile_x + width)
            iy_idx = slice(image_y, image_y + height)
            by_idx = slice(tile_y, tile_y + height)

            with pio.update_image(
                pos, masked_mode=image.mode, default="masked"
            ) as basis:
                image.update_into_maskable_buffer(basis, iy_idx, ix_idx, by_idx, bx_idx)
