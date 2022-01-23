# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['serena', 'serena.payloads', 'serena.utils']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.5.0,<4.0.0', 'attrs>=21.4.0,<22.0.0']

extras_require = \
{':python_version < "3.11"': ['backports.strenum'],
 'docs': ['Sphinx>=4.3.2,<5.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0',
          'sphinx-inline-tabs>=2022.1.2-beta.11,<2023.0.0',
          'sphinxcontrib-trio>=1.1.2,<2.0.0',
          'sphinx-autodoc-typehints>=1.15.2,<2.0.0']}

setup_kwargs = {
    'name': 'serena',
    'version': '0.7.0',
    'description': 'An AMQP 0-9-1 client using AnyIO.',
    'long_description': 'Serena\n======\n\n*Serena* is a pure-Python, structually concurrent AMQP 0-9-1 client.\n\nSee https://amqp.py.veriny.tf/ for more information.\n',
    'author': 'Lura Skye',
    'author_email': 'l@veriny.tf',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
