# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pocketsmith',
 'pocketsmith.api',
 'pocketsmith.apis',
 'pocketsmith.model',
 'pocketsmith.models']

package_data = \
{'': ['*']}

modules = \
['LICENSE', 'CHANGELOG']
install_requires = \
['certifi', 'python-dateutil', 'six', 'urllib3[secure]']

setup_kwargs = {
    'name': 'pocketsmith-api',
    'version': '2.1.1',
    'description': 'Pocketsmith API client',
    'long_description': "# pocketsmith-api\n[Pocketsmith](https://pocketsmith.com) API client, automatically generated with [OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator) from a [manicured version](https://github.com/theY4Kman/pocketsmith-api-spec) of the [official OpenAPI spec](https://github.com/pocketsmith/api)\n\n\n# Installation\n```bash\npip install pocketsmith-api\n```\n\n\n# Usage\n```pycon\n>>> import pocketsmith\n>>> client = pocketsmith.PocketsmithClient('my-api-key')\n>>> client.users.get_me()\n{'always_show_base_currency': False,\n 'avatar_url': 'https://secure.gravatar.com/avatar/73e4f4549e97ad9d53e11b8e987f4b90?d=404',\n 'base_currency_code': 'usd',\n 'beta_user': True,\n 'created_at': datetime.datetime(2016, 10, 17, 6, 22, 44, tzinfo=tzutc()),\n 'email': 'yak@y4k.dev',\n 'id': 1234565,\n 'last_activity_at': datetime.datetime(2020, 10, 3, 6, 57, 44, tzinfo=tzutc()),\n 'last_logged_in_at': datetime.datetime(2020, 10, 3, 4, 58, 35, tzinfo=tzutc()),\n 'login': 'yamsandwich',\n 'name': 'Yam S Andwich',\n 'time_zone': 'Eastern Time (US & Canada)',\n 'updated_at': datetime.datetime(2020, 10, 3, 6, 57, 44, tzinfo=tzutc()),\n 'using_multiple_currencies': False,\n 'week_start_day': 0}\n```\n\n\n# Generating the library\nThe [`@openapitools/openapi-generator-cli`](https://github.com/OpenAPITools/openapi-generator-cli) npm package is used for generation. This package will automatically download the latest OpenAPI Generator .jar. To install, run:\n```bash\nnpm install -g @openapitools/openapi-generator-cli\n```\n\nThen, run the following to generate the library from spec, and add a few customizations on top (like the `PocketsmithClient` class)\n```bash\n./generate-pocketsmith-library.sh\n```\n",
    'author': 'Zach "theY4Kman" Kanzler',
    'author_email': 'they4kman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theY4Kman/python-pocketsmith-api',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
