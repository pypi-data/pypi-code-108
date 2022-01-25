# -*- mode: python; coding: utf-8 -*-
# Copyright 2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Collections of related input images.

Some Toasty processing tasks operate over collections of input images that are
related in some way. This module provides standardized mechanisms for
manipulating such collections. In particular, it provides a framework for
scanning over image "descriptions" without reading in the complete image data.
This can be useful because many collection-related operations want to do an
initial pass over the collection to gather some global information, then a
second pass with the actual data processing.

For interactive usage or in basic scripts, use :func:`load` for maximum
convenience. For command-line interfaces, use the :class:`CollectionLoader`
helper to provide a uniform collection-loading interface.
"""

__all__ = """
load
CollectionLoader
ImageCollection
RubinDirectoryCollection
SimpleFitsCollection
""".split()

from abc import ABC
from glob import glob
import numpy as np
from os.path import join
import warnings

from .image import Image, ImageDescription, ImageMode

MATCH_HEADERS = [
    "CTYPE1",
    "CTYPE2",
    "CRVAL1",
    "CRVAL2",
    "CDELT1",
    "CDELT2",
]


class ImageCollection(ABC):
    def descriptions(self):
        """
        Generate a sequence of :class:`toasty.image.ImageDescription` items
        associated with this collection.

        Each description will have an added string attribute ``collection_id``
        that gives a unique textual identifer for the item in the collection.

        Unlike :meth:`ImageCollection.images`, this function does cause the full
        data for each image to be loaded.
        """
        raise NotImplementedError()

    def images(self):
        """
        Generate a sequence of :class:`toasty.image.Image` items associated with
        this collection.

        Each image will have an added string attribute ``collection_id`` that
        gives a unique textual identifer for the item in the collection.
        """
        raise NotImplementedError()

    def export_simple(self):
        """
        Export information about the paths in this collection, if possible.

        Returns
        -------
        A list of tuples ``(fits_file_path, hdu_index)``.

        Raises
        ------
        Raises an exception if it is not possible to meaningfully export this
        particular collection in the "simple" format. This could be the case,
        for instance, if the inputs live in memory and do not have filesystem
        paths.

        Notes
        -----
        Sometimes, you need to expose information about a FITS collection to a
        tool outside of Toasty: for instance, to invoke ``hipsgen`` to generate
        a HiPS tiling. This function gives the information needed to invoke the
        tool, or raises an error if it can't be done correctly. This method
        makes it possible to handle image collections using Toasty's framework,
        but "drop down" to a simpler representation when needed.
        """
        raise Exception("this ImageCollection cannot be exported in the simple format")

    def _is_multi_tan(self):
        ref_headers = None

        for desc in self.descriptions():
            # For figuring out the tiling properties, we need to ensure that
            # we're working in top-down mode everywhere.
            desc.ensure_negative_parity()

            header = desc.wcs.to_header()

            if ref_headers is None:
                ref_headers = {}

                for h in MATCH_HEADERS:
                    ref_headers[h] = header[h]

                if (
                    ref_headers["CTYPE1"] != "RA---TAN"
                    or ref_headers["CTYPE2"] != "DEC--TAN"
                ):
                    return False
            else:
                for h in MATCH_HEADERS:
                    expected = ref_headers[h]
                    observed = header[h]

                    if observed != expected:
                        return False

        return True


class SimpleFitsCollection(ImageCollection):
    def __init__(self, paths, hdu_index=None, blankval=None, **kwargs):
        self._paths = list(paths)
        self._hdu_index = hdu_index
        self._blankval = blankval

    def _scan_hdus(self):
        from astropy.io import fits

        for path_index, fits_path in enumerate(self._paths):
            with fits.open(fits_path) as hdul:
                if isinstance(self._hdu_index, int):
                    hdu_index = self._hdu_index
                    hdu = hdul[self._hdu_index]
                elif self._hdu_index is not None:
                    hdu_index = self._hdu_index[path_index]
                    hdu = hdul[self._hdu_index]
                else:
                    for hdu_index, hdu in enumerate(hdul):
                        if (
                            hasattr(hdu, "shape")
                            and len(hdu.shape) > 1
                            and type(hdu) is not fits.hdu.table.BinTableHDU
                        ):
                            break

                if type(hdu) is fits.hdu.table.BinTableHDU:
                    raise Exception(
                        f"cannot process input `{fits_path}`: Did not find any HDU with image data"
                    )

                yield fits_path, hdu_index, hdu

    def export_simple(self):
        # We're allowed to return a generator, but we listify this so that the
        # FITS files are all closed promptly.
        return [(t[0], t[1]) for t in self._scan_hdus()]

    def _load(self, actually_load_data):
        from astropy.wcs import WCS

        for fits_path, _hdu_index, hdu in self._scan_hdus():
            # Hack for DASCH files, and potentially others. These have TPV
            # polynomial distortions but do not use the magic projection
            # keyword that causes Astropy to accept them. We don't try to be
            # very flexible in how we activate the hack since we don't want
            # to futz with things unnecessarily.

            if (
                "PV1_5" in hdu.header
                and hdu.header["CTYPE1"] == "RA---TAN"
                and hdu.header["CTYPE2"] == "DEC--TAN"
            ):
                hdu.header["CTYPE1"] = "RA---TPV"
                hdu.header["CTYPE2"] = "DEC--TPV"

            # End hack(s).

            wcs = WCS(hdu.header)
            shape = hdu.shape

            # We need to make sure the data are 2D celestial, since that's
            # what our image code and `reproject` (if it's being used) expect.

            full_wcs = None
            keep_axes = None

            if wcs.naxis != 2:
                if not wcs.has_celestial:
                    raise Exception(
                        f"cannot process input `{fits_path}`: WCS cannot be reduced to 2D celestial"
                    )

                full_wcs = wcs
                wcs = full_wcs.celestial

                # note: get_axis_types returns axes in FITS order, innermost first
                keep_axes = [
                    t.get("coordinate_type") == "celestial"
                    for t in full_wcs.get_axis_types()[::-1]
                ]

                for keep, axlen in zip(keep_axes, shape):
                    if not keep and axlen != 1:
                        raise Exception(
                            f"cannot process input `{fits_path}`: found a non-celestial axis with size other than 1"
                        )

            # OK, almost there. Are we loading data or just the descriptor?

            if actually_load_data:
                data = hdu.data

                if full_wcs is not None:  # need to subset?
                    data = data[tuple(slice(None) if k else 0 for k in keep_axes)]

                if self._blankval is not None:
                    data[data == self._blankval] = np.nan

                result = Image.from_array(data, wcs=wcs, default_format="fits")
            else:
                if full_wcs is not None:  # need to subset?
                    shape = tuple(t[1] for t in zip(keep_axes, shape) if t[0])

                if hasattr(hdu, "dtype"):
                    mode = ImageMode.from_array_info(shape, hdu.dtype)
                else:
                    mode = None  # CompImageHDU doesn't have dtype

                result = ImageDescription(mode=mode, shape=shape, wcs=wcs)

            result.collection_id = fits_path
            yield result

    def descriptions(self):
        return self._load(False)

    def images(self):
        return self._load(True)


class RubinDirectoryCollection(ImageCollection):
    """
    Load up imagery from a directory containing FITS files capturing a Rubin
    Observatory tract.

    The directory will be searched for files whose names end in ``.fits``. In
    each of those files, the HDUs beyond the first will be treated as separate
    science images that should be individually loaded. The images will be
    trimmed according to their ``DATASEC`` specification before being returned.

    This class requires the ``ccdproc``  package to trim FITS CCD datasets.
    """

    def __init__(self, dirname, unit=None):
        self._dirname = dirname
        self._unit = unit

    def _load(self, actually_load_data):
        from astropy.io import fits
        from astropy.nddata import ccddata
        import ccdproc

        for fits_path in glob(join(self._dirname, "*.fits")):
            # `astropy.nddata.ccddata.fits_ccddata_reader` only opens FITS from
            # filenames, not from an open HDUList, which means that creating
            # multiple CCDDatas from the same FITS file rapidly becomes
            # inefficient. So, we emulate its logic.

            with fits.open(fits_path) as hdu_list:
                for idx, hdu in enumerate(hdu_list):
                    if idx == 0:
                        header0 = hdu.header
                    else:
                        hdr = hdu.header
                        hdr.extend(header0, unique=True)

                        # This ccddata function often generates annoying warnings
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            hdr, wcs = ccddata._generate_wcs_and_update_header(hdr)

                        # We can't use `ccdproc.trim_image()` without having a
                        # CCDData in hand, so we have to create a fake empty
                        # array even when we're not actually loading any data.
                        #
                        # Note: we skip all the unit-handling logic from
                        # `fits_ccddata_reader` here basically since the LSST
                        # sim data I'm using don't have anything useful.

                        if actually_load_data:
                            data = hdu.data

                            if data.dtype.kind == "i":
                                data = data.astype(np.float32)
                        else:
                            data = np.empty(hdu.shape, dtype=np.void)

                        ccd = ccddata.CCDData(data, meta=hdr, unit=self._unit, wcs=wcs)
                        ccd = ccdproc.trim_image(
                            ccd, fits_section=ccd.header["DATASEC"]
                        )
                        data = ccd.data
                        shape = data.shape
                        wcs = ccd.wcs

                        if actually_load_data:
                            mode = ImageMode.from_array_info(shape, data.dtype)
                        elif hasattr(hdu, "dtype"):
                            mode = ImageMode.from_array_info(shape, hdu.dtype)
                        else:
                            mode = None  # CompImageHDU doesn't have dtype

                        if actually_load_data:
                            result = Image.from_array(
                                data, wcs=wcs, default_format="fits"
                            )
                        else:
                            result = ImageDescription(mode=mode, shape=shape, wcs=wcs)

                        result.collection_id = f"{fits_path}:{idx}"
                        yield result

    def descriptions(self):
        return self._load(False)

    def images(self):
        return self._load(True)


class CollectionLoader(object):
    """
    A class defining how to load a collection of images.

    This is implemented as its own class since there can be some options
    involved, and we want to provide a centralized place for handling them all.

    For interactive usage, use :func:`load`, which is optimized for easy
    invocation. This class is best used in command-line interfaces that interact
    with collections of FITS files.
    """

    blankval = None
    hdu_index = None

    @classmethod
    def add_arguments(cls, parser):
        """
        Add standard collection-loading options to an argparse parser object.

        Parameters
        ----------
        parser : :class:`argparse.ArgumentParser`
            The argument parser to modify

        Returns
        -------
        The :class:`CollectionLoader` class (for chainability).

        Notes
        -----
        If you are writing a command-line interface that takes an image
        collection as an input, use this function to wire in to standardized
        image-loading infrastructure and options.
        """

        parser.add_argument(
            "--hdu-index",
            metavar="INDEX[,INDEX...]",
            help="Which HDU to load in each input FITS file",
        )
        parser.add_argument(
            "--blankval",
            metavar="NUMBER",
            help="An image value to treat as undefined in all FITS inputs",
        )
        return cls

    @classmethod
    def create_from_args(cls, settings):
        """
        Process standard collection-loading options to create a
        :class:`CollectionLoader`.

        Parameters
        ----------
        settings : :class:`argparse.Namespace`
            Settings from processing command-line arguments

        Returns
        -------
        A new :class:`CollectionLoader` initialized with the settings.
        """
        loader = cls()

        if settings.hdu_index is not None:
            # Note: semantically we treat `hdu_index = 2` differently than
            # `hdu_index = [2]`: the first means use HDU 2 in all files, the
            # second means use HDU 2 in the first file. But we don't have a way
            # to distinguish between the two when parsing the CLI argument.
            try:
                index = int(settings.hdu_index)
            except ValueError:
                try:
                    index = list(map(int, settings.hdu_index.split(",")))
                except Exception:
                    raise Exception(
                        "cannot parse `--hdu-index` setting `{settings.hdu_index!r}`: should "
                        "be a comma-separated list of one or more integers"
                    )

            loader.hdu_index = index

        if settings.blankval is not None:
            try:
                # If integer input image, want to avoid roundoff/precision issues
                v = int(settings.blankval)
            except ValueError:
                try:
                    v = float(settings.blankval)
                except ValueError:
                    raise Exception(
                        "cannot parse `--blankval` setting `{settings.blankval!r}`: should "
                        "be a number"
                    )

            loader.blankval = v

        return loader

    def load_paths(self, paths):
        """
        Set up an `ImageCollection` based on a list of input filesystem paths.

        Parameters
        ----------
        paths : iterable of str
            The filesystem paths to load.

        Returns
        -------
        A new :class:`ImageCollection`.
        """
        paths = list(str(p) for p in paths)

        # This is where more cleverness will go if/when needed.

        return SimpleFitsCollection(
            paths,
            hdu_index=self.hdu_index,
            blankval=self.blankval,
        )


def load(input, hdu_index=None, blankval=None):
    """
    Set up a collection of FITS files as sensibly as possible.

    Parameters
    ----------
    input : str or iterable of str
        The filesystem path(s) of the FITS file(s) to load.
    hdu_index : optional int or list of int, default None
        Which HDU to load. If a scalar, the same index will be
        used in every input file; if a list, corresponding values
        will be used for each input path. If unspecified, Toasty
        will guess.
    blankval : optional number, default None
        An image value to treat as undefined in all FITS inputs.

    Returns
    -------
    A new :class:`ImageCollection`.

    Notes
    -----
    This function is meant to be called interactively from environments like
    Jupyter. Its goal is to "do the right thing" as reliably as possible,
    requiring as little user guidance as needed.
    """
    # One day this function might add more custom logic? But right now we're just
    # providing a streamlined way to access the CollectionLoader.

    if isinstance(input, str):
        input = [input]

    input = list(input)
    loader = CollectionLoader()
    loader.hdu_index = hdu_index
    loader.blankval = blankval
    return loader.load_paths(input)
