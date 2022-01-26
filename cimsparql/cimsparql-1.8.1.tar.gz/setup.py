# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cimsparql']

package_data = \
{'': ['*']}

install_requires = \
['SPARQLWrapper', 'networkx', 'numpy', 'pandas', 'requests', 'tables']

extras_require = \
{'parse_xml': ['pendulum', 'lxml']}

setup_kwargs = {
    'name': 'cimsparql',
    'version': '1.8.1',
    'description': 'CIM query utilities',
    'long_description': '[![PyPI version](https://img.shields.io/pypi/v/cimsparql)](https://pypi.org/project/cimsparql/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/cimsparql)](https://pypi.org/project/cimsparql/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![](https://github.com/statnett/data_cache/workflows/Tests/badge.svg)](https://github.com/statnett/cimsparql/actions?query=workflow%3ATests)\n[![codecov](https://codecov.io/gh/statnett/cimsparql/branch/master/graph/badge.svg)](https://codecov.io/gh/statnett/cimsparql)\n\n# CIMSPARQL Query CIM data using sparql\n\nThis Python package provides functionality for reading/parsing cim data from\neither xml files or GraphDB into Python memory as pandas dataframes.\n\nThe package provides a set of predefined functions/queries to load CIM data\nsuch generator or branch data, though the user can easiliy extend or define\ntheir own queries.\n\n## Usage\n\n### Load data using predefined functions/queries\n\n```python\n>>> from cimsparql.graphdb import GraphDBClient\n>>> from cimsparql.url import service\n>>> gdbc = GraphDBClient(service(repo=\'<repo>\', server=127.0.0.1:7200))\n>>> ac_lines = gdbc.ac_lines(limit=3)\n>>> print(ac_lines[[\'name\', \'x\', \'r\', \'bch\']])\n         name       x       r       bch\n0  <branch 1>  1.9900  0.8800  0.000010\n1  <branch 2>  1.9900  0.8800  0.000010\n2  <branch 3>  0.3514  0.1733  0.000198\n```\n\nIn the example above the client will query repo "<repo>" in the default server\n[GraphDB](https://graphdb.ontotext.com) for AC line values.\n\n### Inspect/view predefined queries\n\nTo see the actual sparql use the `dry_run` option:\n\n```python\n>>> from cimsparql.queries import ac_line_query\n>>> print(ac_line_query(limit=3, dry_run=True))\n```\n\nThe resulting string contains all the prefix\'s available in the Graphdb repo\nmaking it easier to copy and past to graphdb. Note that the prefixes are *not*\nrequired in the user specified quires described below.\n\nThe `dry_run` option is available for all the predefined queries.\n\n### Load data using user specified queries\n\n```python\n>>> query = \'SELECT ?mrid where { ?mrid rdf:type cim:ACLineSegment } limit 2\'\n>>> query_result = gdbc.get_table(query)\n>>> print(query_result)\n```\n\n### List of available repos at the server\n\n```python\n>>> from cimsparql.url import GraphDbConfig\n>>> print(GraphDbConfig().repos)\n```\n\n### Prefix and namespace\n\nAvailable namespace for current graphdb client (`gdbc` in the examples above),\nwhich can be used in queries (such as `rdf` and `cim`) can by found by\n\n```python\n>>> print(gdbc.ns)\n{\'wgs\': \'http://www.w3.org/2003/01/geo/wgs84_pos#\',\n \'rdf\': \'http://www.w3.org/1999/02/22-rdf-syntax-ns#\',\n \'owl\': \'http://www.w3.org/2002/07/owl#\',\n \'cim\': \'http://iec.ch/TC57/2010/CIM-schema-cim15#\',\n \'gn\': \'http://www.geonames.org/ontology#\',\n \'xsd\': \'http://www.w3.org/2001/XMLSchema#\',\n \'rdfs\': \'http://www.w3.org/2000/01/rdf-schema#\',\n \'SN\': \'http://www.statnett.no/CIM-schema-cim15-extension#\',\n \'ALG\': \'http://www.alstom.com/grid/CIM-schema-cim15-extension#\'}\n```\n',
    'author': 'Statnett Datascience',
    'author_email': 'Datascience.Drift@Statnett.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/statnett/cimsparql.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
