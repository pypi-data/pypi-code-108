"""
wmpaws
-------------

This is the description for that library
"""
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='wmpaws',
    version='1.0',
    license='GNU',
    author='Martin Urbanec',
    author_email='martin@urbanec.cz',
    description='A library for Wikimedia\'s PAWS service.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_dir={"": 'src'},
    packages=setuptools.find_packages(where="src"),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'requests',
        'requests_oauthlib',
        'pymysql',
        'pandas',
        'ipython'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
