import setuptools
from setuptools import setup
from bx import __version__


import os.path as op
this_directory = op.abspath(op.dirname(__file__))
with open(op.join(this_directory, 'README.md')) as f:
    long_description = f.read()

download_url = 'https://gitlab.com/xgrg/bx/-/archive/v%s/bx-v%s.tar.gz'
download_url = download_url % (__version__, __version__)

setup(
    name='bbrc-bx',
    install_requires=['coverage>=4.5',
                      'nose>=1.3',
                      'requests>=2.21',
                      'six>=1.10',
                      'lxml>=4.3',
                      'nibabel>=2.3',
                      'pydicom>=1.2',
                      'numpy>=1.16',
                      'pandas>=0.24',
                      'xlrd>=1.2',
                      'xlutils>=2.0',
                      'xlwt>=1.3',
                      'tqdm>=4.31',
                      'openpyxl>=2.6',
                      'bbrc-pyxnat>=1.4.2',
                      'rich>=10.1'],
    scripts=['bin/bx'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=__version__,
    description='BarcelonaBeta + XNAT = bx',
    packages=setuptools.find_packages(),
    author='Greg Operto',
    author_email='goperto@barcelonabeta.org',
    url='https://gitlab.com/xgrg/bx',
    download_url=download_url,
    classifiers=['Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 3.7'],
    include_package_data=True

)
