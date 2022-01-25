# -*- mode: python; coding: utf-8 -*-
# Copyright 2013-2022 Chris Beaumont and the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import os
from tempfile import mkstemp, mkdtemp
from shutil import rmtree

import pytest
import numpy as np

try:
    import healpy as hp
    from astropy.io import fits

    HAS_ASTRO = True
except ImportError:
    HAS_ASTRO = False

try:
    import OpenEXR

    HAS_OPENEXR = True
except ImportError:
    HAS_OPENEXR = False

from . import test_path
from .. import cli, toast
from ..image import ImageLoader
from ..jpeg2000 import ChunkedJPEG2000Reader, HAS_JPEG2000
from ..pyramid import Pos, PyramidIO
from ..toast import sample_layer, sample_layer_filtered
from ..transform import f16x3_to_rgb


def test_mid():
    from .._libtoasty import mid

    result = mid((0, 0), (np.pi / 2, 0))
    expected = np.pi / 4, 0
    np.testing.assert_array_almost_equal(result, expected)

    result = mid((0, 0), (0, 1))
    expected = 0, 0.5
    np.testing.assert_array_almost_equal(result, expected)


def test_area():
    MAX_DEPTH = 6
    areas = {}

    for t in toast.generate_tiles(MAX_DEPTH, bottom_only=False):
        a = areas.get(t.pos.n, 0)
        areas[t.pos.n] = a + toast.toast_tile_area(t)

    for d in range(1, MAX_DEPTH + 1):
        np.testing.assert_almost_equal(areas[d], 4 * np.pi)


def test_tile_for_point_boundaries():
    # These test points occur at large-scale tile boundaries and so we're not
    # picky about where they land in the tiling -- either tile on a border is
    # OK.

    from ..toast import toast_tile_for_point

    latlons = [
        (0.0, 0.0),
        (0.0, -0.5 * np.pi),
        (0.0, 0.5 * np.pi),
        (0.0, np.pi),
        (0.0, 1.5 * np.pi),
        (0.0, 2 * np.pi),
        (0.0, 2.5 * np.pi),
        (-0.5 * np.pi, 0.0),
        (-0.5 * np.pi, -np.pi),
        (-0.5 * np.pi, np.pi),
        (0.5 * np.pi, 0.0),
        (0.5 * np.pi, -np.pi),
        (0.5 * np.pi, np.pi),
    ]

    for depth in range(4):
        for lat, lon in latlons:
            tile = toast_tile_for_point(depth, lat, lon)


def test_tile_for_point_specifics():
    from ..toast import toast_tile_for_point

    test_data = {
        (0.1, 0.1): [
            (0, 0, 0),
            (1, 1, 0),
            (2, 3, 1),
            (3, 7, 3),
            (4, 14, 7),
            (5, 29, 14),
            (6, 59, 29),
            (7, 119, 59),
            (8, 239, 119),
            (9, 479, 239),
            (10, 959, 479),
            (11, 1918, 959),
            (12, 3837, 1918),
        ]
    }

    for (lat, lon), nxys in test_data.items():
        for nxy in nxys:
            tile = toast_tile_for_point(nxy[0], lat, lon)
            assert tile.pos.n == nxy[0]
            assert tile.pos.x == nxy[1]
            assert tile.pos.y == nxy[2]


def test_pixel_for_point():
    from ..toast import toast_pixel_for_point

    test_data = {
        (0.1, 0.1): (3, 7, 3, 126, 191),
        (-0.4, 2.2): (3, 1, 1, 200, 75),
    }

    for (lat, lon), (n, x, y, px, py) in test_data.items():
        shallow_tile, frac_x, frac_y = toast_pixel_for_point(n, lat, lon)
        assert shallow_tile.pos.n == n
        assert shallow_tile.pos.x == x
        assert shallow_tile.pos.y == y
        assert px == int(round(frac_x))
        assert py == int(round(frac_y))
        deep_tile, _, _ = toast_pixel_for_point(n + 8, lat, lon)
        assert deep_tile.pos.x % 256 == px
        assert deep_tile.pos.y % 256 == py


def image_test(expected, actual, err_msg):
    resid = np.abs(1.0 * actual - expected)
    if np.median(resid) < 10:
        return

    _, pth = mkstemp(suffix=".png")
    import PIL.Image

    PIL.Image.fromarray(np.hstack((expected, actual))).save(pth)
    pytest.fail("%s. MedResid=%f. Saved to %s" % (err_msg, np.median(resid), pth))


class PyramidTester(object):
    def setup_method(self, _method):
        self.work_dir = mkdtemp()
        self.pio = PyramidIO(self.work_dir)

    def teardown_method(self, _method):
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def verify_level1(
        self,
        ref="earth_toasted_sky",
        format=None,
        expected_2d=False,
        drop_alpha=False,
        planetary=False,
    ):
        for n, x, y in [(1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]:
            if planetary:
                # to transform sky to planetary, we need to mirror the global
                # image horizontally. So here we mirror on a tile level, and
                # below we mirror on a pixel level.
                ref_x = 1 - x
                warn = f"; this is mirrored from input position ({n},{x},{y}) for planetary mode"
            else:
                ref_x = x
                warn = ""

            ref_path = test_path(ref, str(n), str(y), "%i_%i.png" % (y, ref_x))
            expected = ImageLoader().load_path(ref_path).asarray()

            if planetary:
                expected = expected[:, ::-1]

            pos = Pos(n=n, x=x, y=y)
            observed = self.pio.read_image(pos, format=format).asarray()

            if expected_2d:
                expected = expected.mean(axis=2)

            if drop_alpha:
                assert observed.shape[2] == 4
                observed = observed[..., :3]

            image_test(expected, observed, "Failed for %s%s" % (ref_path, warn))


class TestSampleLayer(PyramidTester):
    def test_plate_carree(self):
        from ..samplers import plate_carree_sampler

        img = ImageLoader().load_path(
            test_path("Equirectangular_projection_SW-tweaked.jpg")
        )
        sampler = plate_carree_sampler(img.asarray())
        sample_layer(self.pio, sampler, 1, format="png")
        self.verify_level1()

    def test_plate_carree_ecliptic(self):
        from ..samplers import plate_carree_ecliptic_sampler

        img = ImageLoader().load_path(test_path("tess_platecarree_ecliptic_512.jpg"))
        sampler = plate_carree_ecliptic_sampler(img.asarray())
        sample_layer(self.pio, sampler, 1, format="png")
        self.verify_level1(ref="tess")

    @pytest.mark.skipif("not HAS_OPENEXR")
    def test_earth_plate_carree_exr(self):
        from ..samplers import plate_carree_sampler

        img = ImageLoader().load_path(
            test_path("Equirectangular_projection_SW-tweaked.exr")
        )
        sampler = plate_carree_sampler(img.asarray())
        sample_layer(self.pio, sampler, 1, format="npy")
        f16x3_to_rgb(self.pio, 1, parallel=1, out_format="png")
        self.verify_level1()

    @pytest.mark.skipif("not HAS_JPEG2000")
    def test_earth_plate_carree_jpeg2000_chunked_planetary(self):
        from ..samplers import ChunkedPlateCarreeSampler
        from ..toast import ToastCoordinateSystem

        img = ChunkedJPEG2000Reader(
            test_path("Equirectangular_projection_SW-tweaked.jp2")
        )
        # this currently (2021 Oct) only supports planetary coordinates:
        chunker = ChunkedPlateCarreeSampler(img, planetary=True)

        for ichunk in range(chunker.n_chunks):
            tile_filter = chunker.filter(ichunk)
            sampler = chunker.sampler(ichunk)
            sample_layer_filtered(
                self.pio,
                tile_filter,
                sampler,
                1,  # depth
                coordsys=ToastCoordinateSystem.PLANETARY,
                parallel=1,
            )

        self.verify_level1(drop_alpha=True, planetary=True)

    @pytest.mark.skipif("not HAS_ASTRO")
    def test_healpix_equ(self):
        from ..samplers import healpix_fits_file_sampler

        sampler = healpix_fits_file_sampler(test_path("earth_healpix_equ.fits"))
        sample_layer(self.pio, sampler, 1, format="npy")
        self.verify_level1(format="npy", expected_2d=True)

    @pytest.mark.skipif("not HAS_ASTRO")
    def test_healpix_gal(self):
        from ..samplers import healpix_fits_file_sampler

        sampler = healpix_fits_file_sampler(test_path("earth_healpix_gal.fits"))
        sample_layer(self.pio, sampler, 1, format="fits")
        self.verify_level1(format="fits", expected_2d=True)


class TestCliBasic(PyramidTester):
    """
    CLI tests.
    """

    def inner_test(self, image_path, projection):
        args = [
            "tile-allsky",
            "--name=Earth",
            f"--projection={projection}",
            "--outdir",
            self.work_path(),
            image_path,
            "2",
        ]
        cli.entrypoint(args)
        cli.entrypoint(["cascade", "--start", "2", self.work_path()])
        self.verify_level1(planetary=True, drop_alpha=True)

    def test_planet(self):
        self.inner_test(
            test_path("Equirectangular_projection_SW-tweaked.jpg"),
            "plate-carree-planet",
        )

    def test_planet_zeroleft(self):
        """
        Our source image is a standard planetary map where longitudes range from
        -180 to 180, left to right. So to get the correct zeroleft input, we
        need to swap the left and right halves.
        """
        img = ImageLoader().load_path(
            test_path("Equirectangular_projection_SW-tweaked.jpg")
        )
        hw = img.width // 2
        buf = img.asarray()
        temp = buf[:, hw:].copy()
        buf[:, hw:] = buf[:, :hw]
        buf[:, :hw] = temp
        img._array = buf  # hack!
        img._pil = None
        p = self.work_path("zeroleft.jpg")
        img.save(p, format="jpg")
        self.inner_test(
            p,
            "plate-carree-planet-zeroleft",
        )

    def test_planet_zeroright(self):
        """
        The horizontal mirror of zeroleft. Longitudes increase to the left, but
        the right edge of the image is longitude 0.
        """
        img = ImageLoader().load_path(
            test_path("Equirectangular_projection_SW-tweaked.jpg")
        )
        hw = img.width // 2
        buf = img.asarray()
        temp = buf[:, hw:].copy()
        buf[:, hw:] = buf[:, :hw]
        buf[:, :hw] = temp
        img._array = buf[:, ::-1]  # hack!
        img._pil = None
        p = self.work_path("zeroright.jpg")
        img.save(p, format="jpg")
        self.inner_test(
            p,
            "plate-carree-planet-zeroright",
        )
