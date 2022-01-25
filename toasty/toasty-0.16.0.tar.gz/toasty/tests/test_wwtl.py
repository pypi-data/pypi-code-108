# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import numpy as np
from numpy import testing as nt
import os.path
import pytest
import sys

from wwt_data_formats.filecabinet import FileCabinetWriter

from . import assert_xml_elements_equal, test_path
from .. import cli
from .. import study


class TestStudy(object):
    def setup_method(self, method):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def test_basic_cli(self):
        # First, create a WWTL. NB, filenames should match the ID's in the XML
        # file.

        fw = FileCabinetWriter()

        with open(test_path('layercontainer.wwtxml'), 'rb') as f:
            b = f.read()

        fw.add_file_with_data('55cb0cce-c44a-4a44-a509-ea66fce643a5.wwtxml', b)

        with open(test_path('NGC253ALMA.jpg'), 'rb') as f:
            b = f.read()

        fw.add_file_with_data('55cb0cce-c44a-4a44-a509-ea66fce643a5\\7ecb6411-e4ee-4dfa-90ef-77d6f486c7d2.jpg', b)

        with open(self.work_path('image.wwtl'), 'wb') as f:
            fw.emit(f)

        # Now run it through the CLI.

        for variants in ([], ['--placeholder-thumbnail'], ['--name=Custom Name']):
            args = ['tile-wwtl']
            args += variants
            args += [
                '--outdir', self.work_path('tiles'),
                self.work_path('image.wwtl')
            ]
            cli.entrypoint(args)
