# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tableauhyperio']

package_data = \
{'': ['*']}

install_requires = \
['black>=19.10b0',
 'flake8>=3.8.3',
 'pandas>=1.0.4',
 'tableauhyperapi>=0.0.10899',
 'tqdm>=4.46.1']

setup_kwargs = {
    'name': 'tableauhyperio',
    'version': '0.8.2',
    'description': 'Read and write Tableau hyper files using Pandas DataFrames',
    'long_description': '#DEPRECATED\n\nGo to https://github.com/innobi/pantab for a maintained package\n\n# Tableau Hyper IO: read and write Tableau hyper files using Pandas DataFrames\n[![PyPI](https://img.shields.io/pypi/v/tableauhyperio)](https://pypi.org/project/tableauhyperio)\n[![PyPI - License](https://img.shields.io/pypi/l/tableauhyperio)](https://github.com/AlexFrid/tableauhyperio/blob/master/LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## What is it?\nA simple way to read Tableau hyper files into Pandas DataFrames\nand write to Tableau hyper files from Pandas DataFrames.\n\n## Why was this made?\nFor a project I was working on I needed to read hyper files.\nI searched if a package already existed and found only the [pandleau](https://pypi.org/project/pandleau/) package,\nwhich only writes to hyper files but does not read them and also uses the older extract 2.0 API.\nSince I couldn\'t find any other package that met my needs I decided to make one myself, which has been a good learning experience.\n\n## Installation\n\nYou can install tableauhyperio using pip:\n```bash\npip install tableauhyperio\n```\nThis will also try downloading the Tableau hyper API, tqdm and pandas packages\nif you don\'t have them already.\n\n## Example usage\n```python\nimport tableauhyperio as hio\n\n# Reading a regular hyper file\ndf = hio.read_hyper("example.hyper")\n\n# Reading a hyper file with a custom schema\ndf = hio.read_hyper("example.hyper", "my_schema")\n\n# Writing a regular hyper file\nhio.to_hyper(df, "example_output.hyper")\n\n# Writing a hyper file with a custom schema and custom table name\nhio.to_hyper(df, "example_output.hyper", "my_schema", "my_table")\n```\n\n## Dependencies\n- [Pandas](https://pandas.pydata.org)\n- [tableauhyperapi](https://help.tableau.com/current/api/hyper_api/en-us/index.html)\n- [tqdm](https://github.com/tqdm/tqdm)\n',
    'author': 'Alexander Fridriksson',
    'author_email': 'post@alexanderfridriksson.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AlexFrid/tableauhyperio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
