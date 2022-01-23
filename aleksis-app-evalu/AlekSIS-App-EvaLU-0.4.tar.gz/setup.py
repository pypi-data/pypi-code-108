# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.evalu',
 'aleksis.apps.evalu.migrations',
 'aleksis.apps.evalu.tests.models',
 'aleksis.apps.evalu.util']

package_data = \
{'': ['*'],
 'aleksis.apps.evalu': ['locale/*',
                        'locale/ar/LC_MESSAGES/*',
                        'locale/de_DE/LC_MESSAGES/*',
                        'locale/fr/LC_MESSAGES/*',
                        'locale/la/LC_MESSAGES/*',
                        'locale/nb_NO/LC_MESSAGES/*',
                        'locale/tr_TR/LC_MESSAGES/*',
                        'static/*',
                        'static/css/*',
                        'static/js/evalu/*',
                        'templates/evalu/*',
                        'templates/evalu/part/*',
                        'templates/evalu/participate/*',
                        'templates/evalu/phase/*',
                        'templates/evalu/registration/*',
                        'templates/material/fields/*']}

install_requires = \
['aleksis-app-chronos>=2.0,<3.0',
 'aleksis-core>=2.0,<3.0',
 'cryptography>=35.0.0,<36.0.0',
 'django-formtools>=2.3,<3.0']

entry_points = \
{'aleksis.app': ['evalu = aleksis.apps.evalu.apps:DefaultConfig']}

setup_kwargs = {
    'name': 'aleksis-app-evalu',
    'version': '0.4',
    'description': '\u200aInofficial AlekSIS App EvaLU (Evaluation of teaching and lesson quality)',
    'long_description': '\u200aInofficial AlekSIS App EvaLU (Evaluation of teaching and lesson quality)\n=========================================================================\n\nAlekSIS\n-------\n\nThis is an inofficial application for use with the `AlekSIS`_ platform.\n\nFeatures\n--------\n\nThis app can be used to evaluate teaching and lesson quality of teachers.\n\nLicence\n-------\n\n::\n\n  Copyright © 2021 Jonathan Weth <dev@jonathanweth.de>\n\n  Licenced under the EUPL, version 1.2 or later\n\nCreate graph of models\n----------------------\n\n::\n\n  poetry run pip install pygraphviz\n  poetry run aleksis-admin graph_models evalu -X Site,ExtensibleModel -x site,extended_data -o\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\n.. _AlekSIS: https://edugit.org/AlekSIS/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n',
    'author': 'Jonathan Weth',
    'author_email': 'dev@jonathanweth.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://katharienum.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
