# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ou_container_builder',
 'ou_container_builder.generators',
 'ou_container_builder.packs',
 'ou_container_builder.templates.generators.jupyter_notebook',
 'ou_container_builder.templates.generators.web_app']

package_data = \
{'': ['*'],
 'ou_container_builder': ['templates/*',
                          'templates/packs/mariadb/*',
                          'templates/packs/services/*',
                          'templates/packs/tutorial-server/*']}

install_requires = \
['cerberus>=1.3.3,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'jinja2>=2.11.3,<3.0.0',
 'pyyaml>=5.4.1,<6.0.0']

entry_points = \
{'console_scripts': ['ou-container-builder = '
                     'ou_container_builder.__main__:main']}

setup_kwargs = {
    'name': 'ou-container-builder',
    'version': '1.0.8',
    'description': '',
    'long_description': None,
    'author': 'Mark Hall',
    'author_email': 'mark.hall@open.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
