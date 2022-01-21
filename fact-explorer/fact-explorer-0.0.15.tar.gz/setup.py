# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fact_explorer',
 'fact_explorer.app',
 'fact_explorer.app.api',
 'fact_explorer.app.business',
 'fact_explorer.app.db',
 'fact_explorer.app.entities',
 'fact_explorer.app.frontend',
 'fact_explorer.cli']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.6,<0.7',
 'asyncpg>=0.22,<0.23',
 'fastapi>=0.65,<0.66',
 'psycopg2-binary>=2.8,<3.0',
 'pyjson5==1.6.0',
 'rich>=10.4,<11.0',
 'typer>=0,<1',
 'uvicorn>=0.13,<0.14']

extras_require = \
{'crypto': ['cryptoshred>=0.0,<0.1'],
 'docs': ['sphinx-autodoc-typehints>=1.12,<2.0',
          'sphinx-rtd-theme>=0.5,<0.6',
          'sphinx-click>=3.0,<4.0',
          'Sphinx<4'],
 'schema': ['schema-registry>=0.0,<0.1']}

entry_points = \
{'console_scripts': ['fact-explorer = fact_explorer.cli.main:app']}

setup_kwargs = {
    'name': 'fact-explorer',
    'version': '0.0.15',
    'description': 'A fast and simple tool to explore facts.',
    'long_description': "# Fact Explorer\n\nWelcome to fact_explorer. You can find more extensive documentation over at [readthedocs](https://fact-explorer.readthedocs.io/en/latest/).\n\nThis is a companion project to `factcast <https://github.com/factcast/factcast>`_ an event store written in Java.\nYou can also check out other event sourcing related project in python over at `pyfactcast <https://pypi.org/project/pyfactcast/>`_\nas well as `cryptoshred <https://pypi.org/project/cryptoshred/>`_.\n\nThis project arose mainly out of the necessity to work with events directly instead of through projections. This is useful to:\n\n- Enable searching for 'random' events quickly during debugging\n- Checking events during migrations\n- Many other things (you should probably not do if you are an event purist)\n\nContributions are welcome. Just get in touch.\n\n## Quickstart\n\nSimply `pip install fact-exporter` and get going. The cli is available as `fact-exporter` and\nyou can run `fact-exporter --help` to get up to speed on what you can do.\n\n## Development\n\nThis project uses `poetry` for dependency management and `pre-commit` for local checks.\n",
    'author': 'Eduard Thamm',
    'author_email': 'eduard.thamm@thammit.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/friendly-facts/fact-explorer',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
