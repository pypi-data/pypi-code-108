# -*- mode: python; coding: utf-8 -*-
# Copyright 2019-2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import numpy as np
import numpy.testing as nt
import os.path
import pytest
import sys
from xml.etree import ElementTree as etree

from . import assert_xml_elements_equal, test_path
from ..builder import Builder
from .. import cli
from .. import collection
from .. import multi_tan


try:
    from astropy.io import fits

    HAS_ASTRO = True
except ImportError:
    HAS_ASTRO = False


try:
    import reproject

    HAS_REPROJECT = True
except ImportError:
    HAS_REPROJECT = False


class TestMultiTan(object):
    WTML = """
<Folder Browseable="True" Group="Explorer" Name="Toasty" Searchable="True">
    <Place
        Angle="0"
        AngularSize="0"
        DataSetType="Sky"
        Dec="0.7438249862258411"
        Magnitude="0"
        Name="Toasty"
        Opacity="100"
        RA="14.41975153073335"
        Rotation="0"
        Thumbnail="thumb.jpg"
        ZoomLevel="0.2437119999998555"
    >
        <ForegroundImageSet>
            <ImageSet
                BandPass="Visible"
                BaseDegreesPerTile="0.023893333333319167"
                BaseTileLevel="0"
                BottomsUp="False"
                CenterX="216.2962962963"
                CenterY="0.74380165289257"
                DataSetType="Sky"
                ElevationModel="False"
                FileType=".fits"
                Generic="False"
                Name="Toasty"
                OffsetX="2.33333333333195e-05"
                OffsetY="2.33333333333195e-05"
                Projection="Tan"
                QuadTreeMap=""
                Rotation="-0"
                Sparse="True"
                StockSet="False"
                TileLevels="1"
                Url="{1}/{3}/{3}_{2}.fits"
                WidthFactor="2"
            >
                <ThumbnailUrl>thumb.jpg</ThumbnailUrl>
            </ImageSet>
        </ForegroundImageSet>
    </Place>
</Folder>"""

    # Gross workaround for platform differences in the XML output.

    if sys.platform == "darwin":
        WTML = WTML.replace('Dec="0.7438249862258411"', 'Dec="0.743824986225841"')

    # Back to the non-gross stuff.

    def setup_method(self, method):
        from tempfile import mkdtemp

        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree

        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def test_basic(self):
        coll = collection.SimpleFitsCollection([test_path("wcs512.fits.gz")])

        proc = multi_tan.MultiTanProcessor(coll)

        from ..pyramid import PyramidIO

        pio = PyramidIO(self.work_path("basic"), default_format="fits")

        builder = Builder(pio)

        proc.compute_global_pixelization(builder)
        proc.tile(pio)

    BARY_SLICES = [
        (slice(0, 128), slice(0, 128)),
        (slice(0, 128), slice(128, None)),
        (slice(128, None), slice(0, 128)),
        (slice(128, None), slice(128, None)),
    ]

    def maybe_test_barycenter(self, path, bary_expected):
        """
        Check the barycenters of four 128x128 quadrants of a tile file. The idea
        here is that if we introduce a problem with vertical flips in tiled FITS
        processing, we'll detect it here.
        """

        if not HAS_ASTRO:
            return

        with fits.open(path) as hdul:
            data = hdul[0].data

        data[~np.isfinite(data)] = 0.0
        bary_observed = []

        for islice in self.BARY_SLICES:
            idata = data[islice]
            yidx, xidx = np.indices((128, 128))
            xbary = (idata * xidx).sum() / idata.sum()
            ybary = (idata * yidx).sum() / idata.sum()
            bary_observed.append((xbary, ybary))

        nt.assert_array_almost_equal(bary_observed, bary_expected, decimal=5)

    WCS512_BARYDATA = [
        (63.44949378800272, 64.40535387506924),
        (63.24744175084746, 63.67473452789256),
        (65.22950207855361, 63.35629429568745),
        (62.027396724898814, 62.815937534782144),
    ]

    def test_basic_cli(self):
        """
        Test the CLI interface. We don't go out of our way to validate the
        computations in detail -- that's for the unit tests that probe the
        module directly.
        """
        expected = etree.fromstring(
            self.WTML.replace('Thumbnail="thumb.jpg"', "").replace(
                "<ThumbnailUrl>thumb.jpg</ThumbnailUrl>",
                "<ThumbnailUrl></ThumbnailUrl>",
            )
        )

        args = [
            "tile-multi-tan",
            "--hdu-index",
            "0",
            "--outdir",
            self.work_path("basic_cli"),
            test_path("wcs512.fits.gz"),
        ]
        cli.entrypoint(args)

        with open(
            self.work_path("basic_cli", "index_rel.wtml"), "rt", encoding="utf8"
        ) as f:
            observed = etree.fromstring(f.read())

        assert_xml_elements_equal(observed, expected)

        args = [
            "cascade",
            "--start",
            "1",
            self.work_path("basic_cli"),
        ]
        cli.entrypoint(args)

        self.maybe_test_barycenter(
            self.work_path("basic_cli", "0", "0", "0_0.fits"), self.WCS512_BARYDATA
        )

    def test_study_cli(self):
        """
        Test tile-study on FITS. This should properly go in test_study.py, but
        this file is the one that has the reference WTML information.
        """
        expected = etree.fromstring(self.WTML)

        args = [
            "tile-study",
            "--placeholder-thumbnail",
            "--outdir",
            self.work_path("study_cli"),
            test_path("wcs512.fits.gz"),
        ]
        cli.entrypoint(args)

        with open(
            self.work_path("study_cli", "index_rel.wtml"), "rt", encoding="utf8"
        ) as f:
            observed = etree.fromstring(f.read())

        assert_xml_elements_equal(observed, expected)

        args = [
            "cascade",
            "--start",
            "1",
            self.work_path("study_cli"),
        ]
        cli.entrypoint(args)

        self.maybe_test_barycenter(
            self.work_path("study_cli", "0", "0", "0_0.fits"), self.WCS512_BARYDATA
        )

    @pytest.mark.skipif("not HAS_REPROJECT")
    def test_as_multi_wcs(self):
        """
        Once again, this doesn't super belong here, but this is where we have
        the reference data. We don't compare the WTML contents here since the
        reprojection isn't going to preserve the WCS in detail.
        """
        from .. import builder, collection, multi_wcs, pyramid

        reproject_function = reproject.reproject_interp
        outdir = self.work_path("as_multi_wcs")

        pio = pyramid.PyramidIO(outdir, default_format="fits")
        bld = builder.Builder(pio)
        coll = collection.SimpleFitsCollection(
            [test_path("wcs512.fits.gz")], hdu_index=0
        )
        proc = multi_wcs.MultiWcsProcessor(coll)
        proc.compute_global_pixelization(bld)
        proc.tile(pio, reproject_function, cli_progress=False, parallel=1)
        bld.write_index_rel_wtml()

        args = [
            "cascade",
            "--start",
            "1",
            self.work_path("as_multi_wcs"),
        ]
        cli.entrypoint(args)

        self.maybe_test_barycenter(
            self.work_path("as_multi_wcs", "0", "0", "0_0.fits"), self.WCS512_BARYDATA
        )
