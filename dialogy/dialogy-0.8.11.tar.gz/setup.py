# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dialogy',
 'dialogy.base',
 'dialogy.cli',
 'dialogy.constants',
 'dialogy.plugins',
 'dialogy.plugins.text',
 'dialogy.plugins.text.calibration',
 'dialogy.plugins.text.canonicalization',
 'dialogy.plugins.text.classification',
 'dialogy.plugins.text.combine_date_time',
 'dialogy.plugins.text.duckling_plugin',
 'dialogy.plugins.text.lb_plugin',
 'dialogy.plugins.text.list_entity_plugin',
 'dialogy.plugins.text.list_search_plugin',
 'dialogy.plugins.text.merge_asr_output',
 'dialogy.plugins.text.slot_filler',
 'dialogy.plugins.text.voting',
 'dialogy.types',
 'dialogy.types.entity',
 'dialogy.types.intent',
 'dialogy.types.plugin',
 'dialogy.types.signal',
 'dialogy.types.slots',
 'dialogy.types.utterances',
 'dialogy.utils',
 'dialogy.workflow']

package_data = \
{'': ['*']}

install_requires = \
['attr>=0.3.1,<0.4.0',
 'attrs>=20.3.0,<21.0.0',
 'copier>=5.1.0,<6.0.0',
 'jiwer>=2.2.0,<3.0.0',
 'loguru>=0.5.3,<0.6.0',
 'numpy>=1.20.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'pydash>=4.9.3,<5.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'pytz>=2020.4,<2021.0',
 'requests>=2.25.1,<3.0.0',
 'scipy>=1.7.1,<2.0.0',
 'sklearn>=0.0,<0.1',
 'stanza>=1.3.0,<2.0.0',
 'thefuzz>=0.19.0,<0.20.0',
 'tqdm>=4.62.2,<5.0.0',
 'watchdog>=1.0.2,<2.0.0',
 'xgboost>=1.4.2,<2.0.0']

entry_points = \
{'console_scripts': ['dialogy = dialogy.cli:main']}

setup_kwargs = {
    'name': 'dialogy',
    'version': '0.8.11',
    'description': 'Language understanding for human dialog.',
    'long_description': None,
    'author': 'Amresh Venugopal',
    'author_email': 'amresh.venugopal@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
