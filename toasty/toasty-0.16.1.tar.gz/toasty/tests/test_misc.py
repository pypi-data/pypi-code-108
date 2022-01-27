# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

import argparse
import numpy as np
import numpy.testing as nt
import os.path
import pytest

from . import test_path
from .. import cli


class TestMiscCli(object):
    def setup_method(self, method):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def test_make_thumbnail(self):
        """
        Just a smoketest.
        """
        args = [
            'make-thumbnail',
            test_path('Equirectangular_projection_SW-tweaked.jpg'),
            self.work_path('basic_cli'),
        ]
        cli.entrypoint(args)

    def test_crop(self):
        """
        Test the generic --crop argument.
        """
        from ..image import ImageLoader

        parser = argparse.ArgumentParser()
        ImageLoader.add_arguments(parser)
        settings = parser.parse_args(['--crop=1,2,3,4'])
        img = ImageLoader.create_from_args(settings).load_path(test_path('crop_input.png'))
        arr = img.asarray()
        assert arr.shape == (256, 256, 3)
        assert arr.max() == 0


