# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oshino', 'oshino.agents', 'oshino.augments', 'oshino.core']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'aiohttp>=3.8.1,<4.0.0',
 'oshino-admin>=0.2.0,<0.3.0',
 'protobuf==3.1.0.post1',
 'pytest-asyncio>=0.17.2,<0.18.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'raven>=6.10.0,<7.0.0',
 'requests>=2.27.1,<3.0.0',
 'riemann-client==6.3.0']

setup_kwargs = {
    'name': 'oshino',
    'version': '0.4.0',
    'description': '',
    'long_description': "About\n=====\nOshino - named after character Meme Oshino from anime called Bakemonogatari:\n> Meme Oshino (忍野 メメ, Oshino Meme) is a middle-aged man who lives with the mysterious Shinobu Oshino in an abandoned cram school building in the town Koyomi Araragi resides in Bakemonogatari. An expert in the supernatural, he is the reason why Koyomi was able to return back to normal after being bitten by a vampire, and he becomes Koyomi's informant when it comes to oddities for some time.\n[Source](https://myanimelist.net/character/22552/Meme_Oshino)\n\nJust like anime character, this service likes to deal with supernatural - system availability.\n\nHeavily inspired by [collectd](https://github.com/collectd/collectd) and\n[riemann-tools](https://github.com/riemann/riemann-tools), and unintentionally similar to [python-diamond](https://github.com/python-diamond/Diamond)\n\nAlerting and Monitoring based on [Riemann](https://riemann.io)\n\n\n[![Build Status](https://travis-ci.org/CodersOfTheNight/oshino.svg?branch=master)](https://travis-ci.org/CodersOfTheNight/oshino)\n[![Coverage Status](https://coveralls.io/repos/github/CodersOfTheNight/oshino/badge.svg?branch=master)](https://coveralls.io/github/CodersOfTheNight/oshino?branch=master)\n[![Documentation Status](https://readthedocs.org/projects/oshino/badge/?version=latest)](http://oshino.readthedocs.io/projects/https://github.com/CodersOfTheNight/oshino-consul/en/latest/?badge=latest)\n\n\nRequirements\n============\n- Python 3.5+ version\n- Have Riemann node running\n\nHow to install\n==============\n`pip install oshino`\n\nQuickstart\n==========\nIt is highly recommended for new users to use [Quickstart Guide](docs/quickstart.md)\n\n\nRiemann. What? Why? How?\n=========================\nRiemann is a backbone of this system. It does alerting, it receives metrics, it aggregates metrics and it decides where to send them (eg.: Graphite, Logstash).\nHowever, it is rather unknown to the most of people, and configuring can be not trivial at all. \n\nTo mitigate this problem, documentation for setuping Riemann for this scenario has been made:\n[riemann](docs/riemann.md)\n\nExample config\n--------------\n```yaml\n---\ninterval: 10\nriemann:\n  host: localhost\n  port: 5555\nagents:\n  - name: health-check\n    module: oshino.agents.http_agent.HttpAgent\n    url: http://python.org\n    tag: healthcheck\n```\n\nCustom Agents\n===============\nDocumentation about additional agents can be found [here](docs/thirdparty.md)\n\nMore documentation\n==================\nMore documentation can be found under [docs](docs/index.md) directory\n\nContributing\n============\nRefer to [CONTRIBUTING.md](CONTRIBUTING.md)\n",
    'author': 'Šarūnas Navickas',
    'author_email': 'zaibacu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CodersOfTheNight/oshino',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
