# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flypper_redis', 'flypper_redis.storage']

package_data = \
{'': ['*']}

modules = \
['README', 'LICENSE']
install_requires = \
['flypper>=0.1.0,<0.2.0', 'redis>=3.5.3,<4.0.0']

setup_kwargs = {
    'name': 'flypper-redis',
    'version': '0.1.2',
    'description': 'Feature flags, with a GUI - Redis backend',
    'long_description': '# flypper-redis\n\nFlypper-redis is a storage backend for the [flypper](https://github.com/nicoolas25/flypper) package.\n\nIt is backed by Redis so it an be used in a distributed environment and be persisted across restarts.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install `flypper-redis`.\n\n```bash\npip install flypper-redis\n```\n\n## Usage\n\nBuild a storage backend:\n\n```python\nfrom redis import Redis\nfrom flypper_redis.storage.redis import RedisStorage\n\nredis = Redis(host="localhost", port=6379, db=0)\nstorage = RedisStorage(redis=redis, prefix="flypper-demo")\n```\n\nUse it in the web UI:\n\n```python\nfrom flypper.wsgi.web_ui import FlypperWebUI\n\nweb_ui = FlypperWebUI(storage=storage)\n```\n\nUse it in your code:\n1. Build a client for your app\n2. Use a context\n\n```python\nfrom flypper.client import Client as FlypperClient\n\n# Once per thread\nflypper_client = FlypperClient(storage=storage, ttl=10)\n\n# Once per request\nflypper_context = FlypperContext(\n    client=flypper_client,\n    entries={"user_id": "42"},\n)\n\n# Every time you need\nflypper_context.is_enabled("flag_name")\nflypper_context.is_enabled(\n    "other_flag_name",\n    entries={"item_reference": "blue-shampoo"},\n)\n```\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'Nicolas Zermati',
    'author_email': 'nicoolas25@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nicoolas25/flypper-redis',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
