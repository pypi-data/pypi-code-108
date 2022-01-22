#!/usr/bin/env python3
"""
Module SETUPUTILS_BUILD -- PEP 517 backend for setuputils
Copyright (C) 2012-2022 by Peter A. Donis

Released under the Python Software Foundation License.
"""

import os


class Builder(object):
    
    setuptools_fns = (
        'get_requires_for_build_wheel',
        'get_requires_for_build_sdist',
        'prepare_metadata_for_build_wheel',
        'build_sdist',
        'build_wheel',
    )
    
    def __init__(self):
        self.ensure_setup_cfg()
        import setuptools.build_meta
        for fname in self.setuptools_fns:
            setattr(self, fname, getattr(setuptools.build_meta, fname))
    
    def ensure_setup_cfg(self):
        import setuputils
        if any(os.path.isfile(setuputils.in_filename(section)) for section, _ in setuputils.setup_cfg_sections):
            setuputils.write_setup_cfg()


_builder = Builder()

get_requires_for_build_wheel = _builder.get_requires_for_build_wheel
get_requires_for_build_sdist = _builder.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _builder.prepare_metadata_for_build_wheel
build_wheel = _builder.build_wheel
build_sdist = _builder.build_sdist
