#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 00:09:16 2020

@author: Scott Tuttle
"""
import setuptools
if __name__ == "__main__":
    setuptools.setup()


# from pathlib import Path
# from setuptools import setup, find_packages
#
# with open('README.rst', 'r') as readme:
#     long_description = readme.read()
#
#
# def get_version(rel_path):
#     target_path = Path(__file__).resolve().parent.joinpath(rel_path)
#     with open(target_path, 'r') as file:
#         for line in file:
#             if line.startswith('__version__'):
#                 delimiter = '"' if '"' in line else "'"
#                 return line.split(delimiter)[1]
#         else:
#             raise RuntimeError("Unable to find version string.")
#
#
# setup(
#       name='scottbrian_utils',
#       version=get_version('src/scottbrian_utils/__init__.py'),
#       author='Scott Tuttle',
#       description='Print header/trailer utilities',
#       long_description=long_description,
#       long_description_content_type='text/x-rst',
#       url='https://github.com/ScottBrian/scottbrian_utils.git',
#       license='MIT',
#       classifiers=[
#           'License :: OSI Approved :: MIT License',
#           'Development Status :: 5 - Production/Stable',
#           'Intended Audience :: Developers',
#           'Topic :: Utilities',
#           'Programming Language :: Python :: 3',
#           'Programming Language :: Python :: 3.8',
#           'Programming Language :: Python :: 3.9',
#           'Operating System :: POSIX :: Linux'
#                   ],
#       project_urls={
#           'Documentation': 'https://scottbrian-utils.readthedocs.io/en'
#                            '/latest/',
#           'Source': 'https://github.com/ScottBrian/scottbrian_utils.git'},
#       python_requires='>=3.8',
#       packages=find_packages('src'),
#       package_dir={'': 'src'},
#       install_requires=['typing-extensions', 'wrapt'],
#       package_data={"scottbrian_utils": ["__init__.pyi", "py.typed"]},
#       zip_safe=False
#      )
