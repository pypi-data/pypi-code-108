# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsp_exp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jsp-exp',
    'version': '0.1.31',
    'description': 'ジョブショップスケジューリング問題をpythonのクラスで表現',
    'long_description': None,
    'author': '鈴木貴大',
    'author_email': 'merioda.seven.24@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tkp0331/jsp-exp',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.9,<4.0.0',
}


setup(**setup_kwargs)
