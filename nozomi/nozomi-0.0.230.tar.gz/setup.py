"""
Nozomi
PyPI Setup Module
Copyright Amatino Pty Ltd
"""
from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'readme.md'), encoding='utf-8') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

with open(path.join(here, 'VERSION'), encoding='utf-8') as version_file:
    VERSION = version_file.read()

setup(
    name='nozomi',
    version=VERSION,
    description='HTTP web application & API protocol library',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/amatino-code/nozomi',
    author='Amatino',
    author_email='hugh@blinkybeach.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries'
    ],
    keywords='library http api web application',
    packages=find_packages(exclude=('tests', 'tests.*')),
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    install_requires=[],
    project_urls={
        'Github Repository': 'https://github.com/amatino-code/nozomi',
        'About': 'https://github.com/amatino-code/nozomi'
    }
)
