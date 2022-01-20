# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aio_rom']

package_data = \
{'': ['*']}

install_requires = \
['aioredis==2.0.1', 'typing-extensions>=4.0.1,<5.0']

extras_require = \
{'mypy:platform_python_implementation == "CPython"': ['mypy>=0.920,<0.931']}

setup_kwargs = {
    'name': 'aio-rom',
    'version': '0.1.2',
    'description': 'asyncio based Redis object mapper',
    'long_description': 'Python Redis Object Mapper\n======================\n\nasyncio based Redis object mapper\n\n## Table of content\n\n- [Installation](#installation)\n- [Usage](#usage)\n- [Features](#usage)\n- [TODO](#todo)\n- [Limitations](#limitations)\n\n## Installation\n\nTODO\n\n## Usage\n\n```python\nimport asyncio\n\nfrom dataclasses import field\nfrom typing import Set, Dict\n\nfrom aio_rom import Model\nfrom aio_rom.fields import Metadata\nfrom aio_rom.session import redis_pool\n\n\nclass Foo(Model):\n    bar: int\n    foobar: Set[int] = field(default_factory=set)\n    my_boolean: bool = False\n    transient_field: Dict = field(metadata=Metadata(transient=True))\n\n\nclass OtherFoo(Model):\n    foo: Foo\n\nasync def main():\n    async with redis_pool("redis://localhost"):\n        foo = Foo(123, {1,2,3}, True)\n        await foo.save()\n        ...\n        foo2 = await Foo.get(321)\n        other_foo = OtherFoo(303, foo2)\n        await other_foo.save()\n\nasyncio.run(main())\n```\n## Features\nTODO\n\n## TODO\n1. Docs\n1. Tests\n\n## Limitations\n1. `configure` must be called before other calls to Redis can succeed, no defaults to localhost atm.\n1. You cannot use `from __future__ import annotations` in the same file you define your models. See https://bugs.python.org/issue39442\n1. TODO Supported datatypes\n1. Probably more ...\n',
    'author': 'Federico Jaite',
    'author_email': 'fede_654_87@hotmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/fedej/aio-rom',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
