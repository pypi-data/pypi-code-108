
from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
      name             =   'python-pfconclient',
      version          =   '3.0.0',
      description      =   '(Python) client for the Pfcon API',
      long_description =   readme,
      author           =   'FNNDSC',
      author_email     =   'dev@babymri.org',
      url              =   'https://github.com/FNNDSC/python-pfconclient',
      packages         =   ['pfconclient'],
      install_requires =   ['requests>=2.27.1'],
      test_suite       =   'nose.collector',
      tests_require    =   ['nose'],
      scripts          =   ['bin/pfconclient'],
      license          =   'MIT',
      zip_safe         =   False,
      python_requires  =   '>=3.7'
)