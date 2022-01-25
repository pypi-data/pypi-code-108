# -*- mode: python; coding: utf-8 -*-
# Copyright 2019-2021 the AAS WorldWide Telescope project.
# Licensed under the MIT License.

"""Entrypoint for the "toasty" command-line interface.

"""

from __future__ import absolute_import, division, print_function

__all__ = """
die
entrypoint
warn
""".split()

import argparse
import os.path
import sys
import warnings

from wwt_data_formats.cli import EnsureGlobsExpandedAction


# General CLI utilities


def die(msg):
    print("error:", msg, file=sys.stderr)
    sys.exit(1)


def warn(msg):
    print("warning:", msg, file=sys.stderr)


# "cascade" subcommand


def cascade_getparser(parser):
    parser.add_argument(
        "--parallelism",
        "-j",
        metavar="COUNT",
        type=int,
        help="The parallelization level (default: use all CPUs; specify `1` to force serial processing)",
    )
    parser.add_argument(
        "--format",
        "-f",
        metavar="FORMAT",
        default=None,
        choices=["png", "jpg", "npy", "fits"],
        help="The format of data files to cascade. If not specified, this will be guessed.",
    )
    parser.add_argument(
        "--start",
        metavar="DEPTH",
        type=int,
        help="The depth of the TOAST layer to start the cascade",
    )
    parser.add_argument(
        "pyramid_dir",
        metavar="DIR",
        help="The directory containing the tile pyramid to cascade",
    )


def cascade_impl(settings):
    from .merge import averaging_merger, cascade_images
    from .pyramid import PyramidIO

    pio = PyramidIO(settings.pyramid_dir, default_format=settings.format)

    start = settings.start
    if start is None:
        die("currently, you must specify the start layer with the --start option")

    cascade_images(
        pio, start, averaging_merger, parallel=settings.parallelism, cli_progress=True
    )


# "check-avm" subcommand


def check_avm_getparser(parser):
    parser.add_argument(
        "--print",
        "-p",
        dest="print_avm",
        action="store_true",
        help="Print the AVM data if present",
    )
    parser.add_argument(
        "--exitcode",
        action="store_true",
        help="Exit with code 1 if no AVM tags are present",
    )
    parser.add_argument(
        "image",
        metavar="PATH",
        help="An image to check for AVM tags",
    )


def check_avm_impl(settings):
    try:
        from pyavm import AVM, exceptions

        SYNTAX_EXCEPTIONS = (
            exceptions.AVMListLengthError,
            exceptions.AVMItemNotInControlledVocabularyError,
            exceptions.AVMEmptyValueError,
        )
    except ImportError:
        die("cannot check AVM tags: you must install the `pyavm` package")

    try:
        # PyAVM can issue a lot of warnings that aren't helpful to the user.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            avm = AVM.from_image(settings.image)
    except exceptions.NoXMPPacketFound:
        print(f"{settings.image}: no AVM tags")
        sys.exit(1 if settings.exitcode else 0)
    except SYNTAX_EXCEPTIONS as e:
        print(
            f"{settings.image}: AVM data are present but malformed: {e} ({e.__class__.__name__})"
        )
        sys.exit(1)
    except IOError as e:
        die(f"error probing AVM tags of `{settings.image}`: {e}")

    if settings.print_avm:
        print(f"{settings.image}: AVM tags are present")
        print()
        print(avm)
    else:
        print(f"{settings.image}: AVM tags are present (use `--print` to display them)")


# "make_thumbnail" subcommand


def make_thumbnail_getparser(parser):
    from .image import ImageLoader

    ImageLoader.add_arguments(parser)

    parser.add_argument(
        "imgpath",
        metavar="IN-PATH",
        help="The image file to be thumbnailed",
    )
    parser.add_argument(
        "outpath",
        metavar="OUT-PATH",
        help="The location of the new thumbnail file",
    )


def make_thumbnail_impl(settings):
    from .image import ImageLoader

    olp = settings.outpath.lower()
    if not (olp.endswith(".jpg") or olp.endswith(".jpeg")):
        warn(
            'saving output in JPEG format even though filename is "{}"'.format(
                settings.outpath
            )
        )

    img = ImageLoader.create_from_args(settings).load_path(settings.imgpath)
    thumb = img.make_thumbnail_bitmap()

    with open(settings.outpath, "wb") as f:
        thumb.save(f, format="JPEG")


# "tile_allsky" subcommand


def tile_allsky_getparser(parser):
    from .image import ImageLoader

    ImageLoader.add_arguments(parser)

    parser.add_argument(
        "--name",
        metavar="NAME",
        default="Toasty",
        help="The image name to embed in the output WTML file (default: %(default)s)",
    )
    parser.add_argument(
        "--outdir",
        metavar="PATH",
        default=".",
        help="The root directory of the output tile pyramid (default: %(default)s)",
    )
    parser.add_argument(
        "--placeholder-thumbnail",
        action="store_true",
        help="Do not attempt to thumbnail the input image -- saves memory for large inputs",
    )
    parser.add_argument(
        "--projection",
        metavar="PROJTYPE",
        default="plate-carree",
        help="The projection type of the input image (default: %(default)s; choices: %(choices)s)",
        choices=[
            "plate-carree",
            "plate-carree-galactic",
            "plate-carree-ecliptic",
            "plate-carree-planet",
            "plate-carree-planet-zeroleft",
            "plate-carree-planet-zeroright",
            "plate-carree-panorama",
        ],
    )
    parser.add_argument(
        "--parallelism",
        "-j",
        metavar="COUNT",
        type=int,
        help="The parallelization level (default: use all CPUs if OS supports; specify `1` to force serial processing)",
    )
    parser.add_argument(
        "imgpath",
        metavar="PATH",
        help="The image file to be tiled",
    )
    parser.add_argument(
        "depth",
        metavar="DEPTH",
        type=int,
        help="The depth of the TOAST layer to sample",
    )


def tile_allsky_impl(settings):
    from .builder import Builder
    from .image import ImageLoader
    from .pyramid import PyramidIO

    img = ImageLoader.create_from_args(settings).load_path(settings.imgpath)
    pio = PyramidIO(settings.outdir)
    is_planet = False
    is_pano = False

    if settings.projection == "plate-carree":
        from .samplers import plate_carree_sampler

        sampler = plate_carree_sampler(img.asarray())
    elif settings.projection == "plate-carree-galactic":
        from .samplers import plate_carree_galactic_sampler

        sampler = plate_carree_galactic_sampler(img.asarray())
    elif settings.projection == "plate-carree-ecliptic":
        from .samplers import plate_carree_ecliptic_sampler

        sampler = plate_carree_ecliptic_sampler(img.asarray())
    elif settings.projection == "plate-carree-planet":
        from .samplers import plate_carree_planet_sampler

        sampler = plate_carree_planet_sampler(img.asarray())
        is_planet = True
    elif settings.projection == "plate-carree-planet-zeroleft":
        from .samplers import plate_carree_planet_zeroleft_sampler

        sampler = plate_carree_planet_zeroleft_sampler(img.asarray())
        is_planet = True
    elif settings.projection == "plate-carree-planet-zeroright":
        from .samplers import plate_carree_zeroright_sampler

        sampler = plate_carree_zeroright_sampler(img.asarray())
        is_planet = True
    elif settings.projection == "plate-carree-panorama":
        from .samplers import plate_carree_sampler

        sampler = plate_carree_sampler(img.asarray())
        is_pano = True
    else:
        die(
            "the image projection type {!r} is not recognized".format(
                settings.projection
            )
        )

    builder = Builder(pio)

    # Do the thumbnail first since for large inputs it can be the memory high-water mark!
    if settings.placeholder_thumbnail:
        builder.make_placeholder_thumbnail()
    else:
        builder.make_thumbnail_from_other(img)

    builder.toast_base(
        sampler,
        settings.depth,
        is_planet=is_planet,
        is_pano=is_pano,
        parallel=settings.parallelism,
        cli_progress=True,
    )
    builder.set_name(settings.name)
    builder.write_index_rel_wtml()

    print(
        f'Successfully tiled input "{settings.imgpath}" at level {builder.imgset.tile_levels}.'
    )
    print("To create parent tiles, consider running:")
    print()
    print(f"   toasty cascade --start {builder.imgset.tile_levels} {settings.outdir}")


# "tile_healpix" subcommand


def tile_healpix_getparser(parser):
    parser.add_argument(
        "--outdir",
        metavar="PATH",
        default=".",
        help="The root directory of the output tile pyramid",
    )
    parser.add_argument(
        "fitspath",
        metavar="PATH",
        help="The HEALPix FITS file to be tiled",
    )
    parser.add_argument(
        "depth",
        metavar="DEPTH",
        type=int,
        help="The depth of the TOAST layer to sample",
    )


def tile_healpix_impl(settings):
    from .builder import Builder
    from .pyramid import PyramidIO
    from .samplers import healpix_fits_file_sampler

    pio = PyramidIO(settings.outdir, default_format="npy")
    sampler = healpix_fits_file_sampler(settings.fitspath)
    builder = Builder(pio)
    builder.toast_base(sampler, settings.depth)
    builder.write_index_rel_wtml()

    print(
        f'Successfully tiled input "{settings.fitspath}" at level {builder.imgset.tile_levels}.'
    )
    print("To create parent tiles, consider running:")
    print()
    print(f"   toasty cascade --start {builder.imgset.tile_levels} {settings.outdir}")


# "tile_multi_tan" subcommand


def tile_multi_tan_getparser(parser):
    parser.add_argument(
        "--parallelism",
        "-j",
        metavar="COUNT",
        type=int,
        help="The parallelization level (default: use all CPUs; specify `1` to force serial processing)",
    )
    parser.add_argument(
        "--hdu-index",
        metavar="INDEX",
        type=int,
        default=0,
        help="Which HDU to load in each input FITS file",
    )
    parser.add_argument(
        "--outdir",
        metavar="PATH",
        default=".",
        help="The root directory of the output tile pyramid",
    )
    parser.add_argument(
        "paths",
        metavar="PATHS",
        action=EnsureGlobsExpandedAction,
        nargs="+",
        help="The FITS files with image data",
    )


def tile_multi_tan_impl(settings):
    from .builder import Builder
    from .collection import SimpleFitsCollection
    from .multi_tan import MultiTanProcessor
    from .pyramid import PyramidIO

    pio = PyramidIO(settings.outdir, default_format="fits")
    builder = Builder(pio)

    collection = SimpleFitsCollection(settings.paths, hdu_index=settings.hdu_index)

    mtp = MultiTanProcessor(collection)
    mtp.compute_global_pixelization(builder)
    mtp.tile(
        pio,
        parallel=settings.parallelism,
        cli_progress=True,
    )
    builder.write_index_rel_wtml()

    print(f"Successfully tiled inputs at level {builder.imgset.tile_levels}.")
    print("To create parent tiles, consider running:")
    print()
    print(f"   toasty cascade --start {builder.imgset.tile_levels} {settings.outdir}")


# "tile_study" subcommand


def tile_study_getparser(parser):
    from .image import ImageLoader

    ImageLoader.add_arguments(parser)

    parser.add_argument(
        "--name",
        metavar="NAME",
        default="Toasty",
        help="The image name to embed in the output WTML file (default: %(default)s)",
    )
    parser.add_argument(
        "--avm",
        action="store_true",
        help="Expect the input image to have AVM positioning tags",
    )
    parser.add_argument(
        "--fits-wcs",
        metavar="PATH",
        help="Get WCS information from this FITS file",
    )
    parser.add_argument(
        "--placeholder-thumbnail",
        action="store_true",
        help="Do not attempt to thumbnail the input image -- saves memory for large inputs",
    )
    parser.add_argument(
        "--outdir",
        metavar="PATH",
        default=".",
        help="The root directory of the output tile pyramid",
    )
    parser.add_argument(
        "imgpath",
        metavar="PATH",
        help="The study image file to be tiled",
    )


def tile_study_impl(settings):
    from .builder import Builder
    from .image import ImageLoader
    from .pyramid import PyramidIO

    img = ImageLoader.create_from_args(settings).load_path(settings.imgpath)
    pio = PyramidIO(settings.outdir, default_format=img.default_format)
    builder = Builder(pio)

    # First, prepare the tiling, because we can't correctly apply WCS until we
    # know the details of the tiling parameters

    tiling = builder.prepare_study_tiling(img)

    # Now deal with the WCS

    if settings.avm:
        # We don't *always* check for AVM because pyavm prints out a lot of junk
        # and may not be installed.
        try:
            from pyavm import AVM
        except ImportError:
            die("cannot use AVM data: you must install the `pyavm` package")

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                avm = AVM.from_image(settings.imgpath)
        except Exception:
            print(
                f"error: failed to read AVM tags of input `{settings.imgpath}`",
                file=sys.stderr,
            )
            raise

        builder.apply_avm_info(avm, img.width, img.height)
    elif settings.fits_wcs:
        try:
            from astropy.io import fits
            from astropy.wcs import WCS
        except ImportError:
            die("cannot use FITS WCS: you must install the `astropy` package")

        try:
            with fits.open(settings.fits_wcs) as hdul:
                # TODO: more flexibility in HDU choice:
                hdu = hdul[0]
                wcs = WCS(hdu, fobj=hdul)
        except Exception as e:
            die(f"cannot read WCS from FITS file `{settings.fits_wcs}`: {e}")

        wcs_width = hdu.header.get("IMAGEW")  # Astrometry.net
        wcs_height = hdu.header.get("IMAGEH")

        if wcs_width is None and len(hdu.shape) > 1:
            wcs_width = hdu.shape[-1]
            wcs_height = hdu.shape[-2]

        if wcs_width is None:
            warn(
                f"cannot infer image dimensions from WCS FITS file `{settings.fits_wcs}`; "
                f"unable to check consistency with input image"
            )
        elif img.shape[:2] != (wcs_height, wcs_width):
            warn(
                f"image `{settings.imgpath}` has shape {img.shape}, but "
                f"WCS reference file `{settings.fits_wcs}` has shape ({wcs_height}, {wcs_width}); "
                f"astrometry may not transfer correctly"
            )

        img._wcs = wcs  # <= hack alert, but I think this is OK
        img.ensure_negative_parity()
        builder.apply_wcs_info(img.wcs, img.width, img.height)
    elif img.wcs is not None:
        # Study images must have negative parity.
        img.ensure_negative_parity()
        builder.apply_wcs_info(img.wcs, img.width, img.height)
    else:
        builder.default_tiled_study_astrometry()

    # Do the thumbnail before the main image since for large inputs it can be
    # the memory high-water mark!
    if settings.placeholder_thumbnail:
        builder.make_placeholder_thumbnail()
    else:
        builder.make_thumbnail_from_other(img)

    # Finally, actually tile the image
    builder.execute_study_tiling(img, tiling, cli_progress=True)

    # Final metadata
    builder.set_name(settings.name)
    builder.write_index_rel_wtml()

    print(
        f'Successfully tiled input "{settings.imgpath}" at level {builder.imgset.tile_levels}.'
    )
    print("To create parent tiles, consider running:")
    print()
    print(f"   toasty cascade --start {builder.imgset.tile_levels} {settings.outdir}")


# "tile_wwtl" subcommand


def tile_wwtl_getparser(parser):
    from .image import ImageLoader

    ImageLoader.add_arguments(parser)

    parser.add_argument(
        "--name",
        metavar="NAME",
        default="Toasty",
        help="The image name to embed in the output WTML file (default: %(default)s)",
    )
    parser.add_argument(
        "--placeholder-thumbnail",
        action="store_true",
        help="Do not attempt to thumbnail the input image -- saves memory for large inputs",
    )
    parser.add_argument(
        "--outdir",
        metavar="PATH",
        default=".",
        help="The root directory of the output tile pyramid",
    )
    parser.add_argument(
        "wwtl_path",
        metavar="WWTL-PATH",
        help="The WWTL layer file to be processed",
    )


def tile_wwtl_impl(settings):
    from .builder import Builder
    from .pyramid import PyramidIO

    pio = PyramidIO(settings.outdir)
    builder = Builder(pio)
    img = builder.load_from_wwtl(settings, settings.wwtl_path, cli_progress=True)

    # Do the thumbnail first since for large inputs it can be the memory high-water mark!
    if settings.placeholder_thumbnail:
        builder.make_placeholder_thumbnail()
    else:
        builder.make_thumbnail_from_other(img)

    builder.set_name(settings.name)
    builder.write_index_rel_wtml()

    print(
        f'Successfully tiled input "{settings.wwtl_path}" at level {builder.imgset.tile_levels}.'
    )
    print("To create parent tiles, consider running:")
    print()
    print(f"   toasty cascade --start {builder.imgset.tile_levels} {settings.outdir}")


# "transform" subcommand


def transform_getparser(parser):
    subparsers = parser.add_subparsers(dest="transform_command")

    parser = subparsers.add_parser("fx3-to-rgb")
    parser.add_argument(
        "--parallelism",
        "-j",
        metavar="COUNT",
        type=int,
        help="The parallelization level (default: use all CPUs; specify `1` to force serial processing)",
    )
    parser.add_argument(
        "--start",
        metavar="DEPTH",
        type=int,
        help="How deep in the tile pyramid to proceed wth the transformation",
    )
    parser.add_argument(
        "--clip",
        "-c",
        metavar="NUMBER",
        type=float,
        default=1.0,
        help="The level at which to start flipping the floating-point data",
    )
    parser.add_argument(
        "--outdir",
        metavar="PATH",
        help="Output transformed data into this directory, instead of operating in-place",
    )
    parser.add_argument(
        "pyramid_dir",
        metavar="DIR",
        help="The directory containing the tile pyramid to transform",
    )

    parser = subparsers.add_parser("u8-to-rgb")
    parser.add_argument(
        "--parallelism",
        "-j",
        metavar="COUNT",
        type=int,
        help="The parallelization level (default: use all CPUs; specify `1` to force serial processing)",
    )
    parser.add_argument(
        "--start",
        metavar="DEPTH",
        type=int,
        help="How deep in the tile pyramid to proceed wth the transformation",
    )
    parser.add_argument(
        "--outdir",
        metavar="PATH",
        help="Output transformed data into this directory, instead of operating in-place",
    )
    parser.add_argument(
        "pyramid_dir",
        metavar="DIR",
        help="The directory containing the tile pyramid to transform",
    )


def transform_impl(settings):
    from .pyramid import PyramidIO

    if settings.transform_command is None:
        print('Run the "transform" command with `--help` for help on its subcommands')
        return

    if settings.transform_command == "fx3-to-rgb":
        pio = PyramidIO(settings.pyramid_dir)
        pio_out = None

        if settings.outdir is not None:
            pio_out = PyramidIO(settings.outdir)

        from .transform import f16x3_to_rgb

        f16x3_to_rgb(
            pio,
            settings.start,
            clip=settings.clip,
            pio_out=pio_out,
            parallel=settings.parallelism,
            cli_progress=True,
        )
    elif settings.transform_command == "u8-to-rgb":
        pio = PyramidIO(settings.pyramid_dir)
        pio_out = None

        if settings.outdir is not None:
            pio_out = PyramidIO(settings.outdir)

        from .transform import u8_to_rgb

        u8_to_rgb(
            pio,
            settings.start,
            pio_out=pio_out,
            parallel=settings.parallelism,
            cli_progress=True,
        )
    else:
        die('unrecognized "transform" subcommand ' + settings.transform_command)


# "view" subcommand
#
# This largely duplicates `wwtdatatool preview` in the `wwt_data_formats`
# package. The difference is that we automagically tile and output the
# `index_rel.wtml`, while `wwtdatatool` requires it to be preexisting.


def view_getparser(parser):
    from .collection import CollectionLoader

    CollectionLoader.add_arguments(parser)

    parser.add_argument(
        "--parallelism",
        "-j",
        metavar="COUNT",
        type=int,
        help="The parallelization level (default: use all CPUs; specify `1` to force serial processing)",
    )
    parser.add_argument(
        "--browser",
        "-b",
        metavar="BROWSER-TYPE",
        help="The type of browser to use for the viewer (as per Python webbrowser)",
    )
    parser.add_argument(
        "--appurl",
        metavar="URL",
        help="The URL of the app to use (intended for developers)",
    )
    parser.add_argument(
        "paths",
        metavar="PATHS",
        action=EnsureGlobsExpandedAction,
        nargs="+",
        help="The FITS file(s) with image data",
    )


def view_impl(settings):
    from wwt_data_formats.server import preview_wtml
    from .collection import CollectionLoader
    from .fits_tiler import FitsTiler

    coll = CollectionLoader.create_from_args(settings).load_paths(settings.paths)

    # Ignore any astropy WCS/FITS warnings, which can spew a lot of annoying output.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tiler = FitsTiler(coll)
        tiler.tile(cli_progress=True)

    preview_wtml(
        os.path.join(tiler.out_dir, "index_rel.wtml"),
        browser=settings.browser,
        app_type="research",
        app_url=settings.appurl,
    )


# The CLI driver:


def entrypoint(args=None):
    """The entrypoint for the \"toasty\" command-line interface.

    Parameters
    ----------
    args : iterable of str, or None (the default)
      The arguments on the command line. The first argument should be
      a subcommand name or global option; there is no ``argv[0]``
      parameter.

    """
    # Set up the subcommands. We use locals() and globals() in a fairly gross
    # way to avoid circular import issues in Sphinx.

    from .pipeline.cli import pipeline_getparser, pipeline_impl

    names = dict(locals())
    names.update(globals())

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand")
    commands = set()

    for py_name, value in names.items():
        if py_name.endswith("_getparser"):
            cmd_name = py_name[:-10].replace("_", "-")
            subparser = subparsers.add_parser(cmd_name)
            value(subparser)
            commands.add(cmd_name)

    # What did we get?

    settings = parser.parse_args(args)

    if settings.subcommand is None:
        print("Run me with --help for help. Allowed subcommands are:")
        print()
        for cmd in sorted(commands):
            print("   ", cmd)
        return

    py_name = settings.subcommand.replace("-", "_")

    impl = names.get(py_name + "_impl")
    if impl is None:
        die('no such subcommand "{}"'.format(settings.subcommand))

    # OK to go!

    impl(settings)
