# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['thriftpyi', 'thriftpyi.templates']

package_data = \
{'': ['*']}

install_requires = \
['autoflake>=1.3,<2.0',
 'black>=19.3b0,<20.0',
 'click>=7.0,<8.0',
 'jinja2>=2.10,<3.0',
 'thriftpy2>=0.4.2,<0.5.0']

entry_points = \
{'console_scripts': ['thriftpyi = thriftpyi.cli:main']}

setup_kwargs = {
    'name': 'thrift-pyi',
    'version': '0.3.0',
    'description': 'This is simple `.pyi` stubs generator from thrift interfaces',
    'long_description': '========\nOverview\n========\n\n.. start-badges\n\n.. image:: https://github.com/unmade/thrift-pyi/workflows/lint%20and%20test/badge.svg?branch=master\n    :alt: Build Status\n    :target: https://github.com/unmade/thrift-pyi/blob/master/.github/workflows/lint-and-test.yml\n\n.. image:: https://codecov.io/github/unmade/thrift-pyi/coverage.svg?branch=master\n    :alt: Coverage Status\n    :target: https://codecov.io/github/unmade/thrift-pyi\n\n.. image:: https://api.codacy.com/project/badge/Grade/487480f045594e148309e8b7f1f71351\n    :alt: Codacy Badge\n    :target: https://app.codacy.com/app/unmade/thrift-pyi\n\n.. image:: https://requires.io/github/unmade/thrift-pyi/requirements.svg?branch=master\n    :alt: Requirements Status\n    :target: https://requires.io/github/unmade/thrift-pyi/requirements/?branch=master\n\n.. image:: https://img.shields.io/pypi/v/thrift-pyi.svg\n    :alt: PyPI Package latest release\n    :target: https://pypi.org/project/thrift-pyi\n\n.. image:: https://img.shields.io/pypi/wheel/thrift-pyi.svg\n    :alt: PyPI Wheel\n    :target: https://pypi.org/project/thrift-pyi\n\n.. image:: https://img.shields.io/pypi/pyversions/thrift-pyi.svg\n    :alt: Supported versions\n    :target: https://pypi.org/project/thrift-pyi\n\n.. image:: https://img.shields.io/badge/License-MIT-purple.svg\n    :alt: MIT License\n    :target: https://github.com/unmade/thrift-pyi/blob/master/LICENSE\n\n.. end-badges\n\nThis is simple `.pyi` stubs generator from thrift interfaces.\nMotivation for this project is to have autocomplete and type checking\nfor dynamically loaded thrift interfaces\n\nInstallation\n============\n\n.. code-block:: bash\n\n    pip install thrift-pyi\n\nQuickstart\n==========\n\nSample usage:\n\n.. code-block:: bash\n\n    $ thriftpyi example/interfaces --output example/app/interfaces\n\nAdditionally to generated stubs you might want to create `__init__.py` that will load thrift interfaces, for example:\n\n.. code-block:: python\n\n    from pathlib import Path\n    from types import ModuleType\n    from typing import Dict\n\n    import thriftpy2\n\n    _interfaces_path = Path("example/interfaces")\n    _interfaces: Dict[str, ModuleType] = {}\n\n\n    def __getattr__(name):\n        try:\n            return _interfaces[name]\n        except KeyError:\n            interface = thriftpy2.load(str(_interfaces_path.joinpath(f"{name}.thrift")))\n            _interfaces[name] = interface\n            return interface\n\n\nTo see more detailed example of usage refer to `example app <https://github.com/unmade/thrift-pyi/blob/master/example>`_\n\n--strict-optional\n-----------------\n\nPython and thrift are very different at argument handling.\nFor example in thrift the following will be correct declaration:\n\n.. code-block:: thrift\n\n    struct TodoItem {\n        1: required i32 id\n        3: optional i32 type = 1\n        2: required string text\n    }\n\nIn python attributes without a default cannot follow attributes with one.\nTherefore by default all fields are optional with default to None. This is compliant\nto `thriftpy2 <https://github.com/Thriftpy/thriftpy2>`_.\n\nHowever, if you want more strict behaviour you can specify `--strict-optional` option.\nFor the case above, the following stubs will be generated:\n\n.. code-block:: python\n\n    from dataclasses import dataclass\n\n    @dataclass\n    class TodoItem:\n        id: int\n        type: int = 1\n        text: str\n\nDevelopment\n===========\n\nTo install pre-commit hooks::\n\n    pre-commit install\n\nTo run the all tests run::\n\n    tox\n',
    'author': 'Aleksei Maslakov',
    'author_email': 'lesha.maslakov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/unmade/thrift-pyi',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
