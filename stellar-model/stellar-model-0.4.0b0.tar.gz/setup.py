# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stellar_model',
 'stellar_model.model',
 'stellar_model.model.horizon',
 'stellar_model.response']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'stellar-model',
    'version': '0.4.0b0',
    'description': 'Parse the raw Stellar data into Python models.',
    'long_description': '=============\nstellar-model\n=============\n.. image:: https://img.shields.io/github/workflow/status/StellarCN/stellar-model/GitHub%20Action/main?style=flat&maxAge=1800\n    :alt: GitHub Action\n    :target: https://github.com/StellarCN/stellar-model/actions\n\n.. image:: https://img.shields.io/readthedocs/stellar-model.svg?style=flat&maxAge=1800\n    :alt: Read the Docs\n    :target: https://stellar-model.readthedocs.io/en/latest/\n\n.. image:: https://img.shields.io/pypi/v/stellar-model.svg?style=flat&maxAge=1800\n    :alt: PyPI\n    :target: https://pypi.python.org/pypi/stellar-model\n\n.. image:: https://img.shields.io/badge/Supported%20Horizon%20Version-2.8.3-blue?style=flat\n    :alt: Supported Horizon Version\n    :target: https://github.com/stellar/go/releases/tag/horizon-v2.8.3\n\n.. image:: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue?style=flat\n    :alt: Python - Version\n    :target: https://pypi.python.org/pypi/stellar-model\n\n.. image:: https://img.shields.io/badge/implementation-cpython%20%7C%20pypy-blue?style=flat\n    :alt: PyPI - Implementation\n    :target: https://pypi.python.org/pypi/stellar-model\n\n`stellar-model`_ is based on `pydantic`_, you can use it to parse the JSON\nreturned by `Stellar Horizon`_ into Python models, through it, you can get a better\ndevelopment experience in the editor with things like code completion, type hints, and more.\n\nInstalling\n==========\n\nYou need to choose a suitable stellar-model version according to the Horizon version number you are using.\nPlease check the list `here <https://github.com/StellarCN/stellar-model/issues/20/>`_.\n\n.. code-block:: text\n\n    pip install stellar-model==0.3.1b0\n\nExample\n=======\n.. code-block:: python\n\n    import requests\n    from stellar_model import AccountResponse\n\n    url = "https://horizon.stellar.org/accounts/GALAXYVOIDAOPZTDLHILAJQKCVVFMD4IKLXLSZV5YHO7VY74IWZILUTO"\n    raw_resp = requests.get(url).json()\n    parsed_resp = AccountResponse.parse_obj(raw_resp)\n    print(f"Account Sequence: {parsed_resp.sequence}")\n\n\nOf course you can use it with `stellar-sdk`_.\n\n.. code-block:: python\n\n    from stellar_sdk import Server\n    from stellar_model import AccountResponse\n\n    server = Server("https://horizon.stellar.org")\n    account_id = "GALAXYVOIDAOPZTDLHILAJQKCVVFMD4IKLXLSZV5YHO7VY74IWZILUTO"\n    raw_resp = server.accounts().account_id(account_id).call()\n    parsed_resp = AccountResponse.parse_obj(raw_resp)\n    print(f"Account Sequence: {parsed_resp.sequence}")\n\n\nDocumentation\n=============\nstellar-model\'s documentation can be found at https://stellar-model.readthedocs.io\n\n\n.. _stellar-model: https://github.com/StellarCN/stellar-model\n.. _pydantic: https://pydantic-docs.helpmanual.io/\n.. _Stellar Horizon: https://developers.stellar.org/api/resources/\n.. _stellar-sdk: https://github.com/StellarCN/py-stellar-base',
    'author': 'overcat',
    'author_email': '4catcode@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/StellarCN/stellar-model',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
