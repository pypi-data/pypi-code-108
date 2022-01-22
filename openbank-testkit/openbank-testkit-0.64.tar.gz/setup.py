import os
from setuptools import setup

README = None

with open(os.path.abspath(os.path.join(__file__, os.pardir, "README.md")), 'r') as fd:
  README = fd.read()

setup(
  name='openbank-testkit',
  version='0.64',
  description='openbank testkit libraries',
  long_description=README,
  long_description_content_type="text/markdown",
  url='https://github.com/jancajthaml-openbank/testkit',
  author='jan.cajthaml',
  author_email='jan.cajthaml@gmail.com',
  license='Apache 2.0',
  packages=['openbank_testkit'],
  install_requires=[],
  zip_safe=False,
  entry_points = {}
)