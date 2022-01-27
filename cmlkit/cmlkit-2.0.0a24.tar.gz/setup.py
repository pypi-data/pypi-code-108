# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cmlkit',
 'cmlkit.dataset',
 'cmlkit.engine',
 'cmlkit.engine.cache',
 'cmlkit.engine.data',
 'cmlkit.evaluation',
 'cmlkit.evaluation.loss',
 'cmlkit.regression',
 'cmlkit.regression.qmml',
 'cmlkit.representation',
 'cmlkit.representation.mbtr',
 'cmlkit.representation.sf',
 'cmlkit.representation.soap',
 'cmlkit.tune',
 'cmlkit.tune.evaluators',
 'cmlkit.tune.run',
 'cmlkit.tune.search',
 'cmlkit.utility']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0',
 'ase>=3.18',
 'dill>=0.2,<0.3',
 'hyperopt>=0.1.2,<0.2.0',
 'joblib>=0.13,<0.14',
 'numpy>=1.16,<2.0',
 'pebble<=4.3.10',
 'son>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'cmlkit',
    'version': '2.0.0a24',
    'description': 'Machine learning tools for computational chemistry and condensed matter physics',
    'long_description': '# cmlkit 🐫🧰\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cmlkit.svg) [![PyPI](https://img.shields.io/pypi/v/cmlkit.svg)](https://pypi.org/project/cmlkit/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black) \n\nPublications: [`repbench`: Langer, Gößmann, Rupp (2020)](https://marcel.science/repbench)\n\nPlugins: [`cscribe 🐫🖋️`](https://github.com/sirmarcel/cscribe) | [`mortimer 🎩⏰`](https://gitlab.com/sirmarcel/mortimer) | [`skrrt 🚗💨`](https://gitlab.com/sirmarcel/skrrt)\n\n***\n\n`cmlkit` is an extensible `python` package providing clean and concise infrastructure to specify, tune, and evaluate machine learning models for computational chemistry and condensed matter physics. Intended as a common foundation for more specialised systems, not a monolithic user-facing tool, it wants to help you build your own tools! ✨\n\n*If you use this code in any scientific work, please mention it in the publication, cite [the paper](https://marcel.science/repbench) and let me know. Thanks! 🐫*\n\n## What exactly is `cmlkit`?\n\n[💡 A tutorial introduction to `cmlkit` courtesy of the NOMAD Analytics Toolkit 💡](https://www.nomad-coe.eu/index.php?page=bigdata-analyticstoolkit)\n\n*Sidenote*: If you\'ve come across this from outside the "ML for materials and chemistry" world, this will unfortunately be of limited use for you! However, if you\'re interested in ML infrastructure in general, please take a look at `engine` and `tune`, which are not specific to this domain and might be of interest.\n\n### Features\n\n- Reasonably clean, composable, modern codebase with little magic ✨\n\n#### Representations\n\n`cmlkit` provides a unified interface for:\n\n- Many-Body Tensor Representation by [Huo, Rupp (2017)](https://arxiv.org/abs/1704.06439) (`qmmlpack` and `dscribe` implementation)\n- Smooth Overlap of Atomic Positions representaton by [Bartók, Kondor, Csányi (2013)](https://doi.org/10.1103/PhysRevB.87.184115) (`quippy`‡ and `dscribe` implementations)\n- Symmetry Functions representation by [Behler (2011)](https://doi.org/10.1063/1.3553717) (`RuNNer` and `dscribe` implementation), with a semi-automatic parametrisation scheme taken from [Gastegger et al. (2018)](https://doi.org/10.1063/1.5019667).\n\n‡ The `quippy` interface was written for an older version that didn\'t support `python3`.\n\n#### Regression methods\n\n- Kernel Ridge Regression as implemented in [`qmmlpack`](https://gitlab.com/qmml/qmmlpack) (supporting both global and local/atomic representations)\n\n#### Hyper-parameter tuning\n\n- Robust multi-core support (i.e. it can automatically kill timed out external code, even if it ignores `SIGTERM`)\n- No `mongodb` required\n- Extensions to the `hyperopt` priors (uniform `log` grids)\n- Resumable/recoverable runs backed by a readable, atomically written history of the optimisation (backed by [`son`](https://github.com/flokno/son))\n- Search spaces can be defined entirely in text, i.e. they\'re easily writeable, portable and serialisable\n- Possibility to implement multi-step optimisation (experimental at the moment)\n- Extensible with custom loss functions or training loops\n\n#### Various\n\n- Automated loading of datasets by name\n- Seamless conversion of properties into per-atom or per-system quantities. Models can do this automatically!\n- Plugin system! ☢️ Isolate one-off nightmares! ☢️\n- Canonical, stable hashes of models and datasets!\n- Automatically train models and compute losses!\n\n### But what... is it?\n\nAt its core, `cmlkit` defines a unified `dict`-based format to specify model components, which can be straightforwardly read and written as `yaml`. Model components are implemented as pure-ish functions, which is conceptually satisfying and opens the door to easy pipelining and caching. Using this format, `cmlkit` provides interfaces to many representations and a fast kernel ridge regression implementation.\n\nHere is an example for a SOAP+KRR model:\n\n```yaml\nmodel:\n  per: cell\n  regression:\n    krr:               # regression method: kernel ridge regression\n      kernel:\n        kernel_atomic: # soap is a local representation, so we use the appropriate kernel\n          kernelf:\n            gaussian:  # gaussian kernel\n              ls: 80   # ... with length scale 80\n      nl: 1.0e-07      # regularisation parameter\n  representation:\n    ds_soap:           # SOAP representation (dscribe implementation via plugin)\n      cutoff: 3\t\n      elems: [8, 13, 31, 49]\n      l_max: 8\n      n_max: 2\n      sigma: 0.5\n```\n\nHaving a canonical model format allows `cmlkit` to provide a quite pleasant interface to `hyperopt`. The same mechanism *also* enables a simple plugin system, making `cmlkit` easily exensible, so you can isolate one-off task-specific code into separate projects without any problems, while making use of a solid, if opionated, foundation.\n\nFor a gentle, detailed tour please [check out the tutorial]( https://www.nomad-coe.eu/index.php?page=bigdata-analyticstoolkit ).\n\n### Caveats 😬\n\nOkay then, what are the rough parts?\n\n- `cmlkit` is very inconvenient for interactive and non-automated use: Models cannot be saved and caching is not enabled yet, so all computations (representation, kernel matrices, etc.) must be re-run from scratch upon restart. This is not a problem during HP optimisation, as there the point is to try *different* models, but it is annoying for exploring a single model in detail. Fixing this is an *active* consideration, though! After all, the code is written with caching in mind.\n- `cmlkit` is and will remain "scientific research software", i.e. it is prone to somewhat haphazard development practices and periods of hibernation. I\'ll do my best to avoid breaking changes and abandonement, but you know how it is!\n- `cmlkit` is currently in an "alpha" state. While it\'s pretty stable and well-tested for some specific usecases (like writing a [large-scale benchmarking paper](https://marcel.science/repbench)), it\'s not tested for more everyday use. There\'s also some internal loose ends that need to be tied up.\n- `cmlkit` is not particularly user friendly at the moment, and expects its users to be python developers. See below for notes on documentation! 😀\n\n## Installation and friends\n\n`cmlkit` is available via pip:\n\n```\npip install cmlkit\n```\n\nYou can also clone this repository! I\'d suggest having a look into the codebase in any case, as there is currently no external documentation.\n\nIf you want to do any "real" work with `cmlkit`, you\'ll need to install [`qmmlpack`](https://gitlab.com/qmml/qmmlpack/-/tree/development) **on the development branch**. It\'s fairly straightforward!\n\n***\n\nIn order to compute representations with `dscribe`, you should install the [`cscribe`](https://github.com/sirmarcel/cscribe) plugin:\n\n```\npip install cscribe\n```\nYou need to also export `CML_PLUGINS=cscribe`.\n\nTo setup the `quippy` and `RuNNer` interface please consult the readmes in `cmlkit/representation/soap` and `cmlkit/representation/sf`.\n\n***\n\nFor details on environment variables and such things, please consult the readme in the `cmlkit` folder.\n\n## "Frequently" Asked Questions\n\n### Where is the documentation?\n\nAt the moment, I don\'t think it\'s feasible for me to maintain separate written docs, and I believe that purely auto-generated docs are basically a worse version of just looking at the formatted source on Github or in your text editor. So I *highly* encourage to take a look there!\n\nMost submodules in `cmlkit` have their own `README.md` documenting what\'s going on in them, and all "outside facing" classes have extensive docstrings. I hope that\'s sufficient! Please feel free to file an issue if you have any questions.\n\n### I don\'t work in computational chemistry/condensed matter physics. Should I care?\n\nThe short answer is regrettably probably no. \n\nHowever, I think the architecture of this library is quite neat, so maybe it can provide some marginally interesting reading. The `tune` component is very general and provides, in my opinion, a delightfully clean interface to `hyperopt`. The `engine` is also rather general and provides a nice way to serialise specific kinds of python objects to `yaml`.\n\n### Why should I use this?\n\nWell, maybe if you:\n\n- need to use any of the libraries mentioned above, especially if you want to use them in the same project with the same infrastructure,\n- are tired of plain `hyperopt`,\n- would like to be able to save your model parameters in a readable format,\n- think it\'s neat?\n\nMy goal with this is to make it slightly easier for you to build up your own infrastructure for studying models and applications in our field! If you\'re just starting out, just take a look around!\n\n',
    'author': 'Marcel Langer',
    'author_email': 'dev@sirmarcel.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sirmarcel/cmlkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
