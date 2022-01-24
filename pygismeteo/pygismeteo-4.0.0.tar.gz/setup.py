# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pygismeteo']

package_data = \
{'': ['*']}

install_requires = \
['pygismeteo-base>=2.1.0,<3.0.0', 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'pygismeteo',
    'version': '4.0.0',
    'description': 'Wrapper for Gismeteo.ru API',
    'long_description': '# pygismeteo\n\n[![Build Status](https://github.com/monosans/pygismeteo/workflows/test/badge.svg?branch=main&event=push)](https://github.com/monosans/pygismeteo/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/monosans/pygismeteo/branch/main/graph/badge.svg)](https://codecov.io/gh/monosans/pygismeteo)\n[![Python Version](https://img.shields.io/pypi/pyversions/pygismeteo.svg)](https://pypi.org/project/pygismeteo/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/monosans/pygismeteo/blob/main/LICENSE)\n\nОбёртка для [Gismeteo.ru API](https://gismeteo.ru/api).\n\nАсинхронная версия [здесь](https://github.com/monosans/aiopygismeteo).\n\n## Установка\n\n```bash\npython -m pip install -U pygismeteo\n```\n\n## Документация\n\nРелизная версия - <https://pygismeteo.readthedocs.io>\n\nGit версия - <https://pygismeteo.readthedocs.io/ru/latest>\n\n## Пример, выводящий температуру в Москве сейчас\n\n```python\nfrom pygismeteo import Gismeteo\n\ngm = Gismeteo()\ncity_id = gm.get_id_by_query("Москва")\ncurrent = gm.current(city_id)\nprint(current.temperature.air.c)\n```\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/pygismeteo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
