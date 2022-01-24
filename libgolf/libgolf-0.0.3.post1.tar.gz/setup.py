# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libgolf']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'libgolf',
    'version': '0.0.3.post1',
    'description': 'Common utilities for implementing golfing language builtin libraries',
    'long_description': "# libgolf\nlibgolf is a library of common utilities for writing golfing language builtins. It currently includes:\n\n- `List`, a well-featured lazy list class\n- `Character`, a thin wrapper for representing Unicode characters\n- `String`, a wrapper around a `List` of `Character`s that behaves more like Python's [built-in `str`\n  type](https://docs.python.org/3/library/stdtypes.html#str)\n- `vectorise`, a higher-order function (or decorator) for automatically mapping a function over its arguments\n\nlibgolf aims to semi-standardise these features across golfing languages by allowing them to be shared, and provide high-quality code with unit tests\nto ensure robustness of their implementations.\n",
    'author': 'pxeger',
    'author_email': '_@pxeger.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pxeger/libgolf',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
