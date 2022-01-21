# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wmill']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.1.0,<22.0.0', 'windmill-api-client>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'wmill',
    'version': '0.9.0',
    'description': 'A client library for accessing Windmill server wrapping the Windmill client API',
    'long_description': '# wmill\n\nThe client for the [Windmill](https://windmill.dev) platform\n\n## Quickstart\n\n```python\nimport wmill\n\n# with a WM_TOKEN env variable\nclient = wmill.Client()\n\n# without a WM_TOKEN env variable\nclient = wmill.Client(token="<mytoken>")\n\ndef main():\n\n    version = client.get_version()\n    resource = client.get_resource("u/user/resource_path")\n\n    # run synchronously, will return the result\n    res = client.run_script_sync(hash="000000000000002a", args={})\n    print(res)\n\n    for _ in range(3):\n        # run asynchrnously, will return immediately. Can be scheduled\n        client.run_script_async(hash="000000000000002a", args={}, scheduled_in_secs=10)\n```\n',
    'author': 'Ruben Fiszel',
    'author_email': 'ruben@rubenfiszel.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
