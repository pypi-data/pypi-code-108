from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
meta_path = convert_path('./__init__.py')
with open(meta_path) as meta_file:
    exec(meta_file.read(), main_ns)

setup(name="nitrogen-aggr", version=main_ns['__version__'], packages=find_packages())
