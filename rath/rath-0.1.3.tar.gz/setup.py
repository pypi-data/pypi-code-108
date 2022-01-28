# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rath', 'rath.links', 'rath.parsers', 'rath.turms']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'graphql-core>=3.2.0,<4.0.0',
 'koil>=0.1.59,<0.2.0',
 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'rath',
    'version': '0.1.3',
    'description': 'aiohttp powered apollo like graphql client',
    'long_description': '# rath\n\n[![codecov](https://codecov.io/gh/jhnnsrs/rath/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/rath)\n[![PyPI version](https://badge.fury.io/py/rath.svg)](https://pypi.org/project/rath/)\n[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/rath/)\n![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rath.svg)](https://pypi.python.org/pypi/rath/)\n[![PyPI status](https://img.shields.io/pypi/status/rath.svg)](https://pypi.python.org/pypi/rath/)\n[![PyPI download month](https://img.shields.io/pypi/dm/rath.svg)](https://pypi.python.org/pypi/rath/)\n\n### DEVELOPMENT\n\n## Inspiration\n\nRath is like Apollo, but for python. It adheres to the design principle of Links and enables complex GraphQL\nsetups, like seperation of query and subscription endpoints, dynamic token loading, etc..\n\n## Installation\n\n```bash\npip install rath\n```\n\n## Usage Example\n\n```python\nfrom rath.links.auth import AuthTokenLink\nfrom rath.links.aiohttp import AioHttpLink\nfrom rath.links import compose, split\nfrom rath.gql import gql\n\nasync def aload_token():\n    return "SERVER_TOKEN"\n\n\nauth = AuthTokenLink(token_loader=aload_token)\nlink = AioHttpLink(url="https://api.spacex.land/graphql/")\n\n\nrath = Rath(links=compose(auth,link))\nrath.connect()\n\n\nquery = """query TestQuery {\n  capsules {\n    id\n    missions {\n      flight\n    }\n  }\n}\n"""\n\nresult = rath.execute(query)\n```\n\nThis example composes both the AuthToken and AioHttp link: During each query the Bearer headers are set to the retrieved token, on authentication fail (for example if Token Expired) the\nAuthToken automatically refetches the token and retries the query.\n\n## Async Usage\n\nRath is build with koil, for async/sync compatibility but also exposed a complete asynhronous api\n\n```python\nfrom rath.links.auth import AuthTokenLink\nfrom rath.links.aiohttp import AioHttpLink\nfrom rath.links import compose, split\nfrom rath.gql import gql\n\nasync def aload_token():\n    return "SERVER_TOKEN"\n\n\nauth = AuthTokenLink(token_loader=aload_token)\nlink = AioHttpLink(url="https://api.spacex.land/graphql/")\n\n\nasync def main()\n  rath = Rath(links=compose(auth,link))\n  await rath.aconnect()\n\n\n  query = """query TestQuery {\n    capsules {\n      id\n      missions {\n        flight\n      }\n    }\n  }\n  """\n\n  result = await rath.aexecute(query)\n\nasyncio.run(main())\n```\n\n## Included Links\n\n- Reconnecting WebsocketLink (untested)\n- AioHttpLink (supports multipart uploads)\n- SplitLink (allows to split the terminating link - Subscription into WebsocketLink, Query, Mutation into Aiohttp)\n- AuthTokenLink (Token insertion with automatic refresh)\n\n### Why Rath\n\nWell "apollo" is already taken as a name, and rath (according to wikipedia) is an etruscan deity identified with Apollo.\n\n## Rath + Turms\n\nRath works especially well with turms generated typed operations:\n\n```python\nimport asyncio\nfrom examples.api.schema import aget_capsules\nfrom rath.rath import Rath\nfrom rath.links.aiohttp import AIOHttpLink\nfrom rath.links.auth import AuthTokenLink\nfrom rath.links.compose import compose\n\n\nasync def token_loader():\n    return ""\n\n\nlink = compose(\n    AuthTokenLink(token_loader), AIOHttpLink("https://api.spacex.land/graphql/")\n)\n\n\nRATH = Rath(\n    link=link,\n    register=True, # allows global access (singleton-antipattern, but rath has no state)\n)\n\n\nasync def main():\n    capsules = await aget_capsules() # fully typed pydantic powered dataclasses generated through turms\n    print(capsules)\n\n\nasyncio.run(main())\n\n```\n\n## Examples\n\nThis github repository also contains an example client with a turms generated query with the public SpaceX api, as well as a sample of the generated api.\n\n## CLI\n\n```bash\nrath run\n```\n',
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
