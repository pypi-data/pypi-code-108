# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyngsild',
 'pyngsild.agent',
 'pyngsild.agent.bg',
 'pyngsild.sink',
 'pyngsild.source',
 'pyngsild.utils']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0,<0.71.0',
 'more-itertools>=8.10.0,<9.0.0',
 'ngsildclient>=0.1.1,<0.2.0',
 'openpyxl>=3.0.9,<4.0.0',
 'paho-mqtt>=1.6.1,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'schedule>=1.1.0,<2.0.0',
 'shortuuid>=1.0.8,<2.0.0',
 'uvicorn[standard]>=0.15.0,<0.16.0',
 'watchgod>=0.7,<0.8',
 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'pyngsild',
    'version': '0.1.0',
    'description': 'A Python data-centric framework whose goal is to ease and speed up the development of NGSI-LD agents',
    'long_description': '# pyngsild\n\n[![PyPI](https://img.shields.io/pypi/v/pyngsild.svg)](https://pypi.org/project/pyngsild/)\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n\n## Overview\n\n**pyngsild** is a Python data-centric framework whose goal is to ease and speed up the development of [NGSI-LD](https://fiware.github.io/specifications/ngsiv2/stable) agents.\n\nBy providing a clean and simple structure - with components organized as a NGSI-LD data pipeline - the framework allows the developer to avoid the plumbing and focus on the data.\n\n## Key Features\n\n- Agents that rely on the pyngsild framework all share a common structure\n- Many DataSources included\n- Statistics\n- Monitoring *(for background agents)*\n- Error handling\n- Logging\n- Well-tested components\n- Provide primitives to build NGSI-LD compliant entities *(thanks to the [ngsildclient](https://pypi.org/project/ngsildclient/) library)*\n\n## How it works\n\n### DataSources\n\nWhat most differentiates an agent from another is the datasource.\n\nNot only the nature of the data differs but also :\n- the data representation : text, json, ...\n- the way data are accessed : read from a file, received through the network, ...\n\n**pyngsild** provides a level of abstraction in order to expose any datasource in a same way, whether :\n- the agent **consumes** a datasource *(i.e. reads a file, requests an API)*\n- the agent **is triggered** by the datasource *(acts as a daemon listening to incoming data pushed by the datasource)*\n\nAs datasources have very little in common, the only assumption made by the framework is : a **pyngsild** Source is iterable.\n\n*For illustrative purposes an element accessed from a Source could be a line from a CSV file, an item from a JSON array, or a row from a Pandas dataframe.*\n\nMany generic Sources are provided by the framework and it\'s easy to create new ones.\n\n### The pipeline\n\nA NGSI-LD Agent typically :\n- collects data from a datasource\n- builds "normalized" NGSI-LD entities *(according to a domain-specific DataModel)*\n- eventually feeds the Context Broker\n\nThe framework allows to create an **Agent** by providing a **Source**, a **Sink** and a **processor** function.\n\nThe Source collects data from the datasource.\n\nWhen the Agent runs, it iterates over the Source to collect Rows.\n\nThe processor function takes a **Row** and builds a NGSI-LD **Entity** from it.\n\nA Row is an object composed of two attributes : record and provider\n- record: Any = the raw incoming data\n- provider: str = a label indicating the data provider\n\nEventually the Entity is sent to the **Sink** which is in production mode the **Context Broker**.\n\n<pre>\n+-----------------------------------------------------------------------------------+\n|                                                                                   |\n|                                                                                   |\n|      +--------------+                                       +--------------+      |\n|      |              |     Row                    Entity     |              |      |\n|      |    Source    |-------------> process() ------------->|     Sink     |      |\n|      |              |                                       |              |      |\n|      +--------------+                                       +--------------+      |\n|                                                                                   |\n|                                                                                   |\n+-----------------------------------------------------------------------------------+\n                                        Agent    \n</pre>\n\n## Where to get it\nThe source code is currently hosted on GitHub at :\nhttps://github.com/Orange-OpenSource/pyngsild\n\nBinary installer for the latest released version is available at the [Python\npackage index](https://pypi.org/project/pyngsild).\n\n```sh\npip install pyngsild\n```\n\n## Installation\n\n**pyngsild** requires Python 3.10+.\n\nOne should use a virtual environment. For example with pyenv.\n\n```sh\nmkdir myfiwareproject && cd myfiwareproject\npyenv virtualenv 3.10.2 myfiwareproject\npyenv local\npip install pyngsild\n```\n\n## Getting started\n\n### Create a Source\n\nFor example let\'s create a Source that collects data about companies bitcoin holdings thanks to the CoinGecko API.\n\n```python\nimport requests\nfrom pyngsild import *\nfrom ngsildclient import *\n\nCOINGECKO_BTC_CAP_ENDPOINT = "https://api.coingecko.com/api/v3/companies/public_treasury/bitcoin"\n\nsrc = SourceApi(lambda: requests.get(COINGECKO_BTC_CAP_ENDPOINT), path="companies", provider="CoinGecko API")\n```\n\nHave a look [here](coingecko_btc_cap_sample.json) for a sample API result.\n\n### Provide a processor function\n\nYou have to provide the framework with a **processor** function, that will be used to transform a Row into a NGSI-LD compliant entity.\n\n```python\ndef build_entity(row: Row) -> Entity:\n    record: dict = row.record\n    market, symbol = [x.strip() for x in record["symbol"].split(":")]\n    e = Entity("BitcoinCapitalization", f"{market}:{symbol}:{iso8601.utcnow()}")\n    e.obs()\n    e.prop("dataProvider", row.provider)\n    e.prop("companyName", record["name"])\n    e.prop("stockMarket", market)\n    e.prop("stockSymbol", symbol)\n    e.prop("country", record["country"])\n    e.prop("totalHoldings", record["total_holdings"], unitcode="BTC", observedat=Auto)\n    e.prop("totalValue", record["total_current_value_usd"], unitcode="USD", observedat=Auto)\n    return e\n```\n\nHave a look [here](company_entity_sample.json) for a sample NGSI-LD Entity built with this function.\n\n### Run the Agent\n\nLet\'s create the Sink, the Agent and make all parts work together.\n\n```python\nsink = SinkNgsi() # replace by SinkStdout() if you don\'t have a Context Broker\nagent = Agent(src, sink, process=build_entity)\nagent.run()\nprint(agent.stats) # input=27, processed=27, output=27, filtered=0, error=0, side_entities=0\nagent.close()\n```\n\nWe\'re done !\n\nThe Context Broker should have created a set of entities *(27 at the time of writing)*.\n\n## License\n\n[Apache 2.0](LICENSE)\n',
    'author': 'fbattello',
    'author_email': 'fabien.battello@orange.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Orange-OpenSource/pyngsild',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
