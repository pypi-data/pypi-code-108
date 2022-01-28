# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['peachpayments_partner']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.3.0,<3.0.0',
 'cryptography>=35.0.0,<36.0.0',
 'iso4217>=1.6.20180829,<2.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'peachpayments-partner',
    'version': '0.1.0',
    'description': 'PeachPayments Partner Library is a platform agnostic Python package to help integrating PeachPayments with their partners.',
    'long_description': '# Peach Partner Library\n\n## Overview\n\n**Peach Partner Library** is a platform-agnostic Python package to help Payment Service Providers in integrating with PeachPayments.\n\n**Documentation**:\n\n**Source Code**: <https://gitlab.com/peachpayments/peach-partner-python/>\n\n* * *\n\n### Key terms\n\n| Term                     | Definition                                                                                                         |\n| ------------------------ | ------------------------------------------------------------------------------------------------------------------ |\n| Partner API              | A service provided by Peach Payments to enable Payment Service Providers to become available on the Peach Platform |\n| Payment Service Provider | A payment service provider who integrates with the Partner API                                                     |\n\n## Installation\n\nPackage requires Python 3.9+\n\n```sh\n# pip\n$ pip3 install peachpayments-partner\n```\n\n```sh\n# poetry\n$ poetry add peachpayments-partner\n```\n\n## Result codes\n\n```python\nfrom peachpayments_partner.result_codes import result_codes\n\nresult_codes.TRANSACTION_SUCCEEDED.code == "000.000.000"\nresult_codes.get("000.000.000").name == "TRANSACTION_SUCCEEDED"\nresult_codes.get("000.000.000").description == "Transaction succeeded"\n```\n\n## Authentication\n\n### Requests to Payment Service Provider\n\nPeachPayments uses an authorization token (JWT) in each request made to the Payment Service Provider.\nThis library provides the `authentication.is_authenticated` method, which takes the token as an argument and the `authentication.get_key` to collect the signing_key.\n\nThe `is_authenticated` method has only one required argument, the token. If it\'s called without the optional `signing_key` it will collect the key using the `get_key` method. If it\'s called without the optional `audience` it will try to use the environment variable `AUTH0_AUDIENCE`.\n\nThe method decodes the token. If that succeeds, it returns `True`. Otherwise, it raises an `AuthError` exception.\n\n## Formatting error responses\n\nPeachPayments requires the error responses to be formatted in a specific way. This library provides the `format_error_response` method, which takes a dict containing error response as an argument and returns a formatted error response.\n\n```python\ndef format_error_response(code, errors, data):\n```\nThe `errors` dict might look like this:\n\n```python\n{\n    "status": ["Not a valid string."],\n    "code": ["Missing data for required field."],\n}\n```\n\nThe `data` dict might look like this:\n\n```python\n{\n  "status": 10\n}\n```\n\nWith the `code` as `ResultCodes.INVALID_OR_MISSING_PARAMETER`, the formatted error response will look similar to this:\n\n```python\n{\n    "result": {\n      "code": "200.300.404",\n      "description": "invalid or missing parameter",\n      "parameterErrors": [\n          {\n              "value": 10,\n              "name": "status",\n              "message": "Not a valid string."\n          },\n          {\n              "name": "code",\n              "message": "Missing data for required field."\n          }\n      ]\n  },\n  "timestamp": "2021-08-03T16:16:30.992618Z"\n}\n```\n\n## Fixtures\n\nThis library provides examples of valid requests and responses.\n\nAn example of the recommended usage for testing:\n\n```python\nimport pytest\nfrom copy import deepcopy\nfrom peachpayments_partner.fixtures import DEBIT_RESPONSE\n\n@pytest.fixture\ndef debit_response():\n    return deepcopy(DEBIT_RESPONSE)\n```',
    'author': 'PeachPayments',
    'author_email': 'support@peachpayments.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/peachpayments/peach-partner-python/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
