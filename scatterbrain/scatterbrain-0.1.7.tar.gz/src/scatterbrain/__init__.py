#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import  # noqa

import os  # noqa

PACKAGEDIR = os.path.abspath(os.path.dirname(__file__))

import logging  # noqa

log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

import pickle  # noqa

from .background import ScatteredLightBackground  # noqa
from .cupy_numpy_imports import load_image  # noqa
from .scene import StarScene  # noqa
from .tpf import correct_tpf  # noqa
from .version import __version__  # noqa

sector_times = pickle.load(open(f"{PACKAGEDIR}/data/tess_sector_times.pkl", "rb"))


def clear_scatterbrain_cache():
    """Clears the scatterbrain cache"""
    from astropy.utils.data import clear_download_cache

    clear_download_cache(pkgname="scatterbrain")
