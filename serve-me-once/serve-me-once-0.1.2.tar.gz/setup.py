# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['serve_me_once']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'serve-me-once',
    'version': '0.1.2',
    'description': '',
    'long_description': '# [serve-me-once](https://pypi.org/project/fix-my-functions/)\n\nServes some data over HTTP, _once_.\nBased on the built-in Python module `http.server`.\n\n\n## Installation\n\n\tpip install serve-me-once\n\n## Use\n\n```python\nfrom serve_me_once import serve_once, gen_random_port\nserve_once(\n\t"Hello, World",\n\ttimeout=2,\n\tmime_type="text/html",\n\tport=gen_random_port()\n)\n```\n\nor\n\n```python\nfrom serve_me_once import serve_once_in_background, gen_random_port\nimport time\n\naddr = serve_once_in_background(\n\t"Hello, World",\n\ttimeout=2,\n\tmime_type="text/html",\n\tport=gen_random_port()\n)\nprint("Hosting at:", addr)\ntime.sleep(3)\n```\n\n\n# ... Why?\n\nThe web version of [Netron](https://github.com/lutzroeder/netron) accepts an URL as a query parameter ([example](https://netron.app/?url=https://media.githubusercontent.com/media/onnx/models/master/vision/classification/squeezenet/model/squeezenet1.0-3.onnx)).\nBut serving temporary files is a chore.\nHence this.\n',
    'author': 'Peder Bergebakken Sundt',
    'author_email': 'pbsds@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pbsds/serve-me-once/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
