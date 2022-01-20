# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['momba',
 'momba.analysis',
 'momba.debug',
 'momba.engine',
 'momba.gym',
 'momba.jani',
 'momba.kit',
 'momba.model',
 'momba.moml',
 'momba.tools',
 'momba.utils']

package_data = \
{'': ['*']}

install_requires = \
['immutables>=0.16,<0.17', 'mxu>=0.0.6,<0.0.7']

extras_require = \
{'all': ['click>=7.0,<8.0',
         'docker>=5.0.2,<6.0.0',
         'torch>=1.10.1,<2.0.0',
         'gym>=0.21.0,<0.22.0',
         'momba_engine==0.6.1'],
 'cli': ['click>=7.0,<8.0'],
 'docker': ['docker>=5.0.2,<6.0.0'],
 'engine': ['momba_engine==0.6.1'],
 'gym': ['torch>=1.10.1,<2.0.0', 'gym>=0.21.0,<0.22.0']}

entry_points = \
{'console_scripts': ['momba-moml = momba.moml.__main__:main']}

setup_kwargs = {
    'name': 'momba',
    'version': '0.6.1',
    'description': 'A Python library for quantitative models.',
    'long_description': '<p align="center">\n  <img src="https://raw.githubusercontent.com/koehlma/momba/master/docs/_static/images/logo_with_text.svg" alt="Momba Logo" width="200px">\n</p>\n\n<p align="center">\n  <a href="https://pypi.python.org/pypi/momba"><img alt="PyPi Package" src="https://img.shields.io/pypi/v/momba.svg?label=latest%20version"></a>\n  <a href="https://github.com/koehlma/momba/actions"><img alt="Tests" src="https://img.shields.io/github/workflow/status/koehlma/momba/Pipeline?label=tests"></a>\n  <a href="https://koehlma.github.io/momba/"><img alt="Docs" src="https://img.shields.io/static/v1?label=docs&message=master&color=blue"></a>\n  <a href="https://github.com/psf/black"><img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n  <a href="https://gitter.im/koehlma/momba?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge"><img alt="Gitter" src="https://badges.gitter.im/koehlma/momba.svg"></a>\n  <a href="https://doi.org/10.5281/zenodo.4519376"><img alt="DOI" src="https://zenodo.org/badge/DOI/10.5281/zenodo.4519376.svg"></a>\n</p>\n\n*Momba* is a Python framework for dealing with quantitative models centered around the [JANI-model](http://www.jani-spec.org/) interchange format.\nMomba strives to deliver an integrated and intuitive experience to aid the process of model construction, validation, and analysis.\nIt provides convenience functions for the modular construction of models effectively turning Python into a syntax-aware macro language for quantitative models.\nMomba\'s built-in exploration engine allows gaining confidence in a model, for instance, by rapidly prototyping a tool for interactive model exploration and visualization, or by connecting it to a testing framework.\nFinally, thanks to the JANI-model interchange format, several state-of-the-art model checkers and other tools are readily available for model analysis.\n\nPlease cite Momba as follows:\n\nMaximilian A. Köhl, Michaela Klauck, and Holger Hermanns: *Momba: JANI Meets Python*. In: J. F. Groote and K. G. Larsen (eds.) 27th International Conference on Tools and Algorithms for the Construction and Analysis of Systems, TACAS 2021. DOI: https://doi.org/10.1007/978-3-030-72013-1_23.\n\n\n## Features\n\n* first-class **import and export** of **JANI models**\n* **syntax-aware macros** for the modular construction of models with Python code\n* **built-in exploration engine** for PTAs, MDPs and other model types\n* interfaces to state-of-the-art model checkers, e.g., [The Modest Toolset](http://www.modestchecker.net/) and [Storm](https://www.stormchecker.org/)\n* pythonic and **statically typed** APIs to tinker with formal models\n* hassle-free out-of-the-box support for **Windows, Linux, and MacOS**\n\n\n## Getting Started\n\nMomba is available from the [Python Package Index](https://pypi.org/):\n```sh\npip install momba[all]\n```\nInstalling Momba with the `all` feature flag will install all optional dependencies unleashing the full power and all features of Momba.\nCheck out the [examples](https://koehlma.github.io/momba/examples) or read the [user guide](https://koehlma.github.io/momba/guide) to learn more.\n\nIf you aim at a fully reproducible modeling environment, we recommend using [Pipenv](https://pypi.org/project/pipenv/) or [Poetry](https://python-poetry.org/) for dependency management.\nWe also provide a [GitHub Template](https://github.com/koehlma/momba-pipenv-template) for Pipenv.\n\n\n## Rust Crates\n\nThe exploration engine of Momba is written in [Rust](https://rust-lang.org) levering [PyO3](https://pyo3.rs/) for Python bindings.\nIn case you are a Rust developer you might find some of the crates in [engine/crates](engine/crates) useful.\nIn particular, the crate [momba-explore](https://crates.io/crates/momba-explore) allows developing model analysis tools with JANI support in Rust based on Momba\'s explicit state space exploration engine.\nThe Rust command line tool [`momba-sidekick`](https://crates.io/crates/momba-sidekick) directly exposes some of this functionality.\n\n\n## Acknowledgements\n\nThis project is partially supported by the ERC Advanced Investigators Grant 695614 ([POWVER](https://powver.org)), by the German Research Foundation (DFG) under grant No. 389792660, as part of [TRR 248](https://perspicuous-computing.science), and by the Key-Area Research and Development Program Grant 2018B010107004 of Guangdong Province.\n\nThanks to Sarah Sterz for the awesome Momba logo.\n',
    'author': 'Maximilian Köhl',
    'author_email': 'koehl@cs.uni-saarland.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://koehlma.github.io/momba/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
