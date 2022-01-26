# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['castutils', 'castutils.builtins']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'castutils',
    'version': '0.2.3',
    'description': 'Variable transformation and casting utilities (Python)',
    'long_description': None,
    'author': 'Shane Spencer',
    'author_email': '305301+whardier@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
