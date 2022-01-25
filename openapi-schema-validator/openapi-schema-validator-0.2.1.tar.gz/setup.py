# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openapi_schema_validator']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.0.0,<5.0.0']

extras_require = \
{'isodate': ['isodate'],
 'rfc3339-validator': ['rfc3339-validator'],
 'strict-rfc3339': ['strict-rfc3339']}

setup_kwargs = {
    'name': 'openapi-schema-validator',
    'version': '0.2.1',
    'description': 'OpenAPI schema validation for Python',
    'long_description': '************************\nopenapi-schema-validator\n************************\n\n.. image:: https://img.shields.io/pypi/v/openapi-schema-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-schema-validator\n.. image:: https://travis-ci.org/p1c2u/openapi-schema-validator.svg?branch=master\n     :target: https://travis-ci.org/p1c2u/openapi-schema-validator\n.. image:: https://img.shields.io/codecov/c/github/p1c2u/openapi-schema-validator/master.svg?style=flat\n     :target: https://codecov.io/github/p1c2u/openapi-schema-validator?branch=master\n.. image:: https://img.shields.io/pypi/pyversions/openapi-schema-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-schema-validator\n.. image:: https://img.shields.io/pypi/format/openapi-schema-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-schema-validator\n.. image:: https://img.shields.io/pypi/status/openapi-schema-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-schema-validator\n\nAbout\n#####\n\nOpenapi-schema-validator is a Python library that validates schema against the `OpenAPI Schema Specification v3.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#schemaObject>`__ which is an extended subset of the `JSON Schema Specification Wright Draft 00 <http://json-schema.org/>`__.\n\nInstallation\n############\n\nRecommended way (via pip):\n\n::\n\n    $ pip install openapi-schema-validator\n\nAlternatively you can download the code and install from the repository:\n\n.. code-block:: bash\n\n   $ pip install -e git+https://github.com/p1c2u/openapi-schema-validator.git#egg=openapi_schema_validator\n\n\nUsage\n#####\n\nSimple usage\n\n.. code-block:: python\n\n   from openapi_schema_validator import validate\n\n   # A sample schema\n   schema = {\n       "type" : "object",\n       "required": [\n          "name"\n       ],\n       "properties": {\n           "name": {\n               "type": "string"\n           },\n           "age": {\n               "type": "integer",\n               "format": "int32",\n               "minimum": 0,\n               "nullable": True,\n           },\n           "birth-date": {\n               "type": "string",\n               "format": "date",\n           }\n       },\n       "additionalProperties": False,\n   }\n\n   # If no exception is raised by validate(), the instance is valid.\n   validate({"name": "John", "age": 23}, schema)\n\n   validate({"name": "John", "city": "London"}, schema)\n\n   Traceback (most recent call last):\n       ...\n   ValidationError: Additional properties are not allowed (\'city\' was unexpected)\n\nYou can also check format for primitive types\n\n.. code-block:: python\n\n   from openapi_schema_validator import oas30_format_checker\n\n   validate({"name": "John", "birth-date": "-12"}, schema, format_checker=oas30_format_checker)\n\n   Traceback (most recent call last):\n       ...\n   ValidationError: \'-12\' is not a \'date\'\n\n\nRelated projects\n################\n* `openapi-core <https://github.com/p1c2u/openapi-core>`__\n   Python library that adds client-side and server-side support for the OpenAPI.\n* `openapi-spec-validator <https://github.com/p1c2u/openapi-spec-validator>`__\n   Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger) and OpenAPI 3.0 specification\n',
    'author': 'Artur Maciag',
    'author_email': 'maciag.artur@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/p1c2u/openapi-schema-validator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
