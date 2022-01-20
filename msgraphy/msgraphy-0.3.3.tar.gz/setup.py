# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['msgraphy',
 'msgraphy.auth',
 'msgraphy.client',
 'msgraphy.data',
 'msgraphy.domains',
 'msgraphy.fs',
 'msgraphy.sharepoint_classic']

package_data = \
{'': ['*']}

install_requires = \
['msal>=1.10.0,<2.0.0', 'pyhumps>=3.0.2,<4.0.0', 'requests>=2.25.1,<3.0.0']

extras_require = \
{'fs': ['fs.onedrivefs>=1.1.1,<2.0.0']}

entry_points = \
{'fs.opener': ['o365 = msgraphy.fs.opener:MSGraphyOneDriveFSOpener']}

setup_kwargs = {
    'name': 'msgraphy',
    'version': '0.3.3',
    'description': 'An API generator for the MS Graph API',
    'long_description': None,
    'author': 'Kaj Siebert',
    'author_email': 'kaj@k-si.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
