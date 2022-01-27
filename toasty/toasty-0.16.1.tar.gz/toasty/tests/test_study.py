# -*- mode: python; coding: utf-8 -*-
# Copyright 2020-2022 the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import numpy as np
import os.path
import pytest
import sys

from . import HAS_AVM, assert_xml_elements_equal, test_path
from .. import cli
from .. import study


class TestStudy(object):
    WTML = """<?xml version='1.0' encoding='UTF-8'?>
<Folder
    Browseable="True"
    Group="Explorer"
    Name="Toasty"
    Searchable="True"
>
    <Place
        Angle="0"
        AngularSize="0"
        DataSetType="Sky"
        Dec="0"
        Magnitude="0"
        Name="Toasty"
        Opacity="100"
        RA="0"
        Rotation="0"
        Thumbnail="thumb.jpg"
        ZoomLevel="1"
    >
        <ForegroundImageSet>
            <ImageSet
                BandPass="Visible"
                BaseDegreesPerTile="1"
                BaseTileLevel="0"
                BottomsUp="False"
                CenterX="0"
                CenterY="0"
                DataSetType="Sky"
                ElevationModel="False"
                FileType=".png"
                Generic="False"
                Name="Toasty"
                Projection="Tan"
                QuadTreeMap=""
                Rotation="0"
                Sparse="True"
                StockSet="False"
                TileLevels="4"
                Url="{1}/{3}/{3}_{2}.png"
                WidthFactor="2"
            >
                <ThumbnailUrl>thumb.jpg</ThumbnailUrl>
            </ImageSet>
        </ForegroundImageSet>
    </Place>
</Folder>
"""

    def setup_method(self, method):
        from tempfile import mkdtemp

        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree

        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def test_basic(self):
        tiling = study.StudyTiling(2048, 2048)
        assert tiling._width == 2048
        assert tiling._height == 2048
        assert tiling._p2n == 2048
        assert tiling._tile_size == 8
        assert tiling._tile_levels == 3
        assert tiling._img_gx0 == 0
        assert tiling._img_gy0 == 0

    def test_preconditions(self):
        with pytest.raises(ValueError):
            study.StudyTiling(0, 1)

        with pytest.raises(ValueError):
            study.StudyTiling(1, -1)

        with pytest.raises(ValueError):
            study.StudyTiling(1, np.nan)

    def test_image_to_tile(self):
        tiling = study.StudyTiling(514, 514)
        assert tiling._p2n == 1024
        assert tiling.image_to_tile(0, 0) == (0, 0, 255, 255)
        assert tiling.image_to_tile(0, 513) == (0, 3, 255, 0)
        assert tiling.image_to_tile(513, 0) == (3, 0, 0, 255)
        assert tiling.image_to_tile(513, 513) == (3, 3, 0, 0)

    def test_sample_cli(self):
        from xml.etree import ElementTree as etree

        expected = etree.fromstring(self.WTML)

        for variants in ([], ["--placeholder-thumbnail"]):
            args = ["tile-study"]
            args += variants
            args += ["--outdir", self.work_path(), test_path("NGC253ALMA.jpg")]
            cli.entrypoint(args)

        with open(self.work_path("index_rel.wtml"), "rt", encoding="utf8") as f:
            observed = etree.fromstring(f.read())

        assert_xml_elements_equal(observed, expected)

    AVM_WTML = """<?xml version='1.0' encoding='UTF-8'?>
<Folder Browseable="True" Group="Explorer" Name="Toasty" Searchable="True">
    <Place
        Angle="0"
        AngularSize="0"
        DataSetType="Sky"
        Dec="-42.58752472831171"
        Magnitude="0"
        Name="Toasty"
        Opacity="100"
        RA="23.269985215493794"
        Rotation="0"
        Thumbnail="thumb.jpg"
        ZoomLevel="0.3370990847923382"
    >
        <ForegroundImageSet>
            <ImageSet
                BandPass="Visible"
                BaseDegreesPerTile="0.07726507807936124"
                BaseTileLevel="0"
                BottomsUp="False"
                CenterX="349.049780614"
                CenterY="-42.5874939584"
                DataSetType="Sky"
                ElevationModel="False"
                FileType=".png"
                Generic="False"
                Name="Toasty"
                OffsetX="1.886354445296938e-05"
                OffsetY="2.4372703865669735e-05"
                Projection="Tan"
                QuadTreeMap=""
                Rotation="-138.99999999999943"
                Sparse="True"
                StockSet="False"
                TileLevels="3"
                Url="{1}/{3}/{3}_{2}.png"
                WidthFactor="2"
            >
                <Credits>International Gemini Observatory/NOIRLab/NSF/AURA/B. Reynolds (Sutherland Shire Christian School)/T. Rector (University of Alaska, Anchorage)/Australian Gemini Office.</Credits>
                <CreditsUrl>https://noirlab.edu/public/images/geminiann11015a/</CreditsUrl>
                <Description>Gemini GMOS image of the barred spiral galaxy NGC 7552. Benjamin Reynolds, a 10th grade student at Sutherland Shire Christian School, suggested this target for Australia’s 2011 Gemini School Astronomy Contest and won. The picture consists of separate images taken with different filters: H-alpha (red), g (blue), r (green), and i (yellow).</Description>
                <ThumbnailUrl>thumb.jpg</ThumbnailUrl>
            </ImageSet>
        </ForegroundImageSet>
    </Place>
</Folder>"""

    @pytest.mark.skipif("not HAS_AVM")
    def test_avm(self):
        from xml.etree import ElementTree as etree

        # Hack for macOS: XML textualization is ever-so-slightly different.

        wtml = self.AVM_WTML

        if sys.platform == "darwin":
            wtml = wtml.replace('Dec="-42.58752472831171"', 'Dec="-42.587524728311706"')

        expected = etree.fromstring(wtml)

        cli.entrypoint(
            [
                "tile-study",
                "--avm",
                "--outdir",
                self.work_path(),
                test_path("geminiann11015a.jpg"),
            ]
        )

        with open(self.work_path("index_rel.wtml"), "rt", encoding="utf8") as f:
            observed = etree.fromstring(f.read())

        assert_xml_elements_equal(observed, expected)

    # Blah: this is the same as AVM_WTML, minus the metadata fields that aren't
    # preserved in the FITS export.
    FITS_WCS_WTML = """<?xml version='1.0' encoding='UTF-8'?>
<Folder Browseable="True" Group="Explorer" Name="Toasty" Searchable="True">
    <Place
        Angle="0"
        AngularSize="0"
        DataSetType="Sky"
        Dec="-42.58752472831171"
        Magnitude="0"
        Name="Toasty"
        Opacity="100"
        RA="23.269985215493794"
        Rotation="0"
        Thumbnail="thumb.jpg"
        ZoomLevel="0.3370990847923382"
    >
        <ForegroundImageSet>
            <ImageSet
                BandPass="Visible"
                BaseDegreesPerTile="0.07726507807936124"
                BaseTileLevel="0"
                BottomsUp="False"
                CenterX="349.049780614"
                CenterY="-42.5874939584"
                DataSetType="Sky"
                ElevationModel="False"
                FileType=".png"
                Generic="False"
                Name="Toasty"
                OffsetX="1.886354445296938e-05"
                OffsetY="2.4372703865669735e-05"
                Projection="Tan"
                QuadTreeMap=""
                Rotation="-138.99999999999943"
                Sparse="True"
                StockSet="False"
                TileLevels="3"
                Url="{1}/{3}/{3}_{2}.png"
                WidthFactor="2"
            >
                <ThumbnailUrl>thumb.jpg</ThumbnailUrl>
            </ImageSet>
        </ForegroundImageSet>
    </Place>
</Folder>"""

    def test_fits_wcs(self):
        from xml.etree import ElementTree as etree

        # Platform hack: XML textualization is ever-so-slightly different.

        wtml = self.FITS_WCS_WTML

        if sys.platform in ("darwin", "win32"):
            wtml = wtml.replace('Dec="-42.58752472831171"', 'Dec="-42.587524728311706"')

        expected = etree.fromstring(wtml)

        cli.entrypoint(
            [
                "tile-study",
                "--fits-wcs",
                test_path("geminiann11015a_wcs.fits"),
                "--outdir",
                self.work_path(),
                test_path("geminiann11015a.jpg"),
            ]
        )

        with open(self.work_path("index_rel.wtml"), "rt", encoding="utf8") as f:
            observed = etree.fromstring(f.read())

        assert_xml_elements_equal(observed, expected)
