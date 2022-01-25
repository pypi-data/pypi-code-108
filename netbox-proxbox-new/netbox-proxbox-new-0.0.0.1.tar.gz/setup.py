# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netbox_proxbox_new',
 'netbox_proxbox_new.api',
 'netbox_proxbox_new.migrations',
 'netbox_proxbox_new.proxbox_api']

package_data = \
{'': ['*'], 'netbox_proxbox_new': ['templates/netbox_proxbox/*']}

setup_kwargs = {
    'name': 'netbox-proxbox-new',
    'version': '0.0.0.1',
    'description': 'Netbox Plugin - Integrate Proxmox and Netbox',
    'long_description': None,
    'author': 'Sebastian Winkelmann',
    'author_email': 'sebastian.winkelmann@check24.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
