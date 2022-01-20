# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tasq_cli']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.1.2,<4.0.0',
 'altgraph>=0.17,<0.18',
 'boto3>=1.16.4,<2.0.0',
 'botocore>=1.19.4,<2.0.0',
 'docutils>=0.16,<0.17',
 'jmespath>=0.10.0,<0.11.0',
 'pillow>=8.0.1,<9.0.0',
 'pyinstaller-hooks-contrib>=2020.9,<2021.0',
 'pyinstaller>=4.0,<5.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'python-dotenv>=0.14.0,<0.15.0',
 'requests>=2.23.0,<3.0.0',
 's3transfer>=0.3.3,<0.4.0',
 'urllib3>=1.25.11,<2.0.0']

entry_points = \
{'console_scripts': ['tasq = tasq_cli.main:main']}

setup_kwargs = {
    'name': 'tasq-cli',
    'version': '1.0.30',
    'description': 'The command line tool for tasq.ai.',
    'long_description': None,
    'author': 'tasq.ai',
    'author_email': 'info@tasq.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
