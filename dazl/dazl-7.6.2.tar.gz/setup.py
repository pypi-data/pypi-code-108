# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['_dazl_pb',
 '_dazl_pb.plugin_python',
 '_dazl_pb.protoc',
 '_dazl_pb.syntax',
 '_dazl_pb.syntax.python',
 '_dazl_pb.util',
 'dazl',
 'dazl._gen',
 'dazl._gen.com',
 'dazl._gen.com.daml',
 'dazl._gen.com.daml.daml_lf_1_14',
 'dazl._gen.com.daml.ledger',
 'dazl._gen.com.daml.ledger.api',
 'dazl._gen.com.daml.ledger.api.v1',
 'dazl._gen.com.daml.ledger.api.v1.admin',
 'dazl._gen.com.daml.ledger.api.v1.testing',
 'dazl.cli',
 'dazl.client',
 'dazl.damlast',
 'dazl.ledger',
 'dazl.ledger.aio',
 'dazl.ledger.blocking',
 'dazl.ledger.config',
 'dazl.ledger.grpc',
 'dazl.ledgerutil',
 'dazl.metrics',
 'dazl.model',
 'dazl.pretty',
 'dazl.pretty.table',
 'dazl.prim',
 'dazl.protocols',
 'dazl.protocols.v0',
 'dazl.protocols.v1',
 'dazl.protocols.v1.model',
 'dazl.query',
 'dazl.scheduler',
 'dazl.server',
 'dazl.testing',
 'dazl.util',
 'dazl.values']

package_data = \
{'': ['*']}

install_requires = \
['googleapis_common_protos>=1,<2',
 'grpcio>=1.32.0',
 'protobuf>=3.12.0',
 'requests',
 'semver',
 'toposort']

extras_require = \
{':python_full_version < "3.8.0"': ['typing_extensions'],
 ':python_full_version >= "3.6.0" and python_full_version < "3.7.0"': ['async_exit_stack',
                                                                       'dataclasses'],
 'oauth': ['google-auth', 'oauthlib'],
 'prometheus': ['prometheus_client'],
 'pygments': ['pygments'],
 'server': ['aiohttp']}

entry_points = \
{'console_scripts': ['dazl = dazl.cli:main',
                     'protoc-gen-dazl-python = _dazl_pb.plugin_python:main']}

setup_kwargs = {
    'name': 'dazl',
    'version': '7.6.2',
    'description': 'high-level Ledger API client for Daml ledgers',
    'long_description': 'dazl\n====\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/digital-asset/dazl-client/blob/main/LICENSE)\n<a href="https://circleci.com/gh/digital-asset/dazl-client">\n<img src="https://circleci.com/gh/digital-asset/dazl-client.svg?style=svg">\n</a>\n\nCopyright (c) 2017-2022 Digital Asset (Switzerland) GmbH and/or its affiliates. All Rights Reserved.\nSPDX-License-Identifier: Apache-2.0\n\n\nRich Python bindings for accessing Ledger API-based applications.\n\nDocumentation\n-------------\nThe user documentation is available online [here](https://digital-asset.github.io/dazl-client).\n\nInstallation\n------------\nIf you just want to use the library, you can install it locally with `pip`:\n```sh\npip install --user dazl\n```\n\nRequirements\n------------\n* Python 3.6+\n* [Daml Connect](https://www.daml.com)\n* Python gRPC libraries (1.32.0 or later) and Protobuf\n\n**WARNING:** The next major version of dazl (v8.0.0) will require **Python 3.7** or later.\n\nExamples\n--------\n\nAll of the examples below assume you imported `dazl`, and are running a ledger with the default scenario generated with `daml new`.\n\nConnect to the ledger and submit a single command:\n\n```py\nimport asyncio\nimport dazl\n\nasync def main():\n    async with dazl.connect(url=\'http://localhost:6865\', act_as=\'Alice\') as client:\n        contract = { \'issuer\' : \'Alice\', \'owner\' : \'Alice\', \'name\' : \'hello world!\' }\n        await client.create(\'Main:Asset\', contract)\n\n# Python 3.7+\nasyncio.run(main())\n\n# Python 3.6+\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main())\n```\n\nConnect to the ledger as a single party, print all contracts, and close:\n\n```py\nimport asyncio\nimport dazl\nfrom dazl.ledgerutil import ACS\n\nasync def main():\n    async with dazl.connect(url=\'http://localhost:6865\', read_as=\'Alice\') as conn:\n        async with ACS(conn, {"*": {}}) as acs:\n            snapshot = await acs.read()\n\n    print(snapshot)\n\n# Python 3.7+\nasyncio.run(main())\n\n# Python 3.6+\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main())\n```\n\nBuilding locally\n----------------\n\nYou will need additional dependencies to build locally:\n\n* GNU Make\n* [Poetry](https://python-poetry.org/) for build/dependency management\n\nOnce you have these prerequisites in place:\n\n```sh\nmake build\n```\n\nIf you see errors about incompatible python versions, switch your environment to python3 using `poetry env use python3`, for instance.\n\nTests\n-----\n\nTests in dazl are written using [pytest](https://docs.pytest.org/en/latest/). You can run them by doing:\n\n```sh\nmake test\n```\n\nSupport\n-------\n\nThe dazl library is supported by the Daml community. If you are in need of support, have questions or just want to engage in friendly conversation anything Daml, contact us on our [Daml Community Forum](https://discuss.daml.com).\n',
    'author': 'Davin K. Tanabe',
    'author_email': 'davin.tanabe@digitalasset.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/digital-asset/dazl-client',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
