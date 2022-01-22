# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['timelooper']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'timelooper',
    'version': '0.1.1',
    'description': 'Timed loops made simple',
    'long_description': "## Timelooper\n\n[![Build Status](https://app.travis-ci.com/monomonedula/timelooper.svg?branch=master)](https://app.travis-ci.com/monomonedula/timelooper)\n\nI found myself re-implementing the same \npattern over and over \nwhen it comes to repeating some task until \nsome condition is met OR \nthe time is up, so here it is abstracted and generalized into\na neat package. \n\nYep, that's 25 lines of code + tests.\n\n\nHere's a demo use case:\n```python\nfrom timelooper import Looped, loop_timed\nfrom datetime import timedelta\n\n# Suppose we are listening to some queue\n#   and want to batch the incoming messages.\n#   However, we only want to wait for\n#   some limited time for a batch \n#   to be formed.\n\n\nclass CollectableBatch(Looped):\n    def __init__(self, queue, maxsize):\n        self.batch = []\n        self._queue = queue\n        self._maxsize = maxsize\n    \n    async def do(self) -> None:\n        self.batch.append(await self._queue.get())\n\n    def should_stop(self) -> bool:\n        return len(self.batch) == self._maxsize\n\n    \ncollected = CollectableBatch(queue, maxsize=10)\nawait loop_timed(collected, timedelta(seconds=30))  \n\nprint(collected.batch)  # or whatever\n\n```\n\n\n### Installation\n```shell\npip install timelooper\n```",
    'author': 'monomonedula',
    'author_email': 'valh@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monomonedula/timelooper',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
