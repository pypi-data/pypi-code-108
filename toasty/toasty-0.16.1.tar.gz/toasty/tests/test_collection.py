# -*- mode: python; coding: utf-8 -*-
# Copyright 2021 the AAS WorldWide Telescope project
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import pytest
from . import test_path
from .. import collection

try:
    from astropy.io import fits
    HAS_ASTRO = True
except ImportError:
    HAS_ASTRO = False


class TestCollection(object):

    @pytest.mark.skipif('not HAS_ASTRO')
    def test_is_multi_tan(self):
        coll = collection.SimpleFitsCollection([test_path('wcs512.fits.gz')])
        assert coll._is_multi_tan()

        coll = collection.SimpleFitsCollection([test_path('herschel_spire.fits.gz'),
                                                test_path('herschel_spire.fits.gz')])
        assert coll._is_multi_tan()

        coll = collection.SimpleFitsCollection([test_path('wcs512.fits.gz'),
                                                test_path('herschel_spire.fits.gz')])
        assert not coll._is_multi_tan()
