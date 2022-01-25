#!/usr/bin/env python3

import setuptools

#with open("README.md", "r") as fh:
    #long_description = fh.read()

setuptools.setup(
    name='mmis',
    version='1.36',
    author='Rajeev Bheemireddy TUDelft-DEMO',
    description='control software for the Modular Microscope Instrument',
    #long_description=long_description,
    packages=['mmis'],
    #download_url=['https://homepage.tudelft.nl/6w77j/MMI/MMI.tar.gz'],
    package_data={'mmis':['Images/*.*']},
    install_requires=['python-memcached', 'pyPubSub', 'distro', 'beautifulsoup4'],
    )
