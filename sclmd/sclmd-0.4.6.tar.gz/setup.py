#!usr/bin/env python
# -*- coding:utf-8 _*-
from setuptools import setup, find_packages

VERSION = '0.4.6'

setup(
    name='sclmd',
    version=VERSION,
    description='Semi-classical Langevin molecular dynamics',
    long_description='Molecular dynamics script using a semi-classical generalized Langevin equation',
    keywords='molecular dynamics, quantum bath, semiclassical generalized Langevin equation',
    author='Jing-Tao Lv',
    author_email='jtlu@hust.edu.cn',
    url='https://github.com/ApertureG/sclmd',
    license='GNU General Public License v3.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "numpy>=1.8.2",
        "netCDF4",
        "tqdm",
    ],
    python_requires='>=3.7',
    #entry_points={
    #    'console_scripts': [
    #        'sclmd = sclmd.main:main'
    #    ]
    #}
)