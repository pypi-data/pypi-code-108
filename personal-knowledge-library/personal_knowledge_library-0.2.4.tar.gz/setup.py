#!/usr/bin/env python
import pathlib
from setuptools import setup, find_packages

import sys
CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 6)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of personal knowledge lib requires Python {}.{}, but you're trying to
install it on Python {}.{}.
This may be because you are using a version of pip that doesn't
understand the python_requires classifier. Make sure you
have pip >= 9.0 and setuptools >= 24.2, then try again:
    $ python -m pip install --upgrade pip setuptools
This will install the latest version of knowledge-service-lib which works on your
version of Python. If you can't upgrade your pip (or Python), request
an older version of knowledge-service-lib :
    $ python -m pip install wacom-knowledge-services-library
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)

# The directory containing this file
HERE = pathlib.Path(__file__).parent
__version__ = "0.2.4"

# The text of the README file
README = (HERE / "README.md").read_text()

# the setup
setup(
    name='personal_knowledge_library',
    version=__version__,
    description="Library to access Wacom's Personal Knowledge graph.",
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/Wacom-Developer/personal-knowledge-library',
    author='Markus Weber',
    author_email='markus.weber@wacom.com',
    license='Apache 2.0 License',
    keywords='semantic-knowledge;knowledge-graph',
    packages=find_packages(exclude=('docs', 'tests', 'env')),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.1",
        "qwikidata>=0.4.0",
        "python-dateutil>=2.8.2",
        "tqdm>=4.62.0",
        "ndjson>=0.3.1",
        "rdflib>=6.0.2"
    ],
    extras_require={
    },
    tests_require=(
        'pytest',
        'pytest-cov'
    ),
    classifiers=[],
    )
