# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['acl_mngt']
setup_kwargs = {
    'name': 'acl-mngt',
    'version': '0.1.4',
    'description': 'Parse acl config as string, generate vendor specific config.',
    'long_description': None,
    'author': 'Teun Ouwehand',
    'author_email': 'teun@nextpertise.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Nextpertise/acl_mngt/',
    'package_dir': package_dir,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
