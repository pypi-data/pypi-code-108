# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tinkoff', 'tinkoff.invest', 'tinkoff.invest.grpc']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.39.0,<2.0.0', 'protobuf>=3.19.3,<4.0.0', 'tinkoff>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'tinkoff-investments',
    'version': '0.2.0b6',
    'description': '',
    'long_description': '# Tinkoff Invest\n\n[![PyPI](https://img.shields.io/pypi/v/tinkoff-investments)](https://pypi.org/project/tinkoff-investments/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tinkoff-investments)](https://www.python.org/downloads/)\n\n## Начало работы\n\n```\npip install tinkoff-investments\n```\n\n## Примеры\n\nПримеры доступны [здесь](https://github.com/Tinkoff/invest-python/tree/main/examples).\n\n## Contribution\n\n- [CONTRIBUTING](https://github.com/Tinkoff/invest-python/blob/main/CONTRIBUTING.md)\n\n## License\n\nЛицензия [The Apache License](https://github.com/Tinkoff/invest-python/blob/main/LICENSE).\n',
    'author': 'Danil Akhtarov',
    'author_email': 'd.akhtarov@tinkoff.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Tinkoff/invest-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
