#!/usr/bin/env python

from os.path import join, dirname, abspath, isfile
from distutils.core import setup
from setuptools import find_packages

this_directory = abspath(dirname(__file__))
with open(join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = []
if isfile(join(this_directory, "requirements.txt")):
    with open(join(this_directory, "requirements.txt"), encoding='utf-8') as f:
        install_requires = f.readlines()

setup(name='attributee',
    version="0.1.5",
    description='Declarative object initialization library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Luka Cehovin Zajc',
    author_email='luka.cehovin@gmail.com',
    url='https://github.com/lukacu/attributee',
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires='>=3.5'
)

