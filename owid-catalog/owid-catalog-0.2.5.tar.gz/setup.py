# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['owid', 'owid.catalog']

package_data = \
{'': ['*'], 'owid.catalog': ['schemas/*']}

install_requires = \
['dataclasses-json>=0.5.6,<0.6.0',
 'ipdb>=0.13.9,<0.14.0',
 'jsonschema>=3.2.0,<4.0.0',
 'pandas-stubs>=1.2.0,<2.0.0',
 'pandas>=1.3.3,<2.0.0',
 'pyarrow>=5.0.0,<6.0.0',
 'pytest-cov>=2.12.1,<3.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'owid-catalog',
    'version': '0.2.5',
    'description': 'Core data types used by OWID for managing data.',
    'long_description': '![build status](https://github.com/owid/owid-catalog-py/actions/workflows/python-package.yml/badge.svg)\n[![PyPI version](https://badge.fury.io/py/owid-catalog.svg)](https://badge.fury.io/py/owid-catalog)\n![](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue.svg)\n\n# owid-catalog\n\n_A Pythonic API for working with OWID\'s data catalog._\n\nStatus: experimental, APIs likely to change\n\n## Quickstart\n\nInstall with `pip install owid-catalog`. Then you can begin exploring the experimental data catalog:\n\n```python\nfrom owid import catalog\n\n# look for Covid-19 data, return a data frame of matches\ncatalog.find(\'covid\')\n\n# load Covid-19 data from the Our World In Data namespace as a data frame\ndf = catalog.find(\'covid\', namespace=\'owid\').load()\n```\n\n## Development\n\nYou need Python 3.9+, `poetry` and `make` installed. Clone the repo, then you can simply run:\n\n```\n# run all unit tests and CI checks\nmake test\n\n# watch for changes, then run all checks\nmake watch\n```\n\n## Data types\n\n### Catalog\n\nA catalog is an arbitrarily deep folder structure containing datasets inside. It can be local on disk, or remote.\n\n#### Load the remote catalog\n\n```python\n# find the default OWID catalog and fetch the catalog index over HTTPS\ncat = RemoteCatalog()\n\n# get a list of matching tables in different datasets\nmatches = cat.find(\'population\')\n\n# fetch a data frame for a specific match over HTTPS\nt = cat.find_one(\'population\', namespace=\'gapminder\')\n```\n\n### Datasets\n\nA dataset is a folder of tables containing metadata about the overall collection.\n\n- Metadata about the dataset lives in `index.json`\n- All tables in the folder must share a common format (CSV or Feather)\n\n#### Create a new dataset\n\n```python\n# make a folder and an empty index.json file\nds = Dataset.create(\'/tmp/my_data\')\n```\n\n```python\n# choose CSV instead of feather for files\nds = Dataset.create(\'/tmp/my_data\', format=\'csv\')\n```\n\n#### Add a table to a dataset\n\n```python\n# serialize a table using the table\'s name and the dataset\'s default format (feather)\n# (e.g. /tmp/my_data/my_table.feather)\nds.add(table)\n```\n\n#### Remove a table from a dataset\n\n```python\nds.remove(\'table_name\')\n```\n\n#### Access a table\n\n```python\n# load a table including metadata into memory\nt = ds[\'my_table\']\n```\n\n#### List tables\n\n```python\n# the length is the number of datasets discovered on disk\nassert len(ds) > 0\n```\n\n```python\n# iterate over the tables discovered on disk\nfor table in ds:\n    do_something(table)\n```\n\n#### Add metadata\n\n```python\n# you need to manually save your changes\nds.title = "Very Important Dataset"\nds.description = "This dataset is a composite of blah blah blah..."\nds.save()\n```\n\n#### Copy a dataset\n\n```python\n# copying a dataset copies all its files to a new location\nds_new = ds.copy(\'/tmp/new_data_path\')\n\n# copying a dataset is identical to copying its folder, so this works too\nshutil.copytree(\'/tmp/old_data\', \'/tmp/new_data_path\')\nds_new = Dataset(\'/tmp/new_data_path\')\n```\n### Tables\n\nTables are essentially pandas DataFrames but with metadata. All operations on them occur in-memory, except for loading from and saving to disk. On disk, they are represented by tabular file (feather or CSV) and a JSON metadata file.\n\n#### Make a new table\n\n```python\n# same API as DataFrames\nt = Table({\n    \'gdp\': [1, 2, 3],\n    \'country\': [\'AU\', \'SE\', \'CH\']\n}).set_index(\'country\')\n```\n\n#### Add metadata about the whole table\n\n```python\nt.title = \'Very important data\'\n```\n\n#### Add metadata about a field\n\n```python\nt.gdp.description = \'GDP measured in 2011 international $\'\nt.sources = [\n    Source(title=\'World Bank\', url=\'https://www.worldbank.org/en/home\')\n]\n```\n\n#### Add metadata about all fields at once\n\n```python\n# sources and licenses are actually stored a the field level\nt.sources = [\n    Source(title=\'World Bank\', url=\'https://www.worldbank.org/en/home\')\n]\nt.licenses = [\n    License(\'CC-BY-SA-4.0\', url=\'https://creativecommons.org/licenses/by-nc/4.0/\')\n]\n```\n\n#### Save a table to disk\n\n```python\n# save to /tmp/my_table.feather + /tmp/my_table.meta.json\nt.to_feather(\'/tmp/my_table.feather\')\n\n# save to /tmp/my_table.csv + /tmp/my_table.meta.json\nt.to_csv(\'/tmp/my_table.csv\')\n```\n\n#### Load a table from disk\n\nThese work like normal pandas DataFrames, but if there is also a `my_table.meta.json` file, then metadata will also get read. Otherwise it will be assumed that the data has no metadata:\n\n```python\nt = Table.read_feather(\'/tmp/my_table.feather\')\n\nt = Table.read_csv(\'/tmp/my_table.csv\')\n```\n\n\n## Changelog\n\n- `v0.2.5`\n    - Fix ability to load remote CSV tables\n- `v0.2.4`\n    - Update the default catalog URL to use a CDN\n- `v0.2.3`\n    - Fix methods for finding and loading data from a `LocalCatalog`\n- `v0.2.2`\n    - Repack frames to compact dtypes on `Table.to_feather()`\n- `v0.2.1`\n    - Fix key typo used in version check\n- `v0.2.0`\n    - Copy dataset metadata into tables, to make tables more traceable\n    - Add API versioning, and a requirement to update if your version of this library is too old\n- `v0.1.1`\n    - Add support for Python 3.8\n- `v0.1.0`\n    - Initial release, including searching and fetching data from a remote catalog\n',
    'author': 'Our World In Data',
    'author_email': 'tech@ourworldindata.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/owid/owid-grapher-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
