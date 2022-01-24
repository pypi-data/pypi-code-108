# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['poetry_changelog']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'poetry-changelog',
    'version': '0.1.0',
    'description': '',
    'long_description': '# poetry-changelog\n\nWIP\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
