# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splitgraph',
 'splitgraph.cloud',
 'splitgraph.cloud.project',
 'splitgraph.commandline',
 'splitgraph.config',
 'splitgraph.core',
 'splitgraph.core.indexing',
 'splitgraph.core.sql',
 'splitgraph.engine',
 'splitgraph.engine.postgres',
 'splitgraph.hooks',
 'splitgraph.hooks.data_source',
 'splitgraph.ingestion',
 'splitgraph.ingestion.airbyte',
 'splitgraph.ingestion.csv',
 'splitgraph.ingestion.dbt',
 'splitgraph.ingestion.singer',
 'splitgraph.ingestion.singer.commandline',
 'splitgraph.ingestion.snowflake',
 'splitgraph.ingestion.socrata',
 'splitgraph.resources',
 'splitgraph.resources.icons',
 'splitgraph.resources.splitgraph_meta',
 'splitgraph.resources.static',
 'splitgraph.splitfile',
 'splitgraph.utils']

package_data = \
{'': ['*']}

install_requires = \
['asciitree>=0.3.3',
 'chardet>=4.0.0,<5.0.0',
 'click>=7,<8',
 'click_log>=0.3.2',
 'cryptography>=3.4.0',
 'docker>=5.0.2',
 'jsonschema>=3.1.0',
 'minio>=4',
 'packaging>=20.1',
 'parsimonious>=0.8,<0.9',
 'psycopg2-binary>=2,<3',
 'pydantic>=1.8.1',
 'requests>=2.22',
 'ruamel.yaml>=0.17.17,<0.18.0',
 'sodapy>=2.1',
 'splitgraph-pipelinewise-target-postgres>=2.1.0',
 'tabulate>=0.8.7',
 'tqdm>=4.46.0']

extras_require = \
{':sys_platform != "win32"': ['pglast==3.4'],
 'pandas': ['pandas[ingestion]>=0.24', 'sqlalchemy[ingestion]>=1.3,<1.4.23']}

entry_points = \
{'console_scripts': ['sgr = splitgraph.commandline:cli']}

setup_kwargs = {
    'name': 'splitgraph',
    'version': '0.3.4',
    'description': 'Command line library and Python client for Splitgraph, a version control system for data',
    'long_description': '# Splitgraph\n![Build status](https://github.com/splitgraph/splitgraph/workflows/build_all/badge.svg)\n[![Coverage Status](https://coveralls.io/repos/github/splitgraph/splitgraph/badge.svg?branch=master)](https://coveralls.io/github/splitgraph/splitgraph?branch=master)\n[![PyPI version](https://badge.fury.io/py/splitgraph.svg)](https://badge.fury.io/py/splitgraph)\n[![Discord chat room](https://img.shields.io/discord/718534846472912936.svg)](https://discord.gg/4Qe2fYA)\n[![Follow](https://img.shields.io/badge/twitter-@Splitgraph-blue.svg)](https://twitter.com/Splitgraph)\n\n## Overview\n\n**Splitgraph** is a tool for building, versioning and querying reproducible datasets. It\'s inspired\nby Docker and Git, so it feels familiar. And it\'s powered by [PostgreSQL](https://postgresql.org), so it [works seamlessly with existing tools](https://www.splitgraph.com/connect) in the Postgres ecosystem. Use Splitgraph to package your data into self-contained **data images** that you can [share with other Splitgraph instances](https://www.splitgraph.com/docs/getting-started/decentralized-demo).\n\n[**Splitgraph.com**](https://www.splitgraph.com), or **Splitgraph Cloud**, is a public Splitgraph instance where you can share and discover data. It\'s a Splitgraph peer powered by the **Splitgraph Core** code in this repository, adding proprietary features like a data catalog, multitenancy, and a distributed SQL proxy.\n\nYou can explore [40k+ open datasets](https://www.splitgraph.com/explore) in the catalog. You can also connect directly to the [Data Delivery Network](https://www.splitgraph.com/connect) and query any of the datasets, without installing anything.\n\nTo install `sgr` (the command line client) or a local Splitgraph Engine, see the [Installation](#installation) section of this readme.\n\n### Build and Query Versioned, Reproducible Datasets\n\n[**Splitfiles**](https://www.splitgraph.com/docs/concepts/splitfiles) give you a declarative language, inspired by Dockerfiles, for expressing data transformations in ordinary SQL familiar to any researcher or business analyst. You can reference other images, or even other databases, with a simple JOIN.\n\n![](pics/splitfile.png)\n\nWhen you build data with Splitfiles, you get provenance tracking of the resulting data: it\'s possible to find out what sources went into every dataset and know when to rebuild it if the sources ever change. You can easily integrate Splitgraph into your existing CI pipelines, to keep your data up-to-date and stay on top of changes to upstream sources.\n\nSplitgraph images are also version-controlled, and you can manipulate them with Git-like operations through a CLI. You can check out any image into a PostgreSQL schema and interact with it using any PostgreSQL client. Splitgraph will capture your changes to the data, and then you can commit them as delta-compressed changesets that you can package into new images.\n\nSplitgraph supports PostgreSQL [foreign data wrappers](https://wiki.postgresql.org/wiki/Foreign_data_wrappers). We call this feature [mounting](https://www.splitgraph.com/docs/concepts/mounting). With mounting, you can query other databases (like PostgreSQL/MongoDB/MySQL) or open data providers (like [Socrata](https://www.splitgraph.com/docs/ingesting-data/socrata)) from your Splitgraph instance with plain SQL. You can even snapshot the results or use them in Splitfiles.\n\n### Why Splitgraph?\n\nSplitgraph isn\'t opinionated and doesn\'t break existing abstractions. To any existing PostgreSQL application, Splitgraph images are just another database. We have carefully designed Splitgraph to not break the abstraction of a PostgreSQL table and wire protocol, because doing otherwise would mean throwing away a vast existing ecosystem of applications, users, libraries and extensions. This means that a lot of tools that work with PostgreSQL work with Splitgraph out of the box.\n\n![](pics/splitfiles.gif)\n\n## Components\n\nThe code in this repository, known as **Splitgraph Core**, contains:\n\n- **[`sgr` command line client](https://www.splitgraph.com/docs/architecture/sgr-client)**: `sgr` is the main command line tool used to work with Splitgraph "images" (data snapshots). Use it to ingest data, work with splitfiles, and push data to Splitgraph.com.\n- **[Splitgraph Engine](engine/README.md)**: a [Docker image](https://hub.docker.com/r/splitgraph/engine) of the latest Postgres with Splitgraph and other required extensions pre-installed.\n- **[Splitgraph Python library](https://www.splitgraph.com/docs/python-api/splitgraph.core)**: All Splitgraph functionality is available in the Python API, offering first-class support for data science workflows including Jupyter notebooks and Pandas dataframes.\n\n## Docs\n\nDocumentation is available at https://www.splitgraph.com/docs, specifically:\n\n- [Installation](https://www.splitgraph.com/docs/getting-started/installation)\n- [FAQ](https://www.splitgraph.com/docs/getting-started/frequently-asked-questions)\n\nWe also recommend reading our Blog, including some of our favorite posts:\n\n- [Supercharging `dbt` with Splitgraph: versioning, sharing, cross-DB joins](https://www.splitgraph.com/blog/dbt)\n- [Querying 40,000+ datasets with SQL](https://www.splitgraph.com/blog/40k-sql-datasets)\n- [Foreign data wrappers: PostgreSQL\'s secret weapon?](https://www.splitgraph.com/blog/foreign-data-wrappers)\n\n## Installation\n\nPre-requisites:\n\n- Docker is required to run the Splitgraph Engine. `sgr` must have access to Docker. You either need to [install Docker locally](https://docs.docker.com/install/) or have access to a remote Docker socket.\n\nFor Linux and OSX, once Docker is running, install Splitgraph with a single script:\n\n```\n$ bash -c "$(curl -sL https://github.com/splitgraph/splitgraph/releases/latest/download/install.sh)"\n```\n\nThis will download the `sgr` binary and set up the Splitgraph Engine Docker container.\n\nAlternatively, you can get the `sgr` single binary from [the releases page](https://github.com/splitgraph/splitgraph/releases) and run [`sgr engine add`](https://www.splitgraph.com/docs/sgr/engine-management/engine-add) to create an engine.\n\nSee the [installation guide](https://www.splitgraph.com/docs/getting-started/installation) for more installation methods.\n\n## Quick start guide\n\nYou can follow the [quick start guide](https://www.splitgraph.com/docs/getting-started/five-minute-demo) that will guide you through the basics of using Splitgraph with public and private data.\n\nAlternatively, Splitgraph comes with plenty of [examples](examples) to get you started.\n\nIf you\'re stuck or have any questions, check out the [documentation](https://www.splitgraph.com/docs/) or join our [Discord channel](https://discord.gg/4Qe2fYA)!\n\n## Contributing\n\n### Setting up a development environment\n\n  * Splitgraph requires Python 3.6 or later.\n  * Install [Poetry](https://github.com/python-poetry/poetry): `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python` to manage dependencies\n  * Install pre-commit hooks (we use [Black](https://github.com/psf/black) to format code)\n  * `git clone --recurse-submodules https://github.com/splitgraph/splitgraph.git`\n  * `poetry install`\n  * To build the [engine](https://www.splitgraph.com/docs/architecture/splitgraph-engine) Docker image: `cd engine && make`\n\n### Running tests\n\nThe test suite requires [docker-compose](https://github.com/docker/compose). You will also\nneed to add these lines to your `/etc/hosts` or equivalent:\n\n```\n127.0.0.1       local_engine\n127.0.0.1       remote_engine\n127.0.0.1       objectstorage\n```\n\nTo run the core test suite, do\n\n```\ndocker-compose -f test/architecture/docker-compose.core.yml up -d\npoetry run pytest -m "not mounting and not example"\n```\n\nTo run the test suite related to "mounting" and importing data from other databases\n(PostgreSQL, MySQL, Mongo), do\n\n```\ndocker-compose -f test/architecture/docker-compose.core.yml -f test/architecture/docker-compose.mounting.yml up -d\npoetry run pytest -m mounting\n```\n\nFinally, to test the [example projects](https://github.com/splitgraph/splitgraph/tree/master/examples), do\n\n```\n# Example projects spin up their own engines\ndocker-compose -f test/architecture/docker-compose.core.yml -f test/architecture/docker-compose.core.yml down -v\npoetry run pytest -m example\n```\n\nAll of these tests run in [CI](https://github.com/splitgraph/splitgraph/actions).\n',
    'author': 'Splitgraph Limited',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.splitgraph.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
