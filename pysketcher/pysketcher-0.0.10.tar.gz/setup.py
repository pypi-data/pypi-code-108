# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysketcher',
 'pysketcher._utils',
 'pysketcher.annotation',
 'pysketcher.backend',
 'pysketcher.backend.matplotlib',
 'pysketcher.composition',
 'pysketcher.dimension']

package_data = \
{'': ['*'], 'pysketcher': ['images/.gitignore']}

install_requires = \
['celluloid>=0.2.0,<0.3.0',
 'matplotlib>=3.2.1,<4.0.0',
 'numpy>=1.19.5,<2.0.0',
 'scipy>=1.7.3,<2.0.0']

extras_require = \
{'docs': ['sphinx>=4.1.1,<5.0.0',
          'sphinx_rtd_theme>=0.5,<1.1',
          'sphinx-autodoc-typehints>=1.11.1,<2.0.0']}

entry_points = \
{'console_scripts': ['beam1 = examples.beam1:main']}

setup_kwargs = {
    'name': 'pysketcher',
    'version': '0.0.10',
    'description': 'Geometric Sketching Utility for Python',
    'long_description': '============\n PySketcher\n============\n\n.. image:: https://github.com/rvodden/pysketcher/workflows/Tests/badge.svg\n    :target: https://github.com/rvodden/pysketcher/actions?query=workflow%3ATests+branch%3Amaster\n\n.. image:: https://badgen.net/pypi/v/pysketcher?icon=pypi\n       :target: https://pypi.org/project/pysketcher/\n\n.. image:: https://api.codeclimate.com/v1/badges/eae2c2aa97080fbfed7e/maintainability\n    :target: https://codeclimate.com/github/rvodden/pysketcher/maintainability\n\n.. image:: https://codecov.io/gh/rvodden/pysketcher/branch/master/graph/badge.svg?token=AHCKOL75VY\n    :target: https://codecov.io/gh/rvodden/pysketcher\n\n.. image:: https://readthedocs.org/projects/pysketcher/badge/?version=latest&style=flat\n    :target: https://pysketcher.readthedocs.io/en/latest/\n\n.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n    :target: https://github.com/pre-commit/pre-commit\n\n.. image:: https://img.shields.io/badge/hypothesis-tested-brightgreen.svg\n    :target: https://hypothesis.readthedocs.io/\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\n.. image:: https://badgen.net/github/dependabot/rvodden/pysketcher?icon=github\n    :target: https://github.com/rvodden/pysketcher\n\n**This is alpha software - the interface is likely to change with every release prior to 0.1.0.**\n\nPySketcher is a modern Python library designed to make creating geometric, mathematical and physical diagrams very\neasy.\n\nThis library is continues the legacy of Hans Petter Langtangen. Work done since he sadly passed in 2016 includes:\n\n1. The MatlibplotDraw object is no longer global and is no longer tightly coupled to the shape object. There is now a DrawingTool interface which this class implements.\n\n2. Code is organised into multiple files and published on pypi.\n\n3. Shapes are immutable. This means functions such as ``rotate`` return modified copies of the original shape, rather than altering the shape on which they are called.\n\n4. Angles are in radians not degrees.\n\n5. The Composition object is used more consistently. Previously objects such as Beam were direct children of Shape which led to code repetition.\n\n`Please see the documentation for more information <https://pysketcher.readthedocs.io/en/latest/index.html>`_.\n',
    'author': 'Richard Vodden',
    'author_email': 'richard@vodden.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rvodden/pysketcher',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
