# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cg_hermes', 'cg_hermes.cli', 'cg_hermes.config', 'cg_hermes.models']

package_data = \
{'': ['*']}

install_requires = \
['bump2version>=1.0.1,<2.0.0',
 'cgmodels>=0.4.0,<0.5.0',
 'coloredlogs>=14.0,<15.0',
 'pydantic>=1.7.3,<2.0.0',
 'pyyaml>=5.3.1,<6.0.0',
 'tabulate>=0.8.7,<0.9.0',
 'typer>=0.3.2,<0.4.0',
 'typing-extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['hermes = cg_hermes.__main__:main']}

setup_kwargs = {
    'name': 'cg-hermes',
    'version': '1.6.12',
    'description': 'Convert information between pipelines and CG',
    'long_description': None,
    'author': 'Måns Magnusson',
    'author_email': 'mans.magnusson@scilifelab.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
