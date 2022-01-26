# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['util',
 'util.algorithm',
 'util.annotations',
 'util.atomic',
 'util.awsgi',
 'util.awsgi.launcher',
 'util.config',
 'util.digraph',
 'util.digraph.algorithm',
 'util.fs',
 'util.function',
 'util.generic',
 'util.git',
 'util.io',
 'util.keyvalue',
 'util.parsing',
 'util.parsing._tokenizer',
 'util.plugins',
 'util.process',
 'util.proxy',
 'util.safearg',
 'util.singleton',
 'util.task',
 'util.weak']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nr.util',
    'version': '0.4.7',
    'description': 'General purpose Python utility library.',
    'long_description': '# nr.util\n\nGeneral purpose Python utility library.\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
