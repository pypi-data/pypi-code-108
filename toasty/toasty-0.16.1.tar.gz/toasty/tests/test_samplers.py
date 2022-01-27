# -*- mode: python; coding: utf-8 -*-
# Copyright 2019-2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

import numpy as np
import numpy.testing as nt
import os.path
import pytest

from . import test_path
from .. import cli
from .. import samplers

try:
    import healpy as hp
    from astropy.io import fits
    HAS_ASTRO = True
except ImportError:
    HAS_ASTRO = False


class TestSamplers(object):
    def setup_method(self, method):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    @pytest.mark.skipif('not HAS_ASTRO')
    def test_basic_cli(self):
        """Test some CLI interfaces. We don't go out of our way to validate the
        computations in detail -- that's for the unit tests that probe the
        module directly.

        """
        args = [
            'tile-healpix',
            '--outdir', self.work_path('basic_cli'),
            test_path('earth_healpix_equ.fits'),
            '1',
        ]
        cli.entrypoint(args)
