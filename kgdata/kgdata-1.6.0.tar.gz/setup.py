# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kgdata',
 'kgdata.dbpedia',
 'kgdata.misc',
 'kgdata.wikidata',
 'kgdata.wikidata.deprecated',
 'kgdata.wikidata.models',
 'kgdata.wikipedia']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'chardet>=4.0.0,<5.0.0',
 'cityhash>=0.2.3,<0.3.0',
 'click>=8.0.3,<9.0.0',
 'fastnumbers>=3.1.0,<4.0.0',
 'hugedict>=1.1.1,<1.2.0',
 'lbry-rocksdb-optimized>=0.8.1,<0.9.0',
 'loguru>=0.5.3,<0.6.0',
 'networkx>=2.6.3,<3.0.0',
 'numpy>=1.21.4,<2.0.0',
 'orjson>=3.6.4,<4.0.0',
 'parsimonious>=0.8.1,<0.9.0',
 'pyspark==3.0.3',
 'rdflib>=5.0.0,<6.0.0',
 'redis>=3.5.3,<4.0.0',
 'requests>=2.26.0,<3.0.0',
 'ruamel.yaml>=0.17.9,<0.18.0',
 'sem-desc>=3.0.0,<3.1.0',
 'six>=1.16.0,<2.0.0',
 'tqdm>=4.60.0,<5.0.0',
 'ujson>=4.0.2,<5.0.0']

entry_points = \
{'console_scripts': ['kgdata = kgdata.cli:cli']}

setup_kwargs = {
    'name': 'kgdata',
    'version': '1.6.0',
    'description': 'Library to process dumps of knowledge graphs (Wikipedia, DBpedia, Wikidata)',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
