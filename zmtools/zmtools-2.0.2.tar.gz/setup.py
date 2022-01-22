# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zmtools']

package_data = \
{'': ['*']}

install_requires = \
['click>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'zmtools',
    'version': '2.0.2',
    'description': "Various tools used across Zeke Marffy's programs",
    'long_description': '# zmtools\n\nA conglomeration of functions reused in my program; maybe they can help you too. The docstrings should explain all you need to know.\n',
    'author': 'Zeke Marffy',
    'author_email': 'zmarffy@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zmarffy/zmtools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
