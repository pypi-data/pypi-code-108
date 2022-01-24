# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['json_codegen',
 'json_codegen.astlib',
 'json_codegen.generators',
 'json_codegen.generators.python3_marshmallow']

package_data = \
{'': ['*']}

install_requires = \
['astor>=0.7.1']

entry_points = \
{'console_scripts': ['json_codegen = json_codegen.cli.main:cli']}

setup_kwargs = {
    'name': 'json-codegen',
    'version': '0.4.6',
    'description': 'Generate code from JSON schema files.',
    'long_description': '[![Build Status](https://travis-ci.org/expobrain/json-schema-codegen.svg?branch=master)](https://travis-ci.org/expobrain/json-schema-codegen)\n\n# json-schema-codegen\n\nGenerate code from JSON schema files.\n\n# Table of contents\n\n- [Introduction](#introduction)\n- [Currently supported languages](#currently-supported-languages)\n- [Requirements](#requirements)\n- [Installation](#installation)\n- [Usage](#usage)\n- [Code generation](#code-generation)\n  - [Python2](#python-2)\n  - [Python3](#python-3)\n  - [Python3+Marshmallow](#python-3marshmallow)\n  - [JavaScript+Flow and Flow](#javascriptflow-and-flow)\n- [Contribute](#contribute)\n\n# Introduction\n\nThis is a command line tool to take a [json-schema](http://json-schema.org/) file and generate code automatically.\n\nFor instance this `json-schema` definition:\n\n```json\n{\n  "$schema": "http://json-schema.org/draft-04/schema#",\n  "title": "Test",\n  "type": "object",\n  "properties": {\n    "id": { "type": "integer" }\n  }\n}\n```\n\nwill generate this Python code:\n\n```python\nclass Test(object):\n    def __init__(self, data=None):\n        data = data or {}\n\n        self.id = data.get("id")\n```\n\nor this JavaScript+Flow code:\n\n```javascript\nexport class Test {\n  id: ?number;\n\n  constructor(data: Object = {}) {\n    this.id = data.id;\n  }\n}\n```\n\nCurrently this tool generates code for Python and JavaScript with [Flow](https://flow.org/) annotations but it can be extended to generate code for any language.\n\nThe code generation is divided in two stages:\n\n1.  generate the [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) for the target language from the `json-schema` file\n1.  convert the AST into the target language\n\nThis allows the tool to be language agnostic, that is it just needs to generate the AST in JSON format for the target language and then a language specific tool will convert this AST into proper code.\n\n# Currently supported languages\n\nList of currently supported languages:\n\n- Python 2.7+\n- JavaScript ES7+ with Flow annotations\n- pure Flow annotations\n\n# Requirements\n\n- Python 3.6 / 3.7\n- Node v12\n\n# Installation\n\nUntil this [pull request](https://github.com/pypa/setuptools/pull/1389) in [`setuptools`](https://pypi.org/project/setuptools/) is fixed, the only way to install `json-schema-codegen` is to clone the repo:\n\n```shell\ngit clone https://github.com/expobrain/json-schema-codegen.git\n```\n\n# Usage\n\n```shell\nusage: json_codegen.py [-h] [--prefix PREFIX] [--language LANGUAGE]\n                       [--output OUTPUT]\n                       schema\n\npositional arguments:\n  schema                Definition of the PRD as JSON schema\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --prefix PREFIX, -p PREFIX\n                        Optional prefix for generated classes\n  --language LANGUAGE, -l LANGUAGE\n                        Output language. Default is python\n  --output OUTPUT, -o OUTPUT\n                        Output filename for the generated code\n```\n\n# Code generation\n\n## Python 2\n\nThe generation of Python\'s code is integrated into the tool so it needs just a single invocation:\n\n```shell\njson_codegen --language python --output <output_py_file> <json-schema>\n```\n\n## Python 3\n\nThe egenerator of pure Python 3 compatible code:\n\n```shell\njson_codegen --language python3 --output <output_py_file> <json-schema>\n```\n\n## Python 3+Marshmallow\n\nThe generation of Python 3\'s code with [Marshmallow](https://marshmallow.readthedocs.io/en/2.x-line/) support is integrated into the tool so it needs just a single invocation:\n\n```shell\njson_codegen --language python3+marshmallow --output <output_py_file> <json-schema>\n```\n\n## JavaScript+Flow and Flow\n\nGenerating JavaScript+Flow and Flow code involves two steps, generating the AST:\n\n```shell\njson_codegen --language [javascript+flow|flow] --output <output_ast_json> <json-schema>\n```\n\nand generating the code from the AST:\n\n```shell\nbin/ast_to_js <output_ast_json> <output_js_file>\n```\n',
    'author': 'Daniele Esposti',
    'author_email': 'daniele.esposti@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<3.8',
}


setup(**setup_kwargs)
