import importlib
from setuptools import find_packages


for module in find_packages():
    importlib.import_module(module)


