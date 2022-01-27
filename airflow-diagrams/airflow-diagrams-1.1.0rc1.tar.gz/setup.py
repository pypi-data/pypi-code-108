# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['airflow_diagrams']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'apache-airflow-client>=2.2.0,<3.0.0',
 'diagrams>=0.20.0,<0.21.0',
 'thefuzz[speedup]>=0.19.0,<0.20.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['airflow-diagrams = airflow_diagrams.cli:app']}

setup_kwargs = {
    'name': 'airflow-diagrams',
    'version': '1.1.0rc1',
    'description': 'Auto-generated Diagrams from Airflow DAGs.',
    'long_description': "# airflow-diagrams\n\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/feluelle/airflow-diagrams/master.svg)](https://results.pre-commit.ci/latest/github/feluelle/airflow-diagrams/master)\n![test workflow](https://github.com/feluelle/airflow-diagrams/actions/workflows/test.yml/badge.svg)\n[![codecov](https://codecov.io/gh/feluelle/airflow-diagrams/branch/master/graph/badge.svg?token=J8UEP8IVY4)](https://codecov.io/gh/feluelle/airflow-diagrams)\n[![PyPI version](https://img.shields.io/pypi/v/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)\n[![License](https://img.shields.io/pypi/l/airflow-diagrams)](https://github.com/feluelle/airflow-diagrams/blob/master/LICENSE)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/airflow-diagrams)](https://pypi.org/project/airflow-diagrams/)\n\n> Auto-generated Diagrams from Airflow DAGs.\n\nThis project aims to easily visualise your [Airflow](https://github.com/apache/airflow) DAGs on service level\nfrom providers like AWS, GCP, Azure, etc. via [diagrams](https://github.com/mingrammer/diagrams).\n\n## 🚀 Get started\n\nTo install it from [PyPI](https://pypi.org/) run:\n```\npip install airflow-diagrams\n```\n> **_NOTE:_** Make sure you have [Graphviz](https://www.graphviz.org/) installed.\n\nThen just call it like this:\n```\nUsage: airflow-diagrams generate [OPTIONS]\n\n  Generates <airflow-dag-id>_diagrams.py in <output-path> directory which\n  contains the definition to create a diagram. Run this file and you will get\n  a rendered diagram.\n\nOptions:\n  -d, --airflow-dag-id TEXT    The dag id from which to generate the diagram.\n                               By default it generates for all.\n  -h, --airflow-host TEXT      The host of the airflow rest api from where to\n                               retrieve the dag tasks information.  [default:\n                               http://localhost:8080/api/v1]\n  -u, --airflow-username TEXT  The username of the airflow rest api.\n                               [default: admin]\n  -p, --airflow-password TEXT  The password of the airflow rest api.\n                               [default: admin]\n  -o, --output-path DIRECTORY  The path to output the diagrams to.  [default:\n                               .]\n  -m, --mapping-file FILE      The mapping file to use for static mapping from\n                               Airflow task to diagram node. By default no\n                               mapping file is being used.\n  -v, --verbose                Verbose output i.e. useful for debugging\n                               purposes.\n  --help                       Show this message and exit.\n```\n_Examples of generated diagrams can be found in the [examples](examples) directory._\n\n## 🤔 How it Works\n\nℹ️ At first it connects, by using the official [Apache Airflow Python Client](https://github.com/apache/airflow-client-python), to your Airflow installation to retrieve all DAGs (in case you don't specify any `dag_id`) and all Tasks for the DAG(s).\n\n🔮 Then it tries to find a diagram node for every DAGs task, by using [Fuzzy String Matching](https://github.com/seatgeek/thefuzz), that matches the most. If you are unhappy about the match you can also provide a `mapping.yml` file to statically map from Airflow task to diagram node.\n\n🪄 Lastly it renders the results into a python file which can then be executed to retrieve the rendered diagram. 🎉\n\n## ❤️ Contributing\n\nContributions are very welcome. Please go ahead and raise an issue if you have one or open a PR. Thank you.\n",
    'author': 'Felix Uellendall',
    'author_email': 'feluelle@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
