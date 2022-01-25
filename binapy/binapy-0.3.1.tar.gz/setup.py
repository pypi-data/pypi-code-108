# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['binapy',
 'binapy.compression',
 'binapy.encoding',
 'binapy.hashing',
 'binapy.parsing',
 'tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'binapy',
    'version': '0.3.1',
    'description': 'Binary Data manipulation, for humans.',
    'long_description': '# BinaPy\n\n[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)\n[![Downloads](https://pepy.tech/badge/binapy/month)](https://pepy.tech/project/binapy)\n[![Supported Versions](https://img.shields.io/pypi/pyversions/binapy.svg)](https://pypi.org/project/binapy)\n[![PyPi license](https://badgen.net/pypi/license/binapy/)](https://pypi.com/project/binapy/)\n[![PyPI status](https://img.shields.io/pypi/status/binapy.svg)](https://pypi.python.org/pypi/binapy/)\n[![GitHub commits](https://badgen.net/github/commits/guillp/binapy)](https://github.com/guillp/binapy/commit/)\n[![GitHub latest commit](https://badgen.net/github/last-commit/guillp/binapy)](https://github.com/guillp/binapy/commit/)\n\n**BinaPy** is a module that makes Binary Data manipulation simpler and easier than what is offered in the Python standard library.\n\nWith BinaPy, encoding or decoding data in a number of formats (base64, base64url, hex, url-encoding, etc.), compressing or decompressing (gzip), hashing (SHA1, SHA256, MD5, etc., with or without salt), is all a single method call away! And you can extend it with new formats and features.\n\n```python\nfrom binapy import BinaPy\n\nbp = BinaPy("Hello, World!").compress_gzip().encode_b64u()\nprint(bp)\n# b\'eJzzSM3JyddRCM8vyklRBAAfngRq\'\nbp.decode_b64u().decompress_gzip().decode()\n# "Hello, World!"\nisinstance(bp, bytes)\n# True\n```\n\n* Free software: MIT\n* Documentation: <https://guillp.github.io/binapy/>\n\n## Features\n\n- Fluent interface, based on a `bytes` subclass\n- Provides a convenient interface over `hashlib`, `base64`, `gzip`, `urllib.parse`, `json` and more\n- Easy to extend with new formats\n\n## TODO\n\n- add more parsing formats like YAML, CBOR, etc.\n- optionally use faster third-party modules when available\n\n## Credits\n\nThis package template was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.\n',
    'author': 'Guillaume Pujol',
    'author_email': 'guill.p.linux@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/guillp/binapy',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
