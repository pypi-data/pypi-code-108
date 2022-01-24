#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017 StreamSets, Inc.

"""The setup script."""

from setuptools import setup, find_packages
from setuptools.command.sdist import sdist as _sdist
from distutils.extension import Extension

requirements = [
    'dpath==1.4.2',
    'inflection',
    'javaproperties',
    'PyYAML',
    'pycryptodome',
    'requests'
]


class sdist(_sdist):
    """Cythonize .pyx files, but only when sdist is run to avoid requiring users to have
    Cython installed.
    """
    def run(self):
        from Cython.Build import cythonize
        cythonize(['streamsets/sdk/accounts_api.pyx',
                   'streamsets/sdk/sch_api.pyx',
                   'streamsets/sdk/sdc_api.pyx',
                   'streamsets/sdk/st_api.pyx',
                   'streamsets/sdk/examples/sqoop.pyx'],
                  compiler_directives={
                      # always_allow_keywords added because of issue similar to the one described
                      # on https://github.com/bottlepy/bottle/issues/453.
                      'always_allow_keywords': True,
                      'emit_code_comments': False,
                      'language_level': "3"
                  })
        _sdist.run(self)


cmdclass = {'sdist': sdist}

extensions = [Extension('streamsets.sdk.accounts_api', ['streamsets/sdk/accounts_api.c']),
              Extension('streamsets.sdk.sch_api', ['streamsets/sdk/sch_api.c']),
              Extension('streamsets.sdk.sdc_api', ['streamsets/sdk/sdc_api.c']),
              Extension('streamsets.sdk.st_api', ['streamsets/sdk/st_api.c']),
              Extension('streamsets.sdk.examples.sqoop', ['streamsets/sdk/examples/sqoop.c'])]

setup(
    name='streamsets',
    version='3.12.dev2',
    description='A Python SDK for StreamSets',
    author='StreamSets Inc.',
    packages=['streamsets.sdk', 'streamsets.sdk.examples'],
    include_package_data=True,
    install_requires=requirements,
    dependency_links=['https://github.com/streamsets/dpath-python/tarball/master#egg=dpath-1.4.2'],
    ext_modules=extensions,
    python_requires='>=3',
    entry_points={'console_scripts': ['streamsets-sqoop-import = streamsets.sdk.examples.sqoop:main']},
    zip_safe=False,
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
