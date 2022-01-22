# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dotwarden']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dotwarden',
    'version': '1.0.4',
    'description': 'a utility for generating hidden random . directories',
    'long_description': '# dotwarden\na python package for generating . directories\n\n```python\nfrom dotwarden import Dotwarden\n\nif __name__ == "__main__":\n  dw = Dotwarden()\n  input(dw.warden_dir)\n```\n',
    'author': 'Jaffar',
    'author_email': 'jaffar.almaleki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JaffarA/dotwarden',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
