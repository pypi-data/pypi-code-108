# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.ldap',
 'aleksis.apps.ldap.management.commands',
 'aleksis.apps.ldap.migrations',
 'aleksis.apps.ldap.util']

package_data = \
{'': ['*'],
 'aleksis.apps.ldap': ['locale/*',
                       'locale/ar/LC_MESSAGES/*',
                       'locale/de_DE/LC_MESSAGES/*',
                       'locale/fr/LC_MESSAGES/*',
                       'locale/la/LC_MESSAGES/*',
                       'locale/nb_NO/LC_MESSAGES/*',
                       'locale/tr_TR/LC_MESSAGES/*',
                       'static/*']}

install_requires = \
['aleksis-core[ldap]>=2.0,<3.0',
 'django-ldapdb>=1.4.0,<2.0.0',
 'python-magic>=0.4.22,<0.5.0',
 'tqdm>=4.44.1,<5.0.0']

entry_points = \
{'aleksis.app': ['ldap = aleksis.apps.ldap.apps:LDAPConfig']}

setup_kwargs = {
    'name': 'aleksis-app-ldap',
    'version': '2.1',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp LDAP (General LDAP import/export)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp LDAP (General LDAP import/export)\n==================================================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\n* Configurable sync strategies\n* Management commands for ldap import\n* Mass import of users and groups\n* Sync LDAP users and groups on login\n\nLicence\n-------\n\n::\n\n  Copyright © 2020, 2021, 2022 Dominik George <dominik.george@teckids.org>\n  Copyright © 2020 Tom Teichler <tom.teichler@teckids.org>\n\n  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://aleksis.org/\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Tom Teichler',
    'author_email': 'tom.teichler@teckids.org',
    'maintainer': 'Jonathan Weth',
    'maintainer_email': 'wethjo@katharineum.de',
    'url': 'https://aleksis.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
