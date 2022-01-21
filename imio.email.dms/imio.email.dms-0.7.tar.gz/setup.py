# -*- coding: utf-8 -*-
"""Installer for the imio.email.dms package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='imio.email.dms',
    version='0.7',
    description="Package to read emails and send them to DMS",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python',
    author='Laurent Lasudry',
    author_email='info@affinitic.be',
    url='https://pypi.python.org/pypi/imio.email.dms',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['imio', 'imio.email'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'setuptools',
        'docopt',
        'zc.lockfile',
        'imio.email.parser',
        'pathlib2;python_version<"3.0"',
        'requests',
        'six',
        'configparser',
    ],
    extras_require={
    },
    entry_points="""
    [console_scripts]
    process_mails = imio.email.dms.main:process_mails
    clean_mails = imio.email.dms.main:clean_mails
    """,
)
