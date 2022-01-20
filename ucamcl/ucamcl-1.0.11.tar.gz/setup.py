"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
from ucamcl import __version__

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ucamcl',
    version=__version__,
    description='Teaching with Python unit tests',
    long_description=long_description,
    url='https://github.com/damonjw/ucamcl',
    author='Damon Wischik',
    author_email='djw1005@cam.ac.uk',
    license='AGPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Education :: Computer Aided Instruction (CAI)',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='education teaching testing',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['cryptography>=2.0', 'requests'],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)
