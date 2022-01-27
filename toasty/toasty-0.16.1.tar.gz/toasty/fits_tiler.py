# -*- mode: python; coding: utf-8 -*-
# Copyright 2013-2021 Chris Beaumont and the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Tools for automagically tiling FITS files.

Instead of using these interfaces directly, most users should probably use the
all-in-one function :func:`toasty.tile_fits`.
"""

import os.path
from shutil import copyfile
from subprocess import Popen, PIPE, STDOUT, run
import tempfile

from astropy.coordinates import Angle
from astropy.utils.data import download_file
import reproject
from wwt_data_formats.enums import ProjectionType

from toasty import builder, pyramid, multi_tan, multi_wcs

__all__ = [
    "FitsTiler",
]


class FitsTiler(object):
    """
    A class to manage the tiling of a FITS file collection.

    Parameters
    ----------
    coll : :class:`~toasty.collection.ImageCollection`
        A collection of one or more input FITS files
    out_dir : optional str, default None
        The output directory for the tiled FITS data.
        If None, a sensible default next to the first input file
        will be chosen.
    force_hipsgen : optional bool, default False
        If true, the tiling process will be forced to use the
        HiPS format and the ``hipsgen`` tool.
    force_tan : optional bool, default False
        If true, the tiling process will be forced to target the
        WWT "study" format with a tangential projection.
    """

    coll = None
    "The input :class:`~toasty.collection.ImageCollection`."

    out_dir = None
    """The output directory.

    This can be set upon creation or left as None. If the latter, this attribute
    will be filled in after a successful invocation of the :meth:`tile` method.
    """

    force_hipsgen = False
    """Whether the tiling process will be forced to use the HiPS format and the
    ``hipsgen`` tool."""

    force_tan = False
    """Whether the tiling process will be forced to target the WWT "study"
    format with a tangential projection."""

    builder = None
    """A :class:`~toasty.builder.Builder` describing the output dataset.

    This attribute is None upon creation of a class instance. It will be filled
    in after a successful invocation of the :meth:`tile` method.
    """

    def __init__(
        self,
        coll,
        out_dir=None,
        force_hipsgen=False,
        force_tan=False,
    ):
        self.coll = coll
        self.out_dir = out_dir
        self.force_hipsgen = force_hipsgen
        self.force_tan = force_tan

    def should_use_hipsgen(self):
        """
        Determine whether the tiling process should use ``hipsgen``.
        """
        return self.force_hipsgen or (
            self._fits_covers_large_area()
            and self._is_java_installed()
            and not self.force_tan
        )

    def tile(
        self,
        cli_progress=False,
        override=False,
        **kwargs,
    ):
        """
        Process the collection into a tile pyramid using either a common
        tangential projection or HiPSgen.

        Parameters
        ----------
        cli_progress : optional boolean, defaults to False
            If true, progress messages will be printed as the FITS files
            are being processed.
        override : optional boolean, defaults to False
            By default, if the output directory already exists, the tiling
            process is skipped. If this argument is true, an existing
            output directory will be deleted if it exists.
        kwargs
            Settings for the tiling process. For example, ``blankval``.

        Returns
        -------
        Self.

        Notes
        -----
        After this function returns, the attributes :attr:`out_dir` and
        :attr:`builder` of *self* will be fully initialized.
        """

        use_hipsgen = self.should_use_hipsgen()

        if self.out_dir is None:
            # Kind of hacky here ... Note that export_simple() might return a
            # generator so we can't just index the return value.
            for tup in self.coll.export_simple():
                first_fits_path = tup[0]
                break

            first_file_name = first_fits_path.split(".gz")[0]
            self.out_dir = first_file_name[: first_file_name.rfind(".")] + "_tiled"

            if use_hipsgen:
                self.out_dir += "_HiPS"

        if cli_progress:
            print(f"Tile output directory is `{self.out_dir}`")

        pio = pyramid.PyramidIO(self.out_dir, default_format="fits")
        self.builder = builder.Builder(pio)
        self.builder.set_name(self.out_dir.split("/")[-1])

        if os.path.isdir(self.out_dir):
            if override:
                if cli_progress:
                    print(f"Tile directory already exists -- removing")

                import shutil

                shutil.rmtree(self.out_dir)
            else:
                if cli_progress:
                    print("Tile directory already exists -- reusing")

                if os.path.exists(os.path.join(self.out_dir, "properties")):
                    self._copy_hips_properties_to_builder()

                return

        if use_hipsgen:
            self._tile_hips(cli_progress)
        else:
            self._tile_tan(cli_progress, **kwargs)

        self.builder.write_index_rel_wtml()
        return self

    def _tile_tan(self, cli_progress, **kwargs):
        if self.coll._is_multi_tan():
            if cli_progress:
                print("Tiling base layer in multi-TAN mode (step 1 of 2)")

            tile_processor = multi_tan.MultiTanProcessor(self.coll)
            tile_processor.compute_global_pixelization(self.builder)
            tile_processor.tile(self.builder.pio, cli_progress=cli_progress, **kwargs)
        else:
            if cli_progress:
                print("Tiling base layer in multi-WCS mode (step 1 of 2)")

            tile_processor = multi_wcs.MultiWcsProcessor(self.coll)
            tile_processor.compute_global_pixelization(self.builder)
            tile_processor.tile(
                self.builder.pio,
                reproject.reproject_interp,
                cli_progress=cli_progress,
                **kwargs,
            )

        if cli_progress:
            print("Downsampling (step 2 of 2)")

        self.builder.cascade(cli_progress=cli_progress, **kwargs)

    def _tile_hips(self, cli_progress):
        cached_hipsgen_path = download_file(
            "https://aladin.unistra.fr/java/Hipsgen.jar",
            show_progress=cli_progress,
            cache=True,
            pkgname="toasty",
        )

        # Get the "simple export" version of the collection that we can pass to
        # hipsgen.

        try:
            export_info = self.coll.export_simple()
        except Exception as e:
            raise Exception(
                'cannot export FITS collection in "simple" mode for passing to hipsgen'
            ) from e

        fits_paths = []
        hdu_indexes = []

        for tup in export_info:
            fits_paths.append(tup[0])
            hdu_indexes.append(str(tup[1]))

        # If we give hipsgen a relative output directory it will end up
        # inside `in_dir`
        abs_out_dir = os.path.abspath(self.out_dir)
        out_base = os.path.basename(self.out_dir)

        with self._create_hipsgen_input_dir(fits_paths) as in_dir_path:
            # Some antivirus programs (at least Avast) disallow "java -jar"
            # invocation of files lacking ".jar" file extensions. Since we
            # cannot set the file extension of the file in the astropy cache,
            # we have to create a temporary copy with a ".jar" extension.
            hipsgen_path = os.path.join(in_dir_path, "hipsgen.jar")
            copyfile(cached_hipsgen_path, hipsgen_path)
            argv = [
                "java",
                "-jar",
                "{0}".format(hipsgen_path),
                "in={0}".format(in_dir_path),
                "out={0}".format(abs_out_dir),
                "creator_did=ivo://aas.wwt.toasty/{0}".format(out_base),
                "hdu={0}".format(",".join(hdu_indexes)),
                "INDEX",
                "TILES",
            ]

            p = Popen(
                argv,
                stdout=PIPE,
                stderr=STDOUT,
                shell=False,
            )

            # Even if we don't want to print the output, this loop is still useful since it waits until the HiPSgen process
            # is completed.
            for line in p.stdout:
                if cli_progress:
                    print(line.decode("UTF-8"), end="")

            if p.wait() != 0:
                if cli_progress:
                    m = "see its output printed above"
                else:
                    m = "set `cli_progress=True` to see its output"
                raise Exception(f"an error occurred running hipsgen; {m}")

        if not os.path.isdir(self.out_dir):
            if cli_progress:
                m = "see its output printed above"
            else:
                m = "set `cli_progress=True` to see its output"
            raise Exception(
                f"output directory `{self.out_dir}` does not exist, meaning `hipsgen` probably failed; {m}"
            )

        self._copy_hips_properties_to_builder()

    def _fits_covers_large_area(self):
        """
        Here, "large" means "large enough that the TAN projection 'study' mode
        yields visually unacceptable results."
        """
        corners = []

        for desc in self.coll.descriptions():
            corners.append(desc.wcs.pixel_to_world(0, 0))
            corners.append(desc.wcs.pixel_to_world(desc.shape[0], 0))
            corners.append(desc.wcs.pixel_to_world(desc.shape[0], desc.shape[1]))
            corners.append(desc.wcs.pixel_to_world(0, desc.shape[1]))

        # This is a naive N^2 search but the input would have to be pretty
        # pathological for it to make sense to try to be more efficient here.

        max_distance = Angle("0d")
        for compare_index in range(len(corners)):
            for index in range(compare_index + 1, len(corners)):
                distance = corners[compare_index].separation(corners[index])
                if distance > max_distance:
                    max_distance = distance

        return max_distance > Angle("20d")

    def _is_java_installed(self):
        java_version = run(
            ["java", "-version"], capture_output=True, text=True, check=True
        )
        return (
            "version" in java_version.stdout.lower()
            or "version" in java_version.stderr.lower()
        )

    def _create_hipsgen_input_dir(self, fits_list):
        dir = tempfile.TemporaryDirectory()

        for fits_file in fits_list:
            link_name = os.path.basename(fits_file)
            absolute_path = os.path.abspath(fits_file)
            link_path = os.path.join(dir.name, link_name)
            os.symlink(src=absolute_path, dst=link_path)

        return dir

    def _copy_hips_properties_to_builder(self):
        hips_properties = dict()

        with open(os.path.join(self.out_dir, "properties")) as prop:
            for line in prop:
                if line[0] != "#":
                    key_value_pair = line.split("=")
                    hips_properties[key_value_pair[0].strip()] = key_value_pair[
                        1
                    ].strip()

        self.builder.imgset.projection = ProjectionType.HEALPIX
        self.builder.imgset.file_type = "fits"
        self.builder.imgset.tile_levels = int(hips_properties["hips_order"])
        self.builder.place.dec_deg = float(hips_properties["hips_initial_dec"])
        self.builder.place.ra_hr = float(hips_properties["hips_initial_ra"]) / 15.0
        self.builder.place.zoom_level = float(hips_properties["hips_initial_fov"])
        self.builder.imgset.center_x = float(hips_properties["hips_initial_ra"])
        self.builder.imgset.center_y = float(hips_properties["hips_initial_dec"])
        self.builder.imgset.base_degrees_per_tile = float(
            hips_properties["hips_initial_fov"]
        )
        pixel_cut = hips_properties["hips_pixel_cut"].split(" ")
        self.builder.imgset.pixel_cut_low = float(pixel_cut[0])
        self.builder.imgset.pixel_cut_high = float(pixel_cut[1])
        data_range = hips_properties["hips_data_range"].split(" ")
        self.builder.imgset.data_min = float(data_range[0])
        self.builder.imgset.data_max = float(data_range[1])

        self.builder.imgset.url = "Norder{0}/Dir{1}/Npix{2}"
