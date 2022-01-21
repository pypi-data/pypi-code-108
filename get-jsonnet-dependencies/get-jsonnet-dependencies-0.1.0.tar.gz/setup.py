# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['get_jsonnet_dependencies']
entry_points = \
{'console_scripts': ['get-jsonnet-dependencies = '
                     'get_jsonnet_dependencies:main']}

setup_kwargs = {
    'name': 'get-jsonnet-dependencies',
    'version': '0.1.0',
    'description': 'Extracts import dependencies from a Jsonnet file',
    'long_description': '# get-jsonnet-dependencies\n\nExtracts import dependencies from a Jsonnet file\n\n## Usage\n\n```sh\n> pip install get-jsonnet-dependencies\n> get-jsonnet-dependencies -\n> local thing = import "thing.jsonnet";\nthing.jsonnet\n> local amoguise = import @"C:\\Users\\sus\\Documents\\amoguise.libsonnet";\nC:\\Users\\sus\\Documents\\amoguise.libsonnet\n> local a = import "a.jsonnet"; local b = importstr "b.txt";\na.jsonnet\nb.txt\n```\n\nPass a list of files to extract dependencies from\n\nPassing - means to take extract dependencies from stdin\n\nNo arguments means `get-jsonnet-dependencies -`\n\nNote that imports spanning multiple lines won\'t be found by this script\n',
    'author': 'George Zhang',
    'author_email': 'geetransit@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/get-jsonnet-dependencies/',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
