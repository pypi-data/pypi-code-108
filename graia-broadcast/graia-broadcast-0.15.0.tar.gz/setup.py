# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['graia',
 'graia.broadcast',
 'graia.broadcast.builtin',
 'graia.broadcast.entities',
 'graia.broadcast.interfaces',
 'graia.broadcast.interrupt']

package_data = \
{'': ['*']}

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['typing-extensions>=3.10.0,<4.0.0']}

setup_kwargs = {
    'name': 'graia-broadcast',
    'version': '0.15.0',
    'description': 'a highly customizable, elegantly designed event system based on asyncio',
    'long_description': None,
    'author': 'GreyElaina',
    'author_email': 'GreyElaina@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
