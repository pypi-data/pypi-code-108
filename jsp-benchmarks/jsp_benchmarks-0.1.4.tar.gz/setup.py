# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsp_benchmarks']

package_data = \
{'': ['*'], 'jsp_benchmarks': ['instances/*']}

install_requires = \
['jsp-exp>=0.1.31,<0.2.0']

setup_kwargs = {
    'name': 'jsp-benchmarks',
    'version': '0.1.4',
    'description': 'ジョブショップスケジューリング問題のベンチマーク問題をpythonのクラスで表現し，load出来るようにする',
    'long_description': None,
    'author': '鈴木貴大',
    'author_email': 'merioda.seven.24@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tkp0331/jsp-benckmarks',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
