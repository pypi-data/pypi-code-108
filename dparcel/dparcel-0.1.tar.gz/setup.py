# Copyright (c) 2021 Thomas Schanzer.
# Distributed under the terms of the BSD 3-Clause License.
"""Setup file for the dparcel package."""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='dparcel',
    version='0.1',
    description=('A simple parcel theory model of downdrafts '
                 'in atmospheric convection.'),
    long_description=readme(),
    long_description_content_type='text/x-rst',
    url='https://github.com/climate-enigma/dparcel',
    author='Thomas Schanzer',
    author_email='t.schanzer@student.unsw.edu.au',
    license='BSD 3-Clause License',
    packages=['dparcel'],
    install_requires=[
        'numpy',
        'metpy>=1.2',
        'scipy',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
    ],
    keywords='parcel downdraft atmosphere convection model',
    include_package_data=True,
    zip_safe=False,
    project_urls={
        'Documentation': 'https://dparcel.readthedocs.io/',
        'Source Code': 'https://github.com/climate-enigma/dparcel',
        'Bug Tracker': 'https://github.com/climate-enigma/dparcel/issues',
        'Release Notes': 'https://github.com/climate-enigma/dparcel/releases',
    }
)
