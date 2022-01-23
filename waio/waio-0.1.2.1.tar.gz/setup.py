# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['waio',
 'waio.client',
 'waio.factory',
 'waio.factory.models',
 'waio.gupshup',
 'waio.handlers',
 'waio.keyboard',
 'waio.logs',
 'waio.middleware',
 'waio.models',
 'waio.protocols',
 'waio.rules',
 'waio.states',
 'waio.storage',
 'waio.types',
 'waio.utils',
 'waio.utils.callback']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4.post0,<4.0.0',
 'aioredis==2.0.0',
 'dataclass-factory>=2.11,<3.0',
 'loguru>=0.5.3,<0.6.0',
 'ujson==5.1.0']

setup_kwargs = {
    'name': 'waio',
    'version': '0.1.2.1',
    'description': 'waio - is a pretty simple and fully asynchronous framework for WhatsApp Business API written in Python 3.7 with asyncio and aiohttp. Used API official Facebook partner - Gupshup.io',
    'long_description': '<p align="center">\n<img alt="Codacy grade" src="https://img.shields.io/codacy/grade/36695d0fb1c648fbb8e0cb00f3612c7e">\n<img src="https://scrutinizer-ci.com/g/dotX12/waio/badges/quality-score.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/waio/">\n<img src="https://scrutinizer-ci.com/g/dotX12/waio/badges/code-intelligence.svg?b=master" alt="https://scrutinizer-ci.com/g/dotX12/waio/">\n<img src="https://img.shields.io/testspace/tests/dotX12/66672/master" alt="Testspace tests">\n<img src="https://scrutinizer-ci.com/g/dotX12/waio/badges/build.png?b=master" alt="https://scrutinizer-ci.com/g/dotX12/waio/">\n<img src="https://badge.fury.io/py/waio.svg" alt="https://badge.fury.io/py/waio">\n<img src="https://img.shields.io/github/license/dotX12/waio.svg" alt="https://github.com/dotX12/waio/blob/master/LICENSE.md">\n<img src="https://img.shields.io/github/last-commit/dotX12/waio" alt="GitHub last commit">\n<br><br>\n<img width="1000" src="docs/assets/images/readme_footer.png">\n 🤖 waio - is a pretty simple and fully asynchronous framework for WhatsApp Business API written in Python 3.7 with asyncio and aiohttp.\nUsed API official Facebook partner - <a href="https://gupshup.io">Gupshup.io</a>\n\n-----\n</p>\n\n\nYou can create an account and use a **Sandbox** to develop a bot\nand test functionality, and when you finish - create your own business\nnumber and transfer the functionality to your number,\nmake verification (check mark) and be cool!\n\n## Official waio resources:\n- Documentation: [readthedocs](https://waio.readthedocs.io/)\n- Community RU: [@waioru](https://t.me/waioru)\n- PyPI: [waio](https://pypi.python.org/pypi/waio)\n- Source: [Github repo](https://github.com/dotX12/waio)\n',
    'author': 'dotX12',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dotX12/waio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
