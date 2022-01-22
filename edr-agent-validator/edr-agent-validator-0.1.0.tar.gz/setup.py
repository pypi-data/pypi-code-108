# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['edr_agent_validator']

package_data = \
{'': ['*']}

install_requires = \
['desert>=2020.11.18,<2021.0.0',
 'marshmallow-enum>=1.5.1,<2.0.0',
 'marshmallow>=3.14.1,<4.0.0',
 'psutil>=5.9.0,<6.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['edr-agent-validator = edr_agent_validator.console:app']}

setup_kwargs = {
    'name': 'edr-agent-validator',
    'version': '0.1.0',
    'description': 'The Red Canary EDR validation tool.',
    'long_description': 'This is an EDR agent validator project for the Red Canary Engineering Interview.\n\n',
    'author': 'Andrew Kennedy',
    'author_email': 'andrewk36@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andrew-kennedy/edr-agent-validator',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
