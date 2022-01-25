# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['throttled',
 'throttled.fastapi',
 'throttled.fastapi.limiters',
 'throttled.storage',
 'throttled.strategy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'throttled',
    'version': '0.1.16a15',
    'description': 'A rate limiter for FastAPI',
    'long_description': '# ThrottledAPI\n\nThis repo aims to be an audacious RateLimiter for python ASGI/WSGI APIs.\n\n## RoadMap\n\n- [ ] Implement for FastAPI, because I really like the framework\n- [ ] Generalise for others\n\n## Status\n\nIn development ...\n',
    'author': 'Vinícius Vargas',
    'author_email': 'santunionivinicius@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/santunioni/ThrottledAPI',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
