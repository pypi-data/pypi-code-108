# -*- coding: utf-8 -*-
from setuptools import setup

with open('README.md') as f:
    readme = f.read()
with open('requirements.txt') as f:
    requires = [line.strip() for line in f if line.strip()]

setup(
    name='pyapplemusicapi',
    version='2.0.0',
    description='A simple Python interface to search the Apple Music and Apple TV libraries',
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Vinyl Da.i'gyu-Kazotetsu",
    author_email="queen@gooborg.com",
    maintainer="Vinyl Da.i'gyu-Kazotetsu",
    maintainer_email="queen@gooborg.com",
    license='http://www.gnu.org/licenses/gpl-3.0.html',
    platforms=['any'],
    url='https://github.com/queengooborg/pyapplemusicapi',
    project_urls={
        "Bug Tracker": "https://github.com/queengooborg/pyapplemusicapi/issues"
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    packages=['pyapplemusicapi'],
    install_requires=requires,
    zip_safe=False,
    python_requires=">=3.6"
)
