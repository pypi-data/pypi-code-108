# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['basis',
 'basis.cli',
 'basis.cli.commands',
 'basis.cli.services',
 'basis.configuration',
 'basis.graph',
 'basis.helpers',
 'basis.node',
 'basis.node.sql',
 'basis.utils']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=3.0.0,<4.0.0',
 'pandas>=1,<2',
 'platformdirs>=2.4.0,<3.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'requests-mock>=1.9.3,<2.0.0',
 'rich>=10.15.2,<11.0.0',
 'ruyaml>=0.91.0,<0.92.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['basis = basis.cli.main:main']}

setup_kwargs = {
    'name': 'basis-devkit',
    'version': '0.1.3',
    'description': 'Data pipelines from re-usable components',
    'long_description': None,
    'author': 'AJ Alt',
    'author_email': 'aj@getbasis.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
