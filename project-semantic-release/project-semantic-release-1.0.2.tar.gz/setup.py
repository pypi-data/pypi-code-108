# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['semantic_release',
 'semantic_release.changelog',
 'semantic_release.history',
 'semantic_release.history.parser_gitmoji']

package_data = \
{'': ['*'], 'semantic_release': ['templates/*']}

install_requires = \
['chevron>=0.14,<0.15',
 'click>=8.0,<9.0',
 'click_log>=0.3,<0.4',
 'dotty-dict>=1.3,<2.0',
 'dynaconf[toml,ini]>=3.1,<4.0',
 'gitpython>=3.1,<4.0',
 'invoke>=1.6,<2.0',
 'python-gitlab>=3.1,<4.0',
 'requests>=2.27,<3.0',
 'semver>=2.13,<3.0',
 'tomlkit>=0.8,<0.9',
 'twine>=3.7,<4.0',
 'wheel']

extras_require = \
{'emoji': ['emoji>=1.6,<2.0']}

entry_points = \
{'console_scripts': ['semantic-release = semantic_release.cli:entry']}

setup_kwargs = {
    'name': 'project-semantic-release',
    'version': '1.0.2',
    'description': 'Automatic semantic versioning for python projects',
    'long_description': '# project-semantic-release\nAutomatic semantic versioning for python projects\n',
    'author': 'MaxST',
    'author_email': 'mstolpasov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mom1/project-semantic-release',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
