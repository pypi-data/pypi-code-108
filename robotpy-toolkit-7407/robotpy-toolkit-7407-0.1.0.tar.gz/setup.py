# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robotpy_toolkit_7407',
 'robotpy_toolkit_7407.motors',
 'robotpy_toolkit_7407.network',
 'robotpy_toolkit_7407.oi',
 'robotpy_toolkit_7407.sensors',
 'robotpy_toolkit_7407.sensors.gyro',
 'robotpy_toolkit_7407.subsystem_templates',
 'robotpy_toolkit_7407.subsystem_templates.drivetrain',
 'robotpy_toolkit_7407.utils']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0', 'robotpy[ctre,commands2,rev]>=2022.0.21,<2023.0.0']

setup_kwargs = {
    'name': 'robotpy-toolkit-7407',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Ethan Chapman',
    'author_email': 'ethan.chapman0@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
