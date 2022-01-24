# -*- coding: utf-8 -*-
"""Installer for the imio.smartweb.locales package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="imio.smartweb.locales",
    version="1.0a10",
    description="Locales for iMio smartweb packages",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="iMio",
    author_email="christophe.boulanger@imio.be",
    url="https://github.com/imio/imio.smartweb.locales",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/imio.smartweb.locales",
        "Source": "https://github.com/imio/imio.smartweb.locales",
        "Tracker": "https://github.com/imio/imio.smartweb.locales/issues",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["imio", "imio.smartweb"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
    ],
    extras_require={},
    entry_points="",
)
