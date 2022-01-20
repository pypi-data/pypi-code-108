# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fact_lake']

package_data = \
{'': ['*']}

install_requires = \
['cryptoshred>=0.0.7,<0.0.8',
 'pydantic>=1.9.0,<2.0.0',
 'pyfactcast>=0.0.9,<0.0.10',
 'pymongo>=4.0.1,<5.0.0',
 'rich<11',
 'typer<0.4']

extras_require = \
{'docs': ['sphinx<4',
          'sphinx-click>=2.7,<3.0',
          'sphinx-rtd-theme>=0.5,<0.6',
          'sphinx-autodoc-typehints>=1.12,<2.0']}

entry_points = \
{'console_scripts': ['fact-lake = fact_lake.cli:typer_app']}

setup_kwargs = {
    'name': 'fact-lake',
    'version': '0.0.4',
    'description': 'A datalake that is keeping up to date with your factcast',
    'long_description': '# Fact Lake\n\nJust a project stub for now\n\nContributions are welcome. Just get in touch.\n\n## Quickstart\n\nSimply `pip install fact-lake` and get going.\n\n## Development\n\nThis project uses `poetry` for dependency management and `pre-commit` for local checks.\n',
    'author': 'Eduard Thamm',
    'author_email': 'eduard.thamm@thammit.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/friendly-facts/fact-lake',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
