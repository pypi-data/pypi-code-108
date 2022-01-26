# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypypan']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.4.0,<2.0.0',
 'pywikibot>=6.6.3,<7.0.0',
 'requests-oauthlib>=1.3.0,<2.0.0',
 'wikitextparser>=0.48.0,<0.49.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'pypypan',
    'version': '0.2.2',
    'description': '',
    'long_description': None,
    'author': 'Ate te Voortwis',
    'author_email': 'atv@allseas.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
