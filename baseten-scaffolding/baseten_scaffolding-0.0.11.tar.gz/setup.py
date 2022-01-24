# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['baseten_scaffolding',
 'baseten_scaffolding.definitions',
 'baseten_scaffolding.scaffold',
 'baseten_scaffolding.scaffold_templates',
 'baseten_scaffolding.scaffold_templates.common',
 'baseten_scaffolding.scaffold_templates.custom_server',
 'baseten_scaffolding.scaffold_templates.custom_server.server',
 'baseten_scaffolding.scaffold_templates.huggingface_transformer_server',
 'baseten_scaffolding.scaffold_templates.huggingface_transformer_server.server',
 'baseten_scaffolding.scaffold_templates.keras_server',
 'baseten_scaffolding.scaffold_templates.keras_server.server',
 'baseten_scaffolding.scaffold_templates.pytorch_server',
 'baseten_scaffolding.scaffold_templates.pytorch_server.server',
 'baseten_scaffolding.scaffold_templates.sklearn_server',
 'baseten_scaffolding.scaffold_templates.sklearn_server.server',
 'baseten_scaffolding.tests',
 'baseten_scaffolding.tests.common',
 'baseten_scaffolding.tests.definitions']

package_data = \
{'': ['*'],
 'baseten_scaffolding': ['docs/*'],
 'baseten_scaffolding.scaffold_templates': ['docker/*', 'docs/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'msgpack-numpy==0.4.7.1',
 'msgpack==1.0.2',
 'numpy>=1.18,<2.0',
 'packaging==20.9',
 'python-json-logger==2.0.2']

setup_kwargs = {
    'name': 'baseten-scaffolding',
    'version': '0.0.11',
    'description': '',
    'long_description': None,
    'author': 'Alex Gillmor',
    'author_email': 'alex@baseten.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
