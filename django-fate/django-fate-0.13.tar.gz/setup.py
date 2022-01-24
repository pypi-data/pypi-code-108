from distutils.core import setup

# from os import path as os_path
#
# this_directory = os_path.abspath(os_path.dirname(__file__))
#
#
# def read_file(filename):
#     with open(os_path.join(this_directory, filename)) as f:
#         long_description = f.read()
#         return long_description
from setuptools import Extension, dist, find_packages, setup

setup(
    name="django-fate",
    version="0.13",
    author="Ryan",
    packages=find_packages(),
    author_email="604729765@qq.com",
    url="https://www.leetab.com",
    description="Django项目中使用的简易API模块",
    # install_requires=["redis>=3.5.3"],
    # long_description=open("README.rst", encoding="utf-8").read(),
)

# python setup.py sdist
# twine upload dist/*
