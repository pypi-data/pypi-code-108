# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trovoApi']

package_data = \
{'': ['*']}

install_requires = \
['requests==2.26.0']

setup_kwargs = {
    'name': 'python-trovo',
    'version': '0.1.3',
    'description': 'A Python wrapper for the Trovo API',
    'long_description': '# python-trovo\n\nThis is a Python wrapper for some of the [Trovo API](https://developer.trovo.live/docs/APIs.html) functions, specifically:\n\n- Main API\n  - 5.1. Get Game Categories (`get_all_game_categories`)\n  - 5.2. Search Categories (`get_game_categories`)\n  - 5.3. Get top channels (`get_top_channels`)\n  - 5.4. Get Users (get channel id) (`get_users`)\n  - 5.5. Get Channel Info by ID (`get_channel_info_by_id`)\n  - 5.10. Get Emotes (`get_emotes`)\n  - 5.11. Get channel viewers (`get_channel_viewers`)\n  - 5.12. Get channel followers (`get_channel_followers`)\n  - 5.13 Get Live Stream Urls (`get_livestream_urls`)\n  - 5.14 Get Clips Info (`get_clips_info`)\n  - 5.15 Get Past Streams Info (`get_past_streams_info`)\n\nTo obtain a connection, just run the following command:\n```python\nimport trovoApi\n\nc = trovoApi.TrovoClient("client_id")\nprint(c.get_all_game_categories())\n```',
    'author': 'P. R. d. O.',
    'author_email': 'liquid.query960@4wrd.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://codeberg.org/wolfangaukang/python-trovo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
