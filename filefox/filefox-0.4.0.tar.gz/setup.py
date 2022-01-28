# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['filefox']

package_data = \
{'': ['*']}

install_requires = \
['pytoml>=0.1.21,<0.2.0']

setup_kwargs = {
    'name': 'filefox',
    'version': '0.4.0',
    'description': 'Python file toolbox.',
    'long_description': None,
    'author': 'Yevgnen Koh',
    'author_email': 'wherejoystarts@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
