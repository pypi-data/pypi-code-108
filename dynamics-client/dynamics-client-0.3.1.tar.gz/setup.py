# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynamics']

package_data = \
{'': ['*']}

install_requires = \
['oauthlib>=3.1.0', 'requests-oauthlib>=1.3.0', 'tzdata>=2021.5']

extras_require = \
{'django': ['Django>=3.2', 'djangorestframework>=3.12'],
 'typing': ['typing-extensions>=4.0'],
 'zoneinfo': ['backports.zoneinfo>=0.2.1']}

setup_kwargs = {
    'name': 'dynamics-client',
    'version': '0.3.1',
    'description': 'Client for making Web API request from a Microsoft Dynamics 365 Database.',
    'long_description': '# Dynamics Web API Client\n\n[![Coverage Status](https://coveralls.io/repos/github/MrThearMan/dynamics-client/badge.svg?branch=main)](https://coveralls.io/github/MrThearMan/dynamics-client?branch=main)\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/MrThearMan/dynamics-client/Tests)](https://github.com/MrThearMan/dynamics-client/actions/workflows/main.yml)\n[![PyPI - Version](https://img.shields.io/pypi/v/dynamics-client)](https://pypi.org/project/dynamics-client)\n[![License](https://img.shields.io/github/license/MrThearMan/dynamics-client)](https://github.com/MrThearMan/dynamics-client/blob/main/LICENSE)\n[![GitHub last commit](https://img.shields.io/github/last-commit/MrThearMan/dynamics-client)](https://github.com/MrThearMan/dynamics-client/commits/main)\n[![GitHub issues](https://img.shields.io/github/issues-raw/MrThearMan/dynamics-client)](https://github.com/MrThearMan/dynamics-client/issues)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dynamics-client)](https://pypi.org/project/dynamics-client)\n\n```shell\npip install dynamics-client\n```\n\n---\n\n**Documentation**: [https://mrthearman.github.io/dynamics-client/](https://mrthearman.github.io/dynamics-client/)\n\n**Source Code**: [https://github.com/MrThearMan/dynamics-client](https://github.com/MrThearMan/dynamics-client)\n\n---\n\n\nClient for making Web API request from a Microsoft Dynamics 365 Database.\n\nYou should also read the [Dynamics Web API Reference Docs](https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api):\n\n## Basic usage:\n\n```python\nfrom dynamics import DynamicsClient, ftr\n\n# Init the client:\nclient = DynamicsClient(...)\n\n### Example GET request:\n\nclient.table = "accounts"\n\n# Get only these columns for the account.\nclient.select = ["accountid", "name"]\n\n# Filter to only the accounts that have been created on or after the\n# given ISO date string, AND that have 200 or more employees.\nclient.filter = [\n    ftr.on_or_after("createdon", "2020-01-01T00:00:00Z"),\n    ftr.ge("numberofemployees", 200),\n]\n\n# Expand to the contacts (collection-values navigation property)\n# on the account that have \'gmail.com\' in their email address 1 OR 2.\n# Get only the \'firstname\', \'lastname\' and \'mobilephone\' columns for these contacts.\n# Also expand the primary contact (single-valued navigation property).\n# Get only the \'emailaddress1\' column for the primary contact.\nclient.expand = {\n    "contact_customer_accounts": {\n        "select": ["firstname", "lastname", "mobilephone"],\n        "filter": {\n            ftr.contains("emailaddress1", "gmail.com"),\n            ftr.contains("emailaddress2", "gmail.com"),\n        }\n    },\n    "primarycontactid": {\n        "select": ["emailaddress1"],\n    },\n}\n\nresult = client.get()\n\n# [\n#     {\n#         "accountid": ...,\n#         "name": ...,\n#         "contact_customer_accounts": [\n#             {\n#                 "contactid": ...,  # id field is always given\n#                 "firstname": ...,\n#                 "lastname": ...,\n#                 "mobilephone": ...\n#             },\n#             ...\n#         ],\n#         "primarycontactid": {\n#             "contactid": ...,\n#             "emailaddress1": ...\n#         }\n#     },\n#     ...\n# ]\n\n### Example POST request\n\n# IMPORTANT!!!\nclient.reset_query()\n\nclient.table = "contacts"\n\n# Get only these columns from the created contact\nclient.select = ["firstname", "lastname", "emailaddress1"]\n\n# The data to create the contact with. \'@odata.bind\' is used to link\n# the contact to the given navigation property.\naccountid = ...\ndata = {\n    "firstname": ...,\n    "lastname": ...,\n    "emailaddress1": ...,\n    "parentcustomerid_account@odata.bind": f"/accounts({accountid})"\n}\n\nresult = client.post(data=data)\n\n# {\n#     "contactid": ...,\n#     "firstname": ...,\n#     "lastname": ...,\n#     "emailaddress1": ...\n# }\n\n\n### Example PATCH request\n\nclient.reset_query()\n\nclient.table = "contacts"\nclient.row_id = result["contactid"]\n\ndata = {\n    "firstname": ...,\n    "lastname": ...,\n}\n\nresult = client.patch(data=data)\n\n# Return all rows on the updated contact,\n# since no select statement was given\n#\n# {\n#     ...\n#     "contactid": ...,\n#     "firstname": ...,\n#     "lastname": ...,\n#     ...\n# }\n\n\n### Example DELETE request\n\nclient.reset_query()\n\nclient.table = "contacts"\nclient.row_id = result["contactid"]\n\nclient.delete()\n```',
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrThearMan/dynamics-client/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
