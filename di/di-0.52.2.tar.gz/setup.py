# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['di', 'di._utils', 'di.api']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3,<4', 'graphlib2>=0.2.13']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3'],
 ':python_version < "3.9"': ['typing-extensions>=3']}

setup_kwargs = {
    'name': 'di',
    'version': '0.52.2',
    'description': 'Autowiring dependency injection',
    'long_description': '# `di`: pythonic dependency injection\n\n<p align="center">\n<a href="https://github.com/adriangb/di/actions?query=workflow%3ACI%2FCD+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/adriangb/di/actions/workflows/workflow.yaml/badge.svg?event=push&branch=main" alt="Test">\n</a>\n<a href="https://codecov.io/gh/adriangb/di" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/adriangb/di?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/di" target="_blank">\n    <img src="https://img.shields.io/pypi/v/di?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/di" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/di.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n`di` is a modern dependency injection system, modeled around the simplicity of FastAPI\'s dependency injection.\n\nKey features:\n\n- **Intuitive**: simple API, inspired by [FastAPI].\n- **Succinct**: declare what you want, and `di` figures out how to assemble it using type annotations.\n- **Scopes**: inspired by [pytest scopes], but defined by users (no fixed "request" or "session" scopes).\n- **Customizable**: decoupled internal APIs give you the flexibility to customize wiring and execution.\n- **Performant**: `di` can execute dependencies in parallel, move sync dependencies to threads and cache results. Performance critical parts are written in [🦀] via [graphlib2].\n\n## Installation\n\n```shell\npip install di\n```\n\n⚠️ This project is a work in progress. Until there is 1.X.Y release, expect breaking changes. ⚠️\n\n## Simple Example\n\nHere is a simple example of how `di` works:\n\n```python\nfrom dataclasses import dataclass\n\nfrom di import Container, Dependant, SyncExecutor\n\n\nclass A:\n    ...\n\n\nclass B:\n    ...\n\n\n@dataclass\nclass C:\n    a: A\n    b: B\n\n\ndef main():\n    container = Container(scopes=["request"])\n    solved = container.solve(Dependant(C, scope="request"))\n    with container.enter_scope("request"):\n        c = container.execute_sync(solved, executor=SyncExecutor())\n    assert isinstance(c, C)\n    assert isinstance(c.a, A)\n    assert isinstance(c.b, B)\n```\n\nFor more examples, see our [docs].\n\n### Why do I need dependency injection in Python? Isn\'t that a Java thing?\n\nDependency injection is a software architecture technique that helps us achieve [inversion of control] and [dependency inversion] (one of the five [SOLID] design principles).\n\nIt is a common misconception that traditional software design principles do not apply to Python.\nAs a matter of fact, you are probably using a lot of these techniques already!\n\nFor example, the `transport` argument to httpx\'s Client ([docs](https://www.python-httpx.org/advanced/#custom-transports)) is an excellent example of dependency injection. Pytest, arguably the most popular Python test framework, uses dependency injection in the form of [pytest fixtures].\n\nMost web frameworks employ inversion of control: when you define a view / controller, the web framework calls you! The same thing applies to CLIs (like [click]) or TUIs (like [Textual]). This is especially true for many newer web frameworks that not only use inversion of control but also dependency injection. Two great examples of this are [FastAPI] and [BlackSheep].\n\nFor a more comprehensive overview of Python projects related to dependency injection, see [Awesome Dependency Injection in Python].\n\n## Project Aims\n\nThis project aims to be a general dependency injection system, with a focus on providing the underlying dependency injection functionality for other libraries.\n\nIn other words, while you could use this as a standalone dependency injection framework, you may find it to be a bit terse and verbose. There are also much more mature standalone dependency injection frameworks; I would recommend at least looking into [python-dependency-injector] since it is currently the most popular / widely used of the bunch.\n\nFor more background, see our [docs].\n\n[🦀]: https://www.rust-lang.org\n[graphlib2]: https://github.com/adriangb/graphlib2\n[docs]: https://www.adriangb.com/di/\n[binds]: binds.md\n[dependency inversion]: https://en.wikipedia.org/wiki/Dependency_inversion_principle\n[SOLID]: https://en.wikipedia.org/wiki/SOLID\n[inversion of control]: https://en.wikipedia.org/wiki/Inversion_of_control\n[click]: https://click.palletsprojects.com/en/8.0.x/\n[Textual]: https://github.com/willmcgugan/textual\n[FastAPI]: https://fastapi.tiangolo.com/tutorial/dependencies/\n[BlackSheep]: https://www.neoteroi.dev/blacksheep/dependency-injection/\n[Awesome Dependency Injection in Python]: https://github.com/sfermigier/awesome-dependency-injection-in-python\n[python-dependency-injector]: https://github.com/ets-labs/python-dependency-injector\n[pytest scopes]: https://docs.pytest.org/en/6.2.x/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session\n[pytest fixtures]: https://docs.pytest.org/en/6.2.x/fixture.html\n\nSee this release on GitHub: [v0.52.2](https://github.com/adriangb/di/releases/tag/0.52.2)\n',
    'author': 'Adrian Garcia Badaracco',
    'author_email': 'adrian@adriangb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adriangb/di',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
