"""A setuptools based setup module.
sdist bdist_wheel upload
See:
https://packaging.python.org/tutorials/distributing-packages/
https://github.com/pypa/sampleproject
https://pypi.python.org
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PT3S',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='90.12.4.24.dev1',

    description='Python Tools 3S',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/aw3s/PT3S',

    # Author details
    author='PT3S',
    author_email='andreashwolters@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
  
    # What does your project relate to?
    keywords='Python Tools 3S',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['nb', 'testdata', 'testresults']),
    packages=['PT3S','lds','UTILS'],

    package_dir={
       'PT3S':'.','lds':'lds','UTILS':'UTILS'},
    

    python_requires='>=3',

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    ###install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'PT3S': [           
            'PT3S.ipynb'          
           ,'PT3S.html'
           ,'PT3S.pdf'  
           #,'Lx.ipynb'           
           #,'testdata\Lx\20201113_151238a - 6 Logs.7z'
           ,'testdata\OneLPipe.XML'
           #,'testdata\OneLPipe.mdb'
           ,'testdata\WDOneLPipe\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata\WDOneLPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata\WDOneLPipe\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata\LocalHeatingNetwork.XML'
           #,'testdata\LocalHeatingNetwork.mdb'
           ,'testdata\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata\TinyWDN.XML'
           #,'testdata\TinyWDN.mdb'
           ,'testdata\WDTinyWDN\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata\WDTinyWDN\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata\WDTinyWDN\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata\GPipes.XML'
           ,'testdata\WDGPipes\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata\WDGPipes\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata\WDGPipes\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata\GPipe.XML'
           #,'testdata\GPipe.mdb'
           ,'testdata\WDGPipe\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata\WDGPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata\WDGPipe\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata\DHNetwork.XML'
           #,'testdata\DHNetwork.mdb'
           ,'testdata\WDDHNetwork\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata\WDDHNetwork\B1\V0\BZ1\M-1-0-1.MX2'
           #,'testdata\WDDHNetwork\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata11\OneLPipe.XML'
           ,'testdata11\OneLPipe.mdb'
           ,'testdata11\WDOneLPipe\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata11\WDOneLPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata11\WDOneLPipe\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata11\LocalHeatingNetwork.XML'
           ,'testdata11\LocalHeatingNetwork.mdb'
           ,'testdata11\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata11\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata11\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata11\TinyWDN.XML'
           ,'testdata11\TinyWDN.mdb'
           ,'testdata11\WDTinyWDN\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata11\WDTinyWDN\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata11\WDTinyWDN\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata11\GPipes.XML'
           ,'testdata11\WDGPipes\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata11\WDGPipes\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata11\WDGPipes\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata11\GPipe.XML'
           ,'testdata11\GPipe.mdb'
           ,'testdata11\WDGPipe\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata11\WDGPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata11\WDGPipe\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata11\DHNetwork.XML'
           ,'testdata11\DHNetwork.mdb'
           ,'testdata11\WDDHNetwork\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata11\WDDHNetwork\B1\V0\BZ1\M-1-0-1.MX2'
           #,'testdata\WDDHNetwork\B1\V0\BZ1\M-1-0-1.1.MXS'

           ,'testdata10\OneLPipe.XML'
           ,'testdata10\OneLPipe.mdb'
           ,'testdata10\WDOneLPipe\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata10\WDOneLPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata10\WDOneLPipe\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata10\LocalHeatingNetwork.XML'
           ,'testdata10\LocalHeatingNetwork.mdb'
           ,'testdata10\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata10\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata10\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata10\TinyWDN.XML'
           ,'testdata10\TinyWDN.mdb'
           ,'testdata10\WDTinyWDN\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata10\WDTinyWDN\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata10\WDTinyWDN\B1\V0\BZ1\M-1-0-1.1.MXS'
           ,'testdata10\GPipe.XML'
           ,'testdata10\GPipe.mdb'
           ,'testdata10\WDGPipe\B1\V0\BZ1\M-1-0-1.1.MX1'
           ,'testdata10\WDGPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata10\WDGPipe\B1\V0\BZ1\M-1-0-1.1.MXS'

           ,'testdata09\OneLPipe.XML'
           ,'testdata09\OneLPipe.mdb'
           ,'testdata09\WDOneLPipe\B1\V0\BZ1\M-1-0-1.MX1'
           ,'testdata09\WDOneLPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata09\WDOneLPipe\B1\V0\BZ1\M-1-0-1.MXS'
           ,'testdata09\LocalHeatingNetwork.XML'
           ,'testdata09\LocalHeatingNetwork.mdb'
           ,'testdata09\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.MX1'
           ,'testdata09\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata09\WDLocalHeatingNetwork\B1\V0\BZ1\M-1-0-1.MXS'
           ,'testdata09\TinyWDN.XML'
           ,'testdata09\TinyWDN.mdb'
           ,'testdata09\WDTinyWDN\B1\V0\BZ1\M-1-0-1.MX1'
           ,'testdata09\WDTinyWDN\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata09\WDTinyWDN\B1\V0\BZ1\M-1-0-1.MXS'
           ,'testdata09\GPipe.XML'
           ,'testdata09\GPipe.mdb'
           ,'testdata09\WDGPipe\B1\V0\BZ1\M-1-0-1.MX1'
           ,'testdata09\WDGPipe\B1\V0\BZ1\M-1-0-1.MX2'
           ,'testdata09\WDGPipe\B1\V0\BZ1\M-1-0-1.MXS'
            ],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    ###data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)
