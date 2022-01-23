# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hopscotch', 'hopscotch.fixtures', 'hopscotch.fixtures.init_caller_package']

package_data = \
{'': ['*']}

install_requires = \
['venusian>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'hopscotch',
    'version': '0.1.4',
    'description': 'Type-oriented registry with dependency injection.',
    'long_description': '# Hopscotch\n\n[![Coverage Status][codecov-badge]][codecov-link]\n[![Documentation Status][rtd-badge]][rtd-link]\n[![Code style: black][black-badge]][black-link]\n[![PyPI][pypi-badge]][pypi-link]\n[![Python Version][pypi-badge]][pypi-link]\n[![PyPI - Downloads][install-badge]][install-link]\n[![License][license-badge]][license-link]\n[![Test Status][tests-badge]][tests-link]\n[![pre-commit][pre-commit-badge]][pre-commit-link]\n[![black][black-badge]][black-link]\n\n[codecov-badge]: https://codecov.io/gh/pauleveritt/hopscotch/branch/main/graph/badge.svg\n[codecov-link]: https://codecov.io/gh/pauleveritt/hopscotch\n[rtd-badge]: https://readthedocs.org/projects/hopscotch/badge/?version=latest\n[rtd-link]: https://hopscotch.readthedocs.io/en/latest/?badge=latest\n[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg\n[black-link]: https://github.com/ambv/black\n[pypi-badge]: https://img.shields.io/pypi/v/hopscotch.svg\n[pypi-link]: https://pypi.org/project/hopscotch\n[install-badge]: https://img.shields.io/pypi/dw/hopscotch?label=pypi%20installs\n[install-link]: https://pypistats.org/packages/hopscotch\n[license-badge]: https://img.shields.io/pypi/l/hopscotch\n[license-link]: https://opensource.org/licenses/MIT\n[tests-badge]: https://github.com/pauleveritt/hopscotch/workflows/Tests/badge.svg\n[tests-link]: https://github.com/pauleveritt/hopscotch/actions?workflow=Tests\n[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n[pre-commit-link]: https://github.com/pre-commit/pre-commit\n\nWriting a decoupled application -- a "pluggable app" -- in Python is a common practice.\nLooking for a modern registry that scales from simple use, up to rich dependency injection (DI)?\n`hopscotch` is a registry and DI package for Python 3.9+, written to support research into component-driven development for Python\'s web story.\n\n```{admonition} Let\'s Be Real\nI expect a lot of skepticism.\nIn fact, I don\'t expect a lot of adoption.\nInstead, I\'m using this to learn and write articles.\n```\n\n## Features\n\n- _Simple to complex_. The easy stuff for a simple registry is easy, but rich, replaceable systems are in scope also.\n- _Better DX_. Improve developer experience through deep embrace of static analysis and usage of symbols instead of magic names.\n- _Hierarchical_. A cascade of parent registries helps model request lifecycles.\n- _Tested and documented_. High test coverage and quality docs with lots of (tested) examples.- _Extensible_.\n- _Great with components_. When used with [`viewdom`](https://viewdom.readthedocs.io), everything is wired up and you can just work in templates.\n\nHopscotch takes its history from `wired`, which came from `Pyramid`, which came from `Zope`.\n\n## Requirements\n\n- Python 3.9+.\n- venusian (for decorators)\n\n## Installation\n\nYou can install `Hopscotch` via [pip](https://pip.pypa.io/) from [PyPI](https://pypi.org/):\n\n```shell\n$ pip install hopscotch\n```\n\n## Quick Examples\n\nLet\'s look at: a hello world, same but with a decorator, replacement, and multiple choice.\n\nHere\'s a registry with one "kind of thing" in it:\n\n```python\n# One kind of thing\n@dataclass\nclass Greeter:\n    """A simple greeter."""\n\n    greeting: str = "Hello!"\n\n\nregistry = Registry()\nregistry.register(Greeter)\n# Later\ngreeter = registry.get(Greeter)\n# greeter.greeting == "Hello!"\n```\n\nThat\'s manual registration -- let\'s try with a decorator:\n\n```python\n@injectable()\n@dataclass\nclass Greeter:\n    """A simple greeter."""\n\n    greeting: str = "Hello!"\n\n\nregistry = Registry()\nregistry.scan()\n# Later\ngreeter = registry.get(Greeter)\n# greeter.greeting == "Hello!"\n```\n\nYou\'re building a pluggable app where people can replace builtins:\n\n```python\n# Some site might want to change a built-in.\n@injectable(kind=Greeter)\n@dataclass\nclass CustomGreeter:\n    """Provide a different ``Greeter`` in this site."""\n\n    greeting: str = "Howdy!"\n```\n\nSometimes you want a `Greeter` but sometimes you want a `FrenchGreeter` -- for example, based on the row of data a request is processing:\n\n```python\n@injectable(kind=Greeter, context=FrenchCustomer)\n@dataclass\nclass FrenchGreeter:\n    """Provide a different ``Greeter`` in this site."""\n\n    greeting: str = "Bonjour!"\n\n# Much later\nchild_registry = Registry(\n    parent=parent_registry,\n    context=french_customer\n)\ngreeter2 = child_registry.get(Greeter)\n# greeter2.greeting == "Bonjour!"\n```\n\nFinally, have your data constructed for you in rich ways, including custom field "operators":\n\n```python\n@injectable()\n@dataclass\nclass SiteConfig:\n    punctuation: str = "!"\n\n\n@injectable()\n@dataclass\nclass Greeter:\n    """A simple greeter."""\n\n    punctuation: str = get(SiteConfig, attr="punctuation")\n    greeting: str = "Hello"\n\n    def greet(self) -> str:\n        """Provide a greeting."""\n        return f"{self.greeting}{self.punctuation}"\n```\n\nThe full code for these examples are in the docs, with more explanation (and many more examples.)\n\nAnd don\'t worry, dataclasses aren\'t required.\nSome support is available for plain-old classes, `NamedTuple`, and even functions.\n\n# Contributing\n\nContributions are very welcome.\nTo learn more, see the [contributor\'s guide](contributing).\n\n# License\n\nDistributed under the terms of the [MIT license](https://opensource.org/licenses/MIT), _Hopscotch_ is free and open source software.\n\n# Issues\n\nIf you encounter any problems,\nplease [file an issue](https://github.com/pauleveritt/hopscotch/issues) along with a detailed description.\n\n# Credits\n\nThis project was generated from [@cjolowicz\'s](https://github.com/cjolowicz) [Hypermodern Python Cookiecutter](https://github.com/cjolowicz/cookiecutter-hypermodern-python) template.\n',
    'author': 'Paul Everitt',
    'author_email': 'pauleveritt@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pauleveritt/hopscotch',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.1,<4.0.0',
}


setup(**setup_kwargs)
