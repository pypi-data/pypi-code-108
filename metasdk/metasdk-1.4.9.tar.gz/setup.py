#!/usr/bin/env python
from os import path

import setuptools


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


from metasdk import info

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

packages = [
    'metasdk',
    'metasdk.tools',
    'metasdk.logger',
    'metasdk.services'
]

install_reqs = parse_requirements('requirements.txt')
reqs = install_reqs

setuptools.setup(
    name=info.__package_name__,
    version=info.__version__,

    description='Devision Meta SDK',
    long_description=long_description,

    url='https://github.com/devision-io/metasdk',

    author='Artur Geraschenko',
    author_email='arturgspb@gmail.com',

    license='MIT',

    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    install_requires=reqs,
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'metasdk': 'metasdk'},
    include_package_data=True,
)
