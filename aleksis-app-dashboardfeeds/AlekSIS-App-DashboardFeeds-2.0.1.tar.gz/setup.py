# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.dashboardfeeds',
 'aleksis.apps.dashboardfeeds.migrations',
 'aleksis.apps.dashboardfeeds.util']

package_data = \
{'': ['*'],
 'aleksis.apps.dashboardfeeds': ['locale/*',
                                 'locale/ar/LC_MESSAGES/*',
                                 'locale/de_DE/LC_MESSAGES/*',
                                 'locale/fr/LC_MESSAGES/*',
                                 'locale/la/LC_MESSAGES/*',
                                 'locale/nb_NO/LC_MESSAGES/*',
                                 'locale/tr_TR/LC_MESSAGES/*',
                                 'static/*',
                                 'static/dashboardfeeds/*',
                                 'static/dashboardfeeds/css/*',
                                 'templates/dashboardfeeds/*']}

install_requires = \
['aleksis-core>=2.0,<3.0',
 'django-feed-reader>=1.0.0,<2.0.0',
 'feedparser>=6.0.0,<7.0.0',
 'ics>=0.7,<0.8']

entry_points = \
{'aleksis.app': ['dashboardfeeds = '
                 'aleksis.apps.dashboardfeeds.apps:DefaultConfig']}

setup_kwargs = {
    'name': 'aleksis-app-dashboardfeeds',
    'version': '2.0.1',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Dashboard Feeds (Include feeds from external resources as widgets on dashboard)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp Dashboard Feeds (Include feeds from external resources as widgets on dashboard)\n=========================================================================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\n* Add RSS widgets to dashboard\n* Add iCal widgets to dashboard\n\nLicence\n-------\n\n::\n\n  Copyright © 2020 Dominik George <dominik.george@teckids.org>\n  Copyright © 2020 Julian Leucker <leuckerj@gmail.com>\n\n  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://aleksis.org/\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Julian Leucker',
    'author_email': 'leuckerj@gmail.com',
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
