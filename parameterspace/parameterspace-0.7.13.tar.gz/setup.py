# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parameterspace',
 'parameterspace.parameters',
 'parameterspace.priors',
 'parameterspace.transformations']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17.0', 'scipy>=1.6.0']

setup_kwargs = {
    'name': 'parameterspace',
    'version': '0.7.13',
    'description': 'Parametrized hierarchical spaces with flexible priors and transformations.',
    'long_description': '# ParameterSpace\n\n**Contents:**\n\n- [About](#about)\n- [Installation](#installation)\n- [Development](#development)\n  - [Prerequisites](#prerequisites)\n  - [Setup environment](#setup-environment)\n  - [Running Tests](#running-tests)\n  - [Building Documentation](#building-documentation)\n- [License](#license)\n\n## About\n\nA package to define parameter spaces consisting of mixed types (continuous, integer,\ncategorical) with conditions and priors. It allows for easy specification of the\nparameters and their dependencies. The `ParameterSpace` object can then be used to\nsample random random configurations from the prior and convert any valid configuration\ninto a numerical representation. This numerical representation has the following\nproperties:\n\n- it results in a Numpy `ndarray` of type `numpy.float64`\n- transformed representation between 0 and 1 (uniform) including integers, ordinal and\n  categorical parameters\n- inactive parameters are masked as `numpy.nan` values\n\nThis allows to easily use optimizers that expect continuous domains to be used on more\ncomplicated problems because `parameterspace` can convert any numerical vector\nrepresentation inside the unit hypercube into a valid configuration. The function might\nnot be smooth, but for robust methods (like genetic algorithms/evolutionary strategies)\nthis might still be valuable.\n\nThis software is a research prototype. The software is not ready for production use. It\nhas neither been developed nor tested for a specific use case. However, the license\nconditions of the applicable Open Source licenses allow you to adapt the software to\nyour needs. Before using it in a safety relevant setting, make sure that the software\nfulfills your requirements and adjust it according to any applicable safety standards\n(e.g. ISO 26262).\n\n## Documentation\n\n**Visit [boschresearch.github.io/parameterspace](https://boschresearch.github.io/parameterspace/)**\n\n\n## Installation\n\nThe `parameterspace` package can be installed from [pypi.org](https://pypi.org):\n\n```\npip install parameterspace\n```\n\n## Development\n\n### Prerequisites\n\n- Python >= 3.7\n- [Poetry](https://python-poetry.org/docs/#installation)\n\n### Setup environment\n\nTo install the package and its dependencies for development run:\n\n```\npoetry install\n```\n\nOptionally install [pre-commit](https://pre-commit.com) hooks to check code standards\nbefore committing changes:\n\n```\npoetry run pre-commit install\n```\n\n### Running Tests\n\nThe tests are located in the `./tests` folder. The [pytest](https://pytest.org)\nframework is used for running them. To run the tests:\n\n```\npoetry run pytest ./tests\n```\n\n### Building Documentation\n\nTo built documentation run from the repository root:\n\n```\npoetry run mkdocs build --clean\n```\n\nFor serving it locally while working on the documentation run:\n\n```\npoetry run mkdocs serve\n```\n\n## License\n\n`parameterspace` is open-sourced under the Apache-2.0 license. See the\n[LICENSE](LICENSE) file for details.\n\nFor a list of other open source components included in `parameterspace`, see the file\n[3rd-party-licenses.txt](3rd-party-licenses.txt).\n',
    'author': 'Bosch Center for AI, Robert Bosch GmbH',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/boschresearch/parameterspace',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
