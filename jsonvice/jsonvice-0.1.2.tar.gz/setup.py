# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jsonvice']

package_data = \
{'': ['*']}

install_requires = \
['coveralls>=3.3.1,<4.0.0', 'tox>=3.24.5,<4.0.0']

entry_points = \
{'console_scripts': ['jsonvice = jsonvice.jsonvice:cli']}

setup_kwargs = {
    'name': 'jsonvice',
    'version': '0.1.2',
    'description': 'jsonvice minifies JSON files by trimming floating point precision.',
    'long_description': '[![PyPI version](https://badge.fury.io/py/jsonvice.svg)](https://badge.fury.io/py/jsonvice)\n[![Build Status](https://travis-ci.org/deftio/jsonvice.svg?branch=master)](https://travis-ci.org/deftio/jsonvice)\n[![License](https://img.shields.io/badge/License-BSD%202--Clause-blue.svg)](https://opensource.org/licenses/BSD-2-Clause)\n\n\n# About jsonvice  \n\njsonvice is small command line tool (cli) for minifying JSON but with optimal precision truncation/rounding.  In many applications floating point values in JSON can be very long (15 digits) but this level of accuracy isn\'t needed and takes up much space.\n\njsonvice allows the truncation of all the embedded floating point numbers to a specified number of digits. \n\nIt also removes unencessary white space to help minify JSON files. However there are many tools that can minify JSON.\n\ninput.json\n```json\n{\n    "x" :   12.32,\n    "y": 0.23482498323433,\n    "z": "simple test",\n    "a" : [ 1, 2, 3.23423434343 ]\n}\n```\n\nrun jsonvice\n```sh\njsonvice -i input.json -o output.json -p 4\n```\n\nouput.json\n```json\n{"x":12.32,"y":0.2348,"z":"simple test","a":[1,2,3.2342]}\n```\n\n\n# More Examples\n\ncompactify json and reduce floating point precision to max of 5 digits by rounding\n```shell\njsonvice -i myfile.json -o output.json -p 5\n```\n\ncompactify json and reduce floating point precision to max of 5 digits by rounding down\n```shell\njsonvice -i myfile.json -o output.json -p 5 -q floor\n```\n\njsonvice also allows stdin / stdout pipes to be used\n```shell\ncat simple_test.json | python3 path/to/jsonvice.py -i - -o - > output_test.json\n```\n\njsonvice can also beautify (pretty print) json, while still performing precision truncation.  Note this makes the file larger.\n```shell\njsonvice -i myfile.json -o output.json -p 3 -b\n```\n\n\n# Building and Source\nAll source is at [jsonvice](https://github.com/deftio/jsonvice)\n\njsonvice is built with Python using the Poetry packaging and build tool.\n\npip3 install poetry  # if not installed.\n\npoetry update\npoetry install\npoetry build\n\npoetry run jsonvice ...parameters...\n\nExample\n```sh\npoetry run jsonvice -i inputfile.json -o outputfile.json -p 4\n```\n\n# Installing as stand alone cli\npipx (not pip3) can be used to install an isolated version of jsonvice as a command line tool.\n\n```sh\npipx install jsonvice\n```\n\nor install from github repo \n\n```sh\npipx install git+https://github.com/deftio/jsonvice\n```\n\n## Python version support\nPython version 3.6 or higher is required to build\n\n# Testing\npoetry run pytest\n\n# History & Motivation\njson vice started as a script to compactify / minify some large machine learning model files which had large floating point numbers.   By rounding to fixed number of sig digits and then testing the models against testsuites to see the effects of truncation.\n\nAt the time couldn\'t find a tool and whipped up small script (the original script is in /dev directory).\n\nSo jsonvice was built to learn / test practices around the python poetry and pipx tools, for use in other projects, but starting with a small example cli program that already worked.\n\n# License\njsonvice uses the BSD-2 open source license\n',
    'author': 'Manu Chatterjee',
    'author_email': 'deftio@deftio.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/deftio/jsonvice',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
