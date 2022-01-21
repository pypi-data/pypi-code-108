import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.0'
PACKAGE_NAME = 'riya_first_demopackage123'
AUTHOR = 'Riya Chaudhary'
AUTHOR_EMAIL = 'riya123c@gmail.com'

LICENSE = 'MIT License 2.0'
DESCRIPTION = 'Demo package for add,sub,mul and div'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"


setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      packages=find_packages())