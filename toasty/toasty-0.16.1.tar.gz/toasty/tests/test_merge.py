# -*- mode: python; coding: utf-8 -*-
# Copyright 2019-2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

import numpy as np
import numpy.testing as nt
import os.path
import pytest

from . import test_path
from .. import cli
from .. import merge


def test_averaging_merger():
    from ..merge import averaging_merger

    t = np.array([[np.nan, 1], [3, np.nan]])
    nt.assert_almost_equal(averaging_merger(t), [[2.]])


class TestCascade(object):
    def setup_method(self, method):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def test_basic_cli(self):
        """Test the CLI interface. We don't go out of our way to validate the
        computations in detail -- that's for the unit tests that probe the
        module directly.

        """
        for variants in (['--parallelism=1'], ['--parallelism=2', '--placeholder-thumbnail']):
            args = ['tile-allsky']
            args += variants
            args += [
                '--outdir', self.work_path('basic_cli'),
                test_path('Equirectangular_projection_SW-tweaked.jpg'),
                '1',
            ]
            cli.entrypoint(args)

        for parallelism in '12':
            args = [
                'cascade',
                '--parallelism', parallelism,
                '--start', '1',
                self.work_path('basic_cli'),
            ]
            cli.entrypoint(args)
