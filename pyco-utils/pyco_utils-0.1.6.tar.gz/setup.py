"""
pyco_utils
======
Python Common Utils For Web Developers
"""

import io
import re
import os
import sys

from setuptools import setup

try:
    with io.open('pyco_utils/__init__.py', 'rt', encoding='utf8') as f:
        version = re.search(r'__version__ = \'(.*?)\'', f.read())
        # if isinstance(version, re.Match):
        _v = getattr(version, "group", None)
        if callable(_v):
            version = version.group(1)
        else:
            version = re.search(r'__version__ = \"(.*?)\"', f.read()).group(1)

except Exception as e:
    print(sys.executable, sys.path[0], "failed to get version of pyco-utils", e, "retry now")
    _cwd = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _cwd)
    import pyco_utils

    version = pyco_utils.__version__

with io.open('README.md', 'rt', encoding='utf8') as f2:
    long_description = f2.read()

setup(
    name='pyco_utils',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='common utils and samples for python developers',
    long_description=long_description,
    long_description_content_type="text/markdown",

    # The project's main homepage.
    url='http://github.com/dodoru/pyco-utils',
    author='dodoru',
    author_email='dodoru@foxmail.com',
    maintainer='dodoru',
    maintainer_email='dodoru@foxmail.com',

    zip_safe=False,
    platforms='any',
    license='GNU LGPLv3',

    # What does your project relate to?
    keywords='Python utils',

    install_requires=[
        "werkzeug"
    ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=[
        'pyco_utils',
    ],

    include_package_data=True,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[
    ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
    },

)
