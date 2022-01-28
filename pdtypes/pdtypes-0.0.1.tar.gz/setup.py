# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pdtypes']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.2,<2.0']

setup_kwargs = {
    'name': 'pdtypes',
    'version': '0.0.1',
    'description': 'Show data types for pandas data frames in terminal and notebooks',
    'long_description': '# pdtypes\n\nShow data types for pandas data frames in terminal and notebooks\n\n| Turn this | into |\n| --------- | ---- |\n| ![terminal_without_pdtypes][1] | ![terminal_with_pdtypes][2] |\n| ![terminal_without_pdtypes_gf][3] | ![terminal_with_pdtypes_gf][4] |\n| ![notebook_without_pdtypes][5] | ![notebook_with_pdtypes][6] |\n| ![notebook_without_pdtypes_gf][7] | ![notebook_with_pdtypes_gf][8] |\n\n\n\n## Installation\n```shell\npip install -U pdtypes\n```\n\n## Usage\n```python\n# Patching enabled by default\nimport pdtypes\n```\n\nTo disable patching (get everything back to what it was)\n```python\nimport pdtypes\n\n# ...\npdtypes.unpatch()\n\n# To patch again\npdtypes.patch()\n\n```\n\n\n[1]: docs/terminal_without_pdtypes.png\n[2]: docs/terminal_with_pdtypes.png\n[3]: docs/terminal_without_pdtypes_gf.png\n[4]: docs/terminal_with_pdtypes_gf.png\n[5]: docs/notebook_without_pdtypes.png\n[6]: docs/notebook_with_pdtypes.png\n[7]: docs/notebook_without_pdtypes_gf.png\n[8]: docs/notebook_with_pdtypes_gf.png\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/pdtypes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
