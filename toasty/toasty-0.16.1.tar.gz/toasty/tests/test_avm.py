# -*- mode: python; coding: utf-8 -*-
# Copyright 2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

import os.path
import pytest

from . import HAS_AVM, test_path
from .. import cli


class TestAvm(object):
    def setup_method(self, method):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()

    def teardown_method(self, method):
        from shutil import rmtree
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    @pytest.mark.skipif('not HAS_AVM')
    def test_check_cli_bad(self):
        args = [
            'check-avm',
            '--print',
            '--exitcode',
            test_path('badavm-type.png'),
        ]

        try:
            cli.entrypoint(args)
        except SystemExit as e:
            assert e.code == 1
        else:
            assert False, 'no error exit on bad AVM'

    @pytest.mark.skipif('not HAS_AVM')
    def test_check_cli_good(self):
        args = [
            'check-avm',
            '--print',
            test_path('geminiann11015a.jpg'),
        ]

        cli.entrypoint(args)
