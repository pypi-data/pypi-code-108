# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['herre',
 'herre.access',
 'herre.access.model',
 'herre.console',
 'herre.grants',
 'herre.grants.backend',
 'herre.grants.code_server',
 'herre.wards',
 'herre.wards.transports']

package_data = \
{'': ['*']}

install_requires = \
['QtPy>=1.11.1,<2.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'fakts==0.1.40',
 'oauthlib>=3.1.1,<4.0.0',
 'rich>=10.9.0,<11.0.0']

setup_kwargs = {
    'name': 'herre',
    'version': '0.1.60',
    'description': 'The governing package for modules of the arnheim framework, it provides core features like wards, the event loop and authentication with an oauth provider',
    'long_description': '# Herre\n\n### Idea\n\nHerre is the core library to provide the groundwork for every module of the arkitekt framework,\n\n\n \n### Prerequisites\n\nHerre only works with a running Oauth Instance (in your network or locally for debugging).\n\n### Usage\n\nIn order to initialize the Client you need to connect it as a Valid Application with your Arnheim Instance\n\n```python\nclient = Bergen(host="p-tnagerl-lab1",\n    port=8000,\n  client_id="APPLICATION_ID_FROM_ARNHEIM", \n  client_secret="APPLICATION_SECRET_FROM_ARNHEIM",\n  name="karl",\n)\n```\n\nIn your following code you can simple query your data according to the Schema of the Datapoint\n\n```python\nfrom bergen.schema import Node\n\nnode = Node.objects.get(id=1)\nprint(node.name)\n\n```\n\n## Access Data from different Datapoints\n\nThe Arnheim Framework is able to provide data from different Data Endpoints through a commong GraphQL Interface\n. This allows you to access data from various different storage formats like Elements and Omero and interact without\nknowledge of their underlying api.\n\nEach Datapoint provides a typesafe schema. Arnheim Elements provides you with an implemtation of that schema.\n\n## Provide a Template for a Node\n\nDocumentation neccesary\n\n\n### Testing and Documentation\n\nSo far Bergen does only provide limitedunit-tests and is in desperate need of documentation,\nplease beware that you are using an Alpha-Version\n\n\n### Build with\n\n- [Arnheim](https://github.com/jhnnsrs/arnheim)\n- [Pydantic](https://github.com/jhnnsrs/arnheim)\n\n',
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
