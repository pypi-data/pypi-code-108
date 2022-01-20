# -*- utf-8 -*-
# Copyright 2018 Gabriele Vajente

"""Install script for Bruco, install with pip:

    python -m pip install .
"""

import glob
import os.path
import re

from setuptools import (setup, find_packages)


def find_version(path):
    """Parse the __version__ metadata in the given file.
    """
    with open(path, 'r') as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    # metadata
    name='bruco',
    provides=['bruco'],
    description="Brute force coherence",
    author="Gabriele Vajente",
    license="GPLv3+",
    url="https://git.ligo.org/gabriele-vajente/bruco",
    version=find_version(os.path.join('bruco', '__init__.py')),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
            'GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    # dependencies
    setup_requires=[
        'setuptools',
    ],
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'gwdatafind',
        'gwpy',
    ],
    # content
    packages=find_packages(),
    scripts=[os.path.join('bin', 'bruco')],
    data_files=[
        (os.path.join('share', 'bruco'),
         list(glob.glob(os.path.join('share', '*.txt'))),
         ),
    ],
)
