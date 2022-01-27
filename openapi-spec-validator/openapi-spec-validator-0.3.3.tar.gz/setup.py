# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openapi_spec_validator', 'openapi_spec_validator.handlers']

package_data = \
{'': ['*'],
 'openapi_spec_validator': ['resources/schemas/v2.0/*',
                            'resources/schemas/v3.0.0/*',
                            'resources/schemas/v3.0/*']}

install_requires = \
['PyYAML>=5.1',
 'jsonschema>=3.2.0,<4.0.0',
 'openapi-schema-validator<0.2.0',
 'pyrsistent<0.17.0',
 'setuptools',
 'six']

extras_require = \
{':python_version >= "2.7" and python_version < "2.8"': ['pathlib2'],
 'requests': ['requests']}

entry_points = \
{'console_scripts': ['openapi-spec-validator = '
                     'openapi_spec_validator.__main__:main']}

setup_kwargs = {
    'name': 'openapi-spec-validator',
    'version': '0.3.3',
    'description': 'OpenAPI 2.0 (aka Swagger) and OpenAPI 3.0 spec validator',
    'long_description': "**********************\nOpenAPI Spec validator\n**********************\n\n.. image:: https://img.shields.io/pypi/v/openapi-spec-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-spec-validator\n.. image:: https://travis-ci.org/p1c2u/openapi-spec-validator.svg?branch=master\n     :target: https://travis-ci.org/p1c2u/openapi-spec-validator\n.. image:: https://img.shields.io/codecov/c/github/p1c2u/openapi-spec-validator/master.svg?style=flat\n     :target: https://codecov.io/github/p1c2u/openapi-spec-validator?branch=master\n.. image:: https://img.shields.io/pypi/pyversions/openapi-spec-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-spec-validator\n.. image:: https://img.shields.io/pypi/format/openapi-spec-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-spec-validator\n.. image:: https://img.shields.io/pypi/status/openapi-spec-validator.svg\n     :target: https://pypi.python.org/pypi/openapi-spec-validator\n\nAbout\n#####\n\nOpenAPI Spec Validator is a Python library that validates OpenAPI Specs\nagainst the `OpenAPI 2.0 (aka\nSwagger) <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md>`__\nand `OpenAPI\n3.0 <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md>`__\nspecification. The validator aims to check for full compliance with the\nSpecification.\n\nInstallation\n############\n\n::\n\n    $ pip install openapi-spec-validator\n\nAlternatively you can download the code and install from the repository:\n\n.. code-block:: bash\n\n   $ pip install -e git+https://github.com/p1c2u/openapi-spec-validator.git#egg=openapi_spec_validator\n\n\nUsage\n#####\n\nCommand Line Interface\n**********************\n\nStraight forward way:\n\n.. code:: bash\n\n    $ openapi-spec-validator openapi.yaml\n\npipes way:\n\n.. code:: bash\n\n    $ cat openapi.yaml | openapi-spec-validator -\n\ndocker way:\n\n.. code:: bash\n\n    $ docker run -v path/to/openapi.yaml:/openapi.yaml --rm p1c2u/openapi-spec-validator /openapi.yaml\n\nor more pythonic way:\n\n.. code:: bash\n\n    $ python -m openapi_spec_validator openapi.yaml\n\nExamples\n********\n\nBy default, OpenAPI v3 syntax is expected. To validate an OpenAPI v3 spec:\n\n.. code:: python\n\n    from openapi_spec_validator import validate_spec\n    from openapi_spec_validator.readers import read_from_filename\n\n    spec_dict, spec_url = read_from_filename('openapi.yaml')\n\n    # If no exception is raised by validate_spec(), the spec is valid.\n    validate_spec(spec_dict)\n\n    validate_spec({})\n\n    Traceback (most recent call last):\n        ...\n    OpenAPIValidationError: 'openapi' is a required property\n    \nIn order to validate a Swagger / OpenAPI 2.0 spec file, import ``validate_v2_spec`` instead of ``validate_spec``. You can also explicitly import ``validate_v3_spec`` if you want to disambiguate the expected version.\n\nAdd ``spec_url`` to validate spec with relative files:\n\n.. code:: python\n\n    validate_spec(spec_dict, spec_url='file:///path/to/spec/openapi.yaml')\n\nYou can also validate spec from url:\n\n.. code:: python\n\n    from openapi_spec_validator import validate_spec_url\n\n    # If no exception is raised by validate_spec_url(), the spec is valid.\n    validate_spec_url('http://example.com/openapi.json')\n\nIf you want to iterate through validation errors:\n\n.. code:: python\n\n    from openapi_spec_validator import openapi_v3_spec_validator\n\n    errors_iterator = openapi_v3_spec_validator.iter_errors(spec)\n\nRelated projects\n################\n\n* `openapi-core <https://github.com/p1c2u/openapi-core>`__\n   Python library that adds client-side and server-side support for the OpenAPI.\n* `openapi-schema-validator <https://github.com/p1c2u/openapi-schema-validator>`__\n   Python library that validates schema against the OpenAPI Schema Specification v3.0.\n\nLicense\n#######\n\nCopyright (c) 2017-2021, Artur Maciag, All rights reserved. Apache v2\n",
    'author': 'Artur Maciag',
    'author_email': 'maciag.artur@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/p1c2u/openapi-spec-validator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
