# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ehelply_microservice_library',
 'ehelply_microservice_library.cli',
 'ehelply_microservice_library.integrations',
 'ehelply_microservice_library.realtime',
 'ehelply_microservice_library.routers',
 'ehelply_microservice_library.utils',
 'ehelply_microservice_library.utils.constants']

package_data = \
{'': ['*']}

install_requires = \
['ehelply-bootstrapper>=0.15.0,<0.16.0',
 'ehelply-generator>=0.1.2,<0.2.0',
 'ehelply-python-sdk>=0.2.8,<0.3.0',
 'ehelply-updater>=0.1.5,<0.2.0',
 'jinja2>=2.11.3,<3.0.0',
 'pytest-mock>=3.6.1,<4.0.0']

entry_points = \
{'console_scripts': ['ehelply_microservice_library = '
                     'ehelply_microservice_library.cli.self_cli:cli_main']}

setup_kwargs = {
    'name': 'ehelply-microservice-library',
    'version': '1.6.10',
    'description': '',
    'long_description': '## Building\n* `poetry publish --build`\n\n## Development\n* `ehelply_microservice_library dev export-code-docs`\n* Clear cache: `poetry cache clear pypi --all`',
    'author': 'Shawn Clake',
    'author_email': 'shawn.clake@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ehelply.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
