# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gotrue', 'gotrue._async', 'gotrue._sync']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.21.3,<0.22.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'gotrue',
    'version': '0.5.0',
    'description': 'Python Client Library for GoTrue',
    'long_description': '# gotrue-py\n\n[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?label=license)](https://opensource.org/licenses/MIT)\n[![CI](https://github.com/supabase-community/gotrue-py/actions/workflows/ci.yml/badge.svg)](https://github.com/supabase-community/gotrue-py/actions/workflows/ci.yml)\n[![Python](https://img.shields.io/pypi/pyversions/gotrue)](https://pypi.org/project/gotrue)\n[![Version](https://img.shields.io/pypi/v/gotrue?color=%2334D058)](https://pypi.org/project/gotrue)\n[![Codecov](https://codecov.io/gh/supabase-community/gotrue-py/branch/main/graph/badge.svg)](https://codecov.io/gh/supabase-community/gotrue-py)\n[![Last commit](https://img.shields.io/github/last-commit/supabase-community/gotrue-py.svg?style=flat)](https://github.com/supabase-community/gotrue-py/commits)\n[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/supabase-community/gotrue-py)](https://github.com/supabase-community/gotrue-py/commits)\n[![Github Stars](https://img.shields.io/github/stars/supabase-community/gotrue-py?style=flat&logo=github)](https://github.com/supabase-community/gotrue-py/stargazers)\n[![Github Forks](https://img.shields.io/github/forks/supabase-community/gotrue-py?style=flat&logo=github)](https://github.com/supabase-community/gotrue-py/network/members)\n[![Github Watchers](https://img.shields.io/github/watchers/supabase-community/gotrue-py?style=flat&logo=github)](https://github.com/supabase-community/gotrue-py)\n[![GitHub contributors](https://img.shields.io/github/contributors/supabase-community/gotrue-py)](https://github.com/supabase-community/gotrue-py/graphs/contributors)\n\nThis is a Python port of the [supabase js gotrue client](https://github.com/supabase/gotrue-js). The current state is that there is a features parity but with small differences that are mentioned in the section **Differences to the JS client**.\n\n## Installation\n\nWe are still working on making the `gotrue` python library more user-friendly. For now here are some sparse notes on how to install the module.\n\n### Poetry\n\n```bash\npoetry add gotrue\n```\n\n### Pip\n\n```bash\npip install gotrue\n```\n\n## Differences to the JS client\n\nIt should be noted there are differences to the [JS client](https://github.com/supabase/gotrue-js). If you feel particulaly strongly about them and want to motivate a change, feel free to make a GitHub issue and we can discuss it there.\n\nFirstly, feature pairity is not 100% with the [JS client](https://github.com/supabase/gotrue-js). In most cases we match the methods and attributes of the [JS client](https://github.com/supabase/gotrue-js) and api classes, but is some places (e.g for browser specific code) it didn\'t make sense to port the code line for line.\n\nThere is also a divergence in terms of how errors are raised. In the [JS client](https://github.com/supabase/gotrue-js), the errors are returned as part of the object, which the user can choose to process in whatever way they see fit. In this Python client, we raise the errors directly where they originate, as it was felt this was more Pythonic and adhered to the idioms of the language more directly.\n\nIn JS we return the error, but in Python we just raise it.\n\n```js\nconst { data, error } = client.sign_up(...)\n```\n\nThe other key difference is we do not use pascalCase to encode variable and method names. Instead we use the snake_case convention adopted in the Python language.\n\nAlso, the `gotrue` library for Python parses the date-time string into `datetime` Python objects. The [JS client](https://github.com/supabase/gotrue-js) keeps the date-time as strings.\n\n## Usage (outdated)\n\n**Important:** This section is outdated, you can be guided by the [JS client documentation](https://supabase.github.io/gotrue-js) because this Python client has a lot of parity with the JS client.\n\nTo instantiate the client, you\'ll need the URL and any request headers at a minimum.\n\n```python\nfrom gotrue import Client\n\nheaders = {\n    "apiKey": "my-mega-awesome-api-key",\n    # ... any other headers you might need.\n}\nclient: Client = Client(url="www.genericauthwebsite.com", headers=headers)\n```\n\nTo send a magic email link to the user, just provide the email kwarg to the `sign_in` method:\n\n```python\nuser: Dict[str, Any] = client.sign_up(email="example@gmail.com")\n```\n\nTo login with email and password, provide both to the `sign_in` method:\n\n```python\nuser: Dict[str, Any] = client.sign_up(email="example@gmail.com", password="*********")\n```\n\nTo sign out of the logged in user, call the `sign_out` method. We can then assert that the session and user are null values.\n\n```python\nclient.sign_out()\nassert client.user() is None\nassert client.session() is None\n```\n\nWe can refesh a users session.\n\n```python\n# The user should already be signed in at this stage.\nuser = client.refresh_session()\nassert client.user() is not None\nassert client.session() is not None\n```\n\n## Contributions\n\nWe would be immensely grateful for any contributions to this project. In particular are the following items:\n\n- Add documentation\n- Update `README.md`\n',
    'author': 'Joel Lee',
    'author_email': 'joel@joellee.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/supabase-community/gotrue-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
