# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_ado', 'simple_ado.models']

package_data = \
{'': ['*']}

install_requires = \
['deserialize>=1.5.1,<2.0.0', 'requests>=2.21,<3.0', 'tenacity>=6.2.0,<7.0.0']

setup_kwargs = {
    'name': 'simple-ado',
    'version': '3.3.0',
    'description': 'A simple wrapper around the Azure DevOps REST API',
    'long_description': "# simple_ado\n\n`simple_ado` is a Python wrapper around the Azure DevOps REST API.\n\nWhy does it exist when there is an existing Python SDK for the ADO API? \n\nSimply put, it's because the existing one is very complex and difficult to use. This version aims to be as simple as possible to use.\n\n\n# Contributing\n\nThis project welcomes contributions and suggestions.  Most contributions require you to agree to a\nContributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us\nthe rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.\n\nWhen you submit a pull request, a CLA bot will automatically determine whether you need to provide\na CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions\nprovided by the bot. You will only need to do this once across all repos using our CLA.\n\nThis project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).\nFor more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or\ncontact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.\n",
    'author': 'Dale Myers',
    'author_email': 'dalemy@microsoft.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Microsoft/simple_ado',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
