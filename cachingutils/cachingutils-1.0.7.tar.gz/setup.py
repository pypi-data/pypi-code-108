# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cachingutils']

package_data = \
{'': ['*']}

install_requires = \
['lru-dict>=1.1.7,<2.0.0']

setup_kwargs = {
    'name': 'cachingutils',
    'version': '1.0.7',
    'description': 'Utilities to make caching data easier',
    'long_description': '# cachingutils\n\nUtilities to make caching data easier\n\n## Examples\n\nBasic caching:\n\n```py\nfrom cachingutils import cached\n\n\n@cached()\ndef fib(n: int) -> int:\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n\nprint(fib(100))  # 354224848179261915075\n```\n\nCaching with your own cache object:\n\n```py\nfrom cachingutils import Cache, cached\n\n\nmy_cache = Cache()\n\n@cached(cache=my_cache)\ndef fib(n: int) -> int:\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n\nprint(fib(100))  # 354224848179261915075\n```\n\nCaching with an LRU cache:\n\n```py\nfrom cachingutils import LRUCache, cached\n\n\n@cached(cache=LRUCache(2, timeout=60), include_posargs=[0])\ndef fetch_thing(thing_id: int, thing_name: str) -> tuple[int, str]:\n    return thing_id, thing_name  # Imagine this is a call to an API\n\nprint(fetch_thing(123, "456"))  # (123, "456")\nprint(fetch_thing(123, "789"))  # (123, "456")\n\nfetch_thing(567, "789")\nfetch_thing(789, "456")\n\nprint(fetch_thing(123, "456"))  # Cache miss\n```\n\nAsync caching:\n\n```py\nfrom asyncio import run\n\nfrom cachingutils import acached\n\n\n@acached()\nasync def fib(n: int) -> int:\n    if n < 2:\n        return n\n    return await fib(n - 1) + await fib(n - 2)\n\nprint(run(fib(100)))  # 354224848179261915075\n```\n\nCaching specific positional args:\n\n```py\nfrom cachingutils import cached\n\n\n@cached(include_posargs=[0])\nasync def add(a: int, b: int) -> int:\n    return a + b\n\nprint(add(1, 2))  # 3\nprint(add(2, 2))  # 3\nprint(add(2, 3))  # 5\n```\n\nCaching specific keyword args:\n\n```py\nfrom cachingutils import cached\n\n\n@cached(include_posargs=[0], include_kwargs=[\'c\'])\ndef add(a: int, b: int, *, c: int) -> int:\n    return a + b\n\nprint(add(1, 2, c=3))  # 3\nprint(add(2, 2, c=3))  # 4\nprint(add(2, 3, c=3))  # 4\n```\n\nCaching with a timeout:\n\n```py\nfrom time import sleep\n\nfrom cachingutils import cached\n\n\n@cached(timeout=1, include_posargs=[0])\ndef add(a: int, b: int) -> int:\n    return a + b\n\nprint(add(1, 2))  # 3\nprint(add(1, 3))  # 3\nsleep(2)\nprint(add(1, 3))  # 4\n```\n\nUsing a raw `Cache` object:\n\n```py\nfrom time import sleep\n\nfrom cachingutils import Cache\n\n\nmy_cache: Cache[str, int] = Cache(timeout=5)\n\nmy_cache["abc"] = 123\n\nprint(my_cache["abc"])  # 123\n\nsleep(6)\n\nprint(my_cache["abc"])  # KeyError: \'abc\'\n```\n\n---\n\nAll of the above decorators also work within classes:\n\n```py\nfrom cachingutils import cached\n\n\nclass MyClass:\n    @cached()\n    def fib(self, n: int) -> int:\n        if n < 2:\n            return n\n        return self.fib(n - 1) + self.fib(n - 2)\n\n\nmy_class = MyClass()\n\nprint(my_class.fib(100))  # 354224848179261915075\n```\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vcokltfre/cachingutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
