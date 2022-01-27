# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import numpy as np
from numpy import testing as nt
import os.path
import pytest
import shutil
import sys

from . import assert_xml_elements_equal, test_path
from .. import cli
from .. import pipeline
from ..pipeline import astropix


class LocalTestAstroPixImageSource(astropix.AstroPixImageSource):
    def query_candidates(self):
        # NB all these values are wrong for the input image!!!
        item = {
            "creator": "Fake Observatory",
            "title": "Test",
            "description": "An amazing image.",
            "object_name": ["NGC 253"],
            "resource_url": "http://example.com/amazingimage.jpg",
            "reference_url": "https://public.nrao.edu/gallery/astronomers-capture-first-image-of-a-black-hole/",
            "image_id": "test1",
            "image_credit": "Courtesy an amazing telescope.",
            "wcs_coordinate_frame": "ICRS",
            "wcs_equinox": "J2000",
            "wcs_reference_value": ["187.70593075", "12.39112325"],
            "wcs_reference_dimension": ["2166.0", "2129.0"],
            "wcs_reference_pixel": ["3738.9937831", "3032.00448074"],
            "wcs_scale": ["-5.91663506907e-14", "5.91663506907e-14"],
            "wcs_rotation": "0",
            "wcs_projection": "TAN",
            "wcs_quality": "Full",
            "wcs_notes": "FAKE",
            "publisher": "FAKE",
            "publisher_id": "fake",
            "resource_id": "test1",
            "last_updated": "2019-04-08T14:00:38.128143",
            "metadata_version": "1.1",
            "image_width": "7416",
            "image_height": "4320",
            "image_max_boundry": "7416",
            "astropix_id": 21642
        }
        yield astropix.AstroPixCandidateInput(item)

    def fetch_candidate(self, unique_id, cand_data_stream, cachedir):
        shutil.copy(test_path('NGC253ALMA.jpg'), os.path.join(cachedir, 'image.jpg'))


class TestPipeline(object):
    def setup_method(self, method):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()

        pipeline.IMAGE_SOURCE_CLASS_LOADERS['_local_test_astropix'] = lambda: LocalTestAstroPixImageSource

        os.makedirs(self.work_path('repo'))
        shutil.copy(test_path('toasty-pipeline-config.yaml'), self.work_path('repo'))

    def teardown_method(self, method):
        from shutil import rmtree
        rmtree(self.work_dir)

    def work_path(self, *pieces):
        return os.path.join(self.work_dir, *pieces)

    def test_workflow(self):
        args = [
            'pipeline', 'init',
            '--local', self.work_path('repo'),
            self.work_path('work'),
        ]
        cli.entrypoint(args)

        args = [
            'pipeline', 'refresh',
            '--workdir', self.work_path('work'),
        ]
        cli.entrypoint(args)

        args = [
            'pipeline', 'fetch',
            '--workdir', self.work_path('work'),
            'fake_test1', '*nomatchisok*',
        ]
        cli.entrypoint(args)

        args = [
            'pipeline', 'process-todos',
            '--workdir', self.work_path('work'),
        ]
        cli.entrypoint(args)

        args = [
            'pipeline', 'approve',
            '--workdir', self.work_path('work'),
            'fake_test1', 'fake_test?',
        ]
        cli.entrypoint(args)

        args = [
            'pipeline', 'publish',
            '--workdir', self.work_path('work'),
        ]
        cli.entrypoint(args)

        args = [
            'pipeline', 'ignore-rejects',
            '--workdir', self.work_path('work'),
        ]
        cli.entrypoint(args)

    def test_args(self):
        with pytest.raises(SystemExit):
            args = [
                'pipeline', 'init',
                self.work_path('work'),
            ]
            cli.entrypoint(args)

        with pytest.raises(SystemExit):
            args = [
                'pipeline', 'init',
                '--azure-conn-env', 'NOTAVARIABLE',
                self.work_path('work'),
            ]
            cli.entrypoint(args)

        os.environ['FAKECONNSTRING'] = 'fake'

        with pytest.raises(SystemExit):
            args = [
                'pipeline', 'init',
                '--azure-conn-env', 'FAKECONNSTRING',
                self.work_path('work'),
            ]
            cli.entrypoint(args)
