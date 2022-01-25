#!/usr/bin/env python

from setuptools import setup, find_packages

#
# project dependencies
#

install_requires = [
    'pyyaml',
    'tornado==3.0.1',
    'toro==0.5',
    'passlib==1.6'
]

#
# Setuptools configuration, used to create python .eggs and such.
# See: http://bashelton.com/2009/04/setuptools-tutorial/ for a nice
# setuptools tutorial.
#

setup(
    # metadata
    name="cloudomate-thecloudgarage",
    version="2",
    author="thecloudgarage",
    author_email="ambar.thecloudgarage@gmail.com",
    description="Expose a set of shell scripts as an API.",
    url="https://github.com/thecloudgarage/cloudomate.git",
    
    # packaging info
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=install_requires,
    
    entry_points={
        'console_scripts': [
            'cloudomate = cloudomate.server:main'
        ]
    },
    
    zip_safe=False
)

