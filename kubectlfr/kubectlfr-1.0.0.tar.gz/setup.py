# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kubectlfr']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['kubectlfr = kubectlfr:main']}

setup_kwargs = {
    'name': 'kubectlfr',
    'version': '1.0.0',
    'description': 'Utilitaire de contrôle de Kubernetes',
    'long_description': '# Utilitaire de contrôle de Kubernetes\n\n> ** What is this ??? **\n> Every time we use a word in English our manager tells us to use the French translation of it. So, here is a version of kubectl ... in French !\n\n',
    'author': 'Théophane Vié',
    'author_email': 'theophane.vie@petit-nuage.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theophanevie/kubectlfr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
