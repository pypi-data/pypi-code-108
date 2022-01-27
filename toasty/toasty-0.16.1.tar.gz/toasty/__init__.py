# -*- mode: python; coding: utf-8 -*-
# Copyright 2013-2021 Chris Beaumont and the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function


__all__ = [
    "tile_fits",
]


def tile_fits(
    fits,
    out_dir=None,
    hdu_index=None,
    override=False,
    cli_progress=False,
    force_hipsgen=False,
    force_tan=False,
    blankval=None,
    **kwargs
):
    """
    Process a file or a list of FITS files into a tile pyramid using either a common tangential projection or HiPSgen.

    Parameters
    ----------
    fits : str or list of str
        A single path or a list of paths to FITS files to be processed.
    out_dir : optional str, defaults to None
        A path to the output directory where all the tiled fits will be located. If not set, the output directory will
        be at the location of the first FITS file.
    hdu_index : optional int or list of int, defaults to None
        Use this parameter to specify which HDU to tile. If the *fits* input is a list of FITS, you can specify the
        hdu_index of each FITS by using a list of integers like this: [0, 2, 1]. If hdu_index is not set, toasty will
        use the first HDU with tilable content in each FITS.
    override : optional boolean, defaults to False
        If there is already a tiled FITS in *out_dir*, the tiling process is skipped and the content in *out_dir* is
        served. To override the content in *out_dir*, set *override* to True.
    cli_progress : optional boolean, defaults to False
        If true, progress messages will be printed as the FITS files are being processed.
    force_hipsgen : optional boolean, defaults to False
        Force usage of HiPSgen tiling over tangential projection. If this and *force_tan* are set to False, this method
        will figure out when to use the different projections. Tangential projection for smaller angular areas and
        HiPSgen larger regions of the sky.
    force_tan : optional boolean, defaults to False
        Force usage of tangential projection tiling over HiPSgen. If this and *force_hipsgen* are set to False, this
        method will figure out when to use the different projections. Tangential projection for smaller angular areas
        and HiPSgen larger regions of the sky.
    blankval : optional number, default None
        An image value to treat as undefined in all FITS inputs.
    kwargs
        Settings for the tiling process. For example, ``blankval``.

    Returns
    -------
    out_dir : :class:`str`
        The relative path to the base directory where the tiled files are located
    bld : :class:`~toasty.builder.Builder`
        State for the imagery data set that's been assembled.
    """
    # Importing here to keep toasty namespace clean:
    from toasty import collection, fits_tiler

    coll = collection.load(fits, hdu_index=hdu_index, blankval=blankval)
    tiler = fits_tiler.FitsTiler(
        coll,
        out_dir=out_dir,
        force_hipsgen=force_hipsgen,
        force_tan=force_tan,
    )
    tiler.tile(cli_progress=cli_progress, override=override, **kwargs)
    return tiler.out_dir, tiler.builder
