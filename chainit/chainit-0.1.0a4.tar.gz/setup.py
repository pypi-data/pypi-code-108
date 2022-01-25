# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chainit']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'chainit',
    'version': '0.1.0a4',
    'description': 'Chainable lazy iterators',
    'long_description': "# chainit\n\nDocumentation available here: https://lukapeschke.github.io/chainit/\n\nThis library provides the `ChainIt` class, a wrapper around stdlib's\n[itertools](https://docs.python.org/3/library/itertools.html) module, allowing to chain\noperations on iterables, resulting in easier-to-read code.\n\n```python\nimport typing as t\n\ndef fib() -> t.Iterable[int]:\n    a, b = 0, 1\n    while True:\n        yield a\n        next_ = a + b\n        a = b\n        b = next_\n\n# Allows to write things like this...\n(\n    ChainIt(fib())\n    .filter(lambda x: x % 2 == 0)\n    .map(lambda x: x // 2)\n    .flat_map(range)\n    .take_while(lambda x: x < 6)\n    .collect_list()\n)\n\n# ...rather than like this\nfrom itertools import chain as ichain, islice, takewhile\n\nlist(\n    takewhile(\n        lambda x: x < 6,\n        ichain.from_iterable(\n            map(lambda x: range(x // 2), filter(lambda x: x % 2 == 0, fib()))\n        ),\n    )\n)\n```\n\n## Installation\n\n```\npip install chainit\n```\n\n## Examples\n\n### Decorator\n\nIn addition to `ChainIt`, the library provides a `chainit` decorator. It makes a function returning\nan iterable return a `ChainIt` instead:\n\n```python\n@chainit\ndef fac():\n    n = 0\n    fac = 1\n    while True:\n        yield fac\n        n += 1\n        fac *= n\n\nassert fac().enumerate().take(5).collect() == ((0, 1), (1, 1), (2, 2), (3, 6), (4, 24))\n```\n\n### Using a `ChainIt` instance as an iterable\n\n```python\nassert list(fac().take(3)) == [1, 1, 2]\n\nfor idx, x in fac().enumerate():\n    if idx > 3:\n        break\n    print(x)\n```\n",
    'author': 'Luka Peschke',
    'author_email': 'mail@lukapeschke.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lukapeschke/chainit',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
