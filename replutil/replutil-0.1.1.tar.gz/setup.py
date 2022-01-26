# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['replutil']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0', 'click>=8.0.3,<9.0.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'replutil',
    'version': '0.1.1',
    'description': 'A collection of utilities for running services on repl.it',
    'long_description': '# replutil\n\nA collection of utilities for running services on [repl.it](https://replit.com).\n\nIncludes utilities for getting attributes of the container, as well as keeping the container alive using [the UptimeRobot API](https://uptimerobot.com/).\n\n### KeepAlive Example\n\nYou can obtain a token on the [the UptimeRobot dashboard](https://uptimerobot.com/dashboard).\n\n```py\nfrom replutil import *\nfrom time import sleep\nimport logging\n\nlogging.basicConfig(level=logging.INFO)\n\nwith ReplKeepAlive("token"):\n    # Do your long running operations here...\n    sleep(40)\n```\n\nRegistering servers, ports, and watchers are abstracted away from the end user.\n\nWhen used as a context manager, the library will automatically handle registering and deregistering watchers as well as staring and keeping open webservers.\n\nYes, all you need to have your repl container run forever is a single line and an indent. No hacker plan, freedom!\n\nIf this is used in a larger project, like, say, a Discord bot, you should do any `asyncio` event loop logic (including `Client.run`) in the context manager scoping block as it creates processes.\n\n### Install\n\nYou can install this package via pip:\n\n```\npip install replutil\n```\n',
    'author': 'regulad',
    'author_email': 'regulad@regulad.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/regulad/replutil',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
