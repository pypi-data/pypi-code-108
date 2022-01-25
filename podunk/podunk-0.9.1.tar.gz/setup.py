# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

import sys
from os import path as osp
from fnmatch import fnmatch
import os
import re

def package_data_with_recursive_dirs(package_data_spec):
    """converts modified package_data dict to a classic package_data dict
    Where normal package_data entries can only specify globs, the
    modified package_data dict can have
       a) directory names or
       b) tuples of a directory name and a pattern
    as entries in addition to normal globs.
    When one of a) or b) is encountered, the entry is expanded so
    that the resulting package_data contains all files (optionally
    filtered by pattern) encountered by recursively searching the
    directory.
    
    Usage:
    setup(
    ...
        package_data = package_data_with_recursive_dirs({
            'module': ['dir1', ('dir2', '*.xyz')],
            'module2': ['dir3/file1.txt']
                })
    )
    """
    out_spec = {}
    for package_name, spec in package_data_spec.items():
        # replace dots by operating system path separator
        package_path = osp.join(*package_name.split('.'))
        out_entries = []
        for entry in spec:
            directory = None  # full path to data dir
            pattern = None  # pattern to append
            datadir = None  # data dir relative to package (as specified)
            try:  # entry is just a string
                directory = osp.join(package_path, entry)
                datadir = entry
                pattern = None
            except (TypeError, AttributeError):  # entry has additional pattern spec
                directory = osp.join(package_path, entry[0])
                pattern = entry[1]
                datadir = entry[0]
            if osp.isdir(directory):  # only apply if it is really a directory
                for (dirpath, dirnames, filenames) in os.walk(directory):
                    for filename in (osp.join(dirpath, f) for f in filenames):
                        if not pattern or fnmatch(filename, pattern):
                            relname = osp.normpath(osp.join(datadir, osp.relpath(filename, directory)))
                            out_entries.append(relname)
            else:  # datadir is not really a datadir but a glob or something else
                out_entries.append(datadir)  # we just copy the entry
        out_spec[package_name] = out_entries
    return out_spec
    
here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Read version from __init__.py
try:
    filepath = 'podunk/__init__.py'
    with open( filepath ) as f:
        __version__ ,= re.findall( '__version__: str = "(.*)"', f.read() )
except Exception as error:
    __version__ = "0.0.1"
    sys.stderr.write( "Warning: Could not open '%s' due %s\n" % ( filepath, error ) )
    
# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='podunk',
    version=__version__,
    description='A simple library for creating tabular PDF reports in Python using the ReportLab PDF library',    
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/torsten-pf/podunk',
    license='New BSD License',
    platforms=['any'],
    author='Jim Storch', #, Jojo Maquiling, Torsten Pfuetzenreuter',  # Optional
    # author_email='author@example.com',  # Optional
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='sample, setuptools, development',  # Optional
    packages=find_packages(),  # Required
    package_dir={"": "."},
    python_requires='>=3.6, <4',
    install_requires=['reportlab'],
    #include_package_data=True,
    #package_data={'podunk': ['podunk/media/**/*']},
    package_data = package_data_with_recursive_dirs({
            'podunk': ['media'],
    }),
    project_urls={
        'Bug Reports': 'https://github.com/torsten-pf/podunk/issues',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/torsten-pf/podunk/',
    },
)
