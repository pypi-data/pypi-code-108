#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'iris_hector_patino'
DESCRIPTION = "IRIS MODEL ROTE"
EMAIL = "hectorpatino24@gmail.com"
AUTHOR = "hectorpatino"
REQUIRES_PYTHON = ">=3.6.0"


# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the
# Trove Classifier for that!
long_description = DESCRIPTION

# Load the package's VERSION file as a dictionary.
about = {}
ROOT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_DIR = ROOT_DIR / 'requirements'
PACKAGE_DIR = ROOT_DIR / 'iris_hector_patino'
with open(PACKAGE_DIR / "VERSION") as f:
    _version = f.read().strip()
    about["__version__"] = _version


# What packages are required for this module to be executed?
def list_reqs(fname="requirements.txt"):
    with open(REQUIREMENTS_DIR / fname) as fd:
        return fd.read().splitlines()

# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=("tests",)),
    package_data={"iris_hector_patino": ["VERSION"]},
    install_requires=[
        'alembic==1.7.5',
        'atomicwrites==1.4.0',
        'attrs==21.4.0',
        'autopage==0.4.0',
        'cliff==3.10.0',
        'cmaes==0.8.2',
        'cmd2==2.3.3',
        'colorama==0.4.4',
        'colorlog==6.6.0',
        'distlib==0.3.4',
        'feature-engine==1.2.0',
        'filelock==3.4.2',
        'greenlet==1.1.2',
        'importlib-metadata==4.10.0',
        'importlib-resources==5.4.0',
        'iniconfig==1.1.1',
        'joblib==1.1.0',
        'Mako==1.1.6',
        'MarkupSafe==2.0.1',
        'numpy==1.22.0',
        'optuna==2.10.0',
        'packaging==21.3',
        'pandas==1.3.5',
        'patsy==0.5.2',
        'pbr==5.8.0',
        'platformdirs==2.4.1',
        'pluggy==1.0.0',
        'prettytable==3.0.0',
        'py==1.11.0',
        'pydantic==1.9.0',
        'pyparsing==3.0.6',
        'pyperclip==1.8.2',
        'pyreadline3==3.3',
        'pytest==6.2.5',
        'python-dateutil==2.8.2',
        'pytz==2021.3',
        'PyYAML==6.0',
        'scikit-learn==1.0.2',
        'scipy==1.7.3',
        'six==1.16.0',
        'sklearn==0.0',
        'SQLAlchemy==1.4.29',
        'statsmodels==0.13.1',
        'stevedore==3.5.0',
        'strictyaml==1.6.1',
        'threadpoolctl==3.0.0',
        'toml==0.10.2',
        'tox==3.24.5',
        'tqdm==4.62.3',
        'virtualenv==20.13.0',
        'wcwidth==0.2.5',
        'xgboost==1.5.1',
        'zipp==3.7.0',
    ],
    extras_require={},
    include_package_data=True,
    license="BSD-3",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)