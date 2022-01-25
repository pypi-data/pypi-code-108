# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cypherpunkpay',
 'cypherpunkpay.bitcoin',
 'cypherpunkpay.bitcoin.electrum',
 'cypherpunkpay.bitcoin.pwuille',
 'cypherpunkpay.config',
 'cypherpunkpay.db',
 'cypherpunkpay.db.migrations',
 'cypherpunkpay.explorers',
 'cypherpunkpay.explorers.bitcoin',
 'cypherpunkpay.full_node_clients',
 'cypherpunkpay.jobs',
 'cypherpunkpay.lightning_node_clients',
 'cypherpunkpay.models',
 'cypherpunkpay.monero',
 'cypherpunkpay.net',
 'cypherpunkpay.net.http_client',
 'cypherpunkpay.net.tor_client',
 'cypherpunkpay.prices',
 'cypherpunkpay.tools',
 'cypherpunkpay.usecases',
 'cypherpunkpay.web',
 'cypherpunkpay.web.security',
 'cypherpunkpay.web.views',
 'cypherpunkpay.web.views_admin',
 'cypherpunkpay.web.views_donations',
 'cypherpunkpay.web.views_dummystore',
 'cypherpunkpay.web.views_prefix']

package_data = \
{'': ['*'],
 'cypherpunkpay.web': ['css/*',
                       'html/admin/*',
                       'html/admin/partials/*',
                       'html/charge/theme_entertainment/*',
                       'html/charge/theme_entertainment/partials/*',
                       'html/charge/theme_plain/*',
                       'html/charge/theme_plain/partials/*',
                       'html/donations/theme_entertainment/*',
                       'html/donations/theme_plain/*',
                       'html/dummystore/*',
                       'js/*',
                       'png/*']}

install_requires = \
['APScheduler>=3.7.0,<4.0.0',
 'PyQRCode>=1.2.1,<2.0.0',
 'PySocks>=1.7.1,<2.0.0',
 'bitstring>=3.1.9,<4.0.0',
 'cffi==1.15.0',
 'ecdsa>=0.17.0,<0.18.0',
 'monero>=0.99,<0.100',
 'pypng>=0.0.20,<0.0.21',
 'pyramid-jinja2>=2.8,<3.0',
 'pyramid>=2.0,<3.0',
 'requests>=2.26,<3.0',
 'tzlocal==2.1',
 'waitress>=2.0.0,<3.0.0',
 'yoyo-migrations>=7.3.2,<8.0.0']

entry_points = \
{'console_scripts': ['cypherpunkpay = cypherpunkpay.cypherpunkpay:main',
                     'interpolate-cypherpunkpay-conf-on-first-install = '
                     'cypherpunkpay.interpolate_cypherpunkpay_conf_on_first_install:main'],
 'paste.app_factory': ['main = cypherpunkpay:main']}

setup_kwargs = {
    'name': 'cypherpunkpay',
    'version': '1.0.11',
    'description': 'Modern self-hosted software for accepting Bitcoin on clearnet and onion websites.',
    'long_description': None,
    'author': 'cypherpunkdev',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cypherpunkpay.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
