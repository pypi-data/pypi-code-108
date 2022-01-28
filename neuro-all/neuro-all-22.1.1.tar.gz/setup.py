# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neuro_all']

package_data = \
{'': ['*']}

install_requires = \
['certifi==2021.10.8',
 'neuro-cli==22.1.3',
 'neuro-extras==21.11.5',
 'neuro-flow==22.1.0']

entry_points = \
{'console_scripts': ['docker-credential-neuro = '
                     'neuro_cli.docker_credential_helper:main',
                     'neuro = neuro_cli.main:main',
                     'neuro-extras = neuro_extras:main',
                     'neuro-flow = neuro_flow.cli:main'],
 'neuro_api': ['neuro-all = neuro_all:setup']}

setup_kwargs = {
    'name': 'neuro-all',
    'version': '22.1.1',
    'description': "Combo package for installing all neu.ro command line tools by 'pipx install neuro-all' command",
    'long_description': '# neuro-all\nCombo package for installing all neu.ro command line tools by `pipx install neuro-all` command\n',
    'author': 'Neu.ro Team',
    'author_email': 'team@neu.ro',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://neu.ro',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
