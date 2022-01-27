# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['carte_cli',
 'carte_cli.extractor',
 'carte_cli.loader',
 'carte_cli.model',
 'carte_cli.publisher',
 'carte_cli.scaffolding',
 'carte_cli.utils']

package_data = \
{'': ['*'], 'carte_cli.utils': ['templates/*']}

install_requires = \
['Jinja2>=2.11.3,<2.12.0',
 'amundsen-databuilder==4.2.2',
 'boto3>=1.17.2,<1.18.0',
 'click-spinner>=0.1.10,<0.2.0',
 'ruamel.yaml>=0.16.12,<0.17.0',
 'typer>=0.3.2,<0.4.0']

extras_require = \
{'postgres': ['psycopg2>=2.8.6,<2.9.0', 'SQLAlchemy>=1.4.18,<1.5.0']}

entry_points = \
{'console_scripts': ['carte = carte_cli.main:app']}

setup_kwargs = {
    'name': 'carte-cli',
    'version': '0.3.19',
    'description': 'A static site generator for data catalogs',
    'long_description': '# Carte\n[![PyPI version](https://badge.fury.io/py/carte-cli.svg)](https://badge.fury.io/py/carte-cli)\n![PyPI - License](https://img.shields.io/pypi/l/carte-cli)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/carte_cli.svg)](https://pypi.org/project/carte-cli/)\n\n\nCarte is a Python library for extracting metadata from your data sources and generating structured Markdown files from it. It can also scaffold an MkDocs based static site that provides an easy to use, fully searchable UI that you can simply upload to any static site hosting provider. Carte currently supports the AWS Glue catalog, PostgreSQL, and JSON schemas (only basic support). More sources are coming soon. (You can also use sources from the [Amundsen Databuilder](https://github.com/amundsen-io/amundsendatabuilder) library with a bit of scripting, see [the docs](https://docs.cartedata.com/reference/databuilder/) for details)\n\n\n## Installation\n\n``` sh\npip install carte-cli\n```\n\nIf you plan to use PostgreSQL as a data source, you should also install the related optional dependencies using the following command instead of the first one:\n\n``` sh\npip install carte-cli[postgres]\n```\n\n\n\n## Usage\n\nSee [the docs](https://docs.cartedata.com)\n',
    'author': 'Balint Haller',
    'author_email': 'balint@hey.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cartedata.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
