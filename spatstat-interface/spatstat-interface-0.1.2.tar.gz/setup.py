# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['spatstat_interface']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'rpy2>=3.4.5,<4.0.0']

extras_require = \
{'notebook': ['jupyter>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'spatstat-interface',
    'version': '0.1.2',
    'description': 'Simple Python interface with the spatstat R package using rpy2',
    'long_description': '# spatstat-interface\n\n[![Build](https://github.com/For-a-few-DPPs-more/spatstat-interface/actions/workflows/main.yml/badge.svg)](https://github.com/For-a-few-DPPs-more/spatstat-interface/actions/workflows/main.yml)\n[![PyPi version](https://badgen.net/pypi/v/spatstat-interface/)](https://pypi.org/project/spatstat-interface/)\n[![codecov](https://codecov.io/gh/For-a-few-DPPs-more/spatstat-interface/branch/main/graph/badge.svg?token=BHTI6L66P2)](https://codecov.io/gh/For-a-few-DPPs-more/spatstat-interface)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n- [spatstat-interface](#spatstat-interface)\n  - [Dependencies](#dependencies)\n  - [Installation](#installation)\n    - [Install the project as a dependency](#install-the-project-as-a-dependency)\n    - [Install in editable mode and potentially contribute to the project](#install-in-editable-mode-and-potentially-contribute-to-the-project)\n      - [Using `poetry`](#using-poetry)\n      - [Using `pip`](#using-pip)\n  - [Documentation](#documentation)\n    - [Main resources](#main-resources)\n    - [Notes about `spatstat`](#notes-about-spatstat)\n    - [Calling functions](#calling-functions)\n      - [Calling function.variant](#calling-functionvariant)\n      - [Keyword arguments](#keyword-arguments)\n\nSimple Python interface with the spatial statistics [R](https://www.r-project.org/) package [`spatstat`](https://github.com/spatstat/spatstat) using [`rpy2`](https://github.com/rpy2/rpy2).\n\n## Dependencies\n\n- [R](https://www.r-project.org/) (programming language),\n- Python dependencies are listed in the [`pyproject.toml`](./pyproject.toml) file. Note that they mostly correspond to the latest version.\n\n  ```toml\n  [tool.poetry.dependencies]\n  python = "^3.7.1"\n\n  matplotlib = "^3.4.2"\n  numpy = "^1.20.3"\n  pandas = "^1.2.4"\n  rpy2 = "^3.4.5"\n  ```\n\n## Installation\n\nYou may consider using `poetry` to manage your whole project as described here <https://github.com/guilgautier/template-python-project>.\n\n### Install the project as a dependency\n\n- Install the latest version published on [![PyPi version](https://badgen.net/pypi/v/spatstat-interface/)](https://pypi.org/project/spatstat-interface/)\n\n  ```bash\n  # activate your virtual environment an run\n  poetry add spatstat-interface\n  # pip install spatstat-interface\n  ```\n\n- Install from source (this may be broken)\n\n  ```bash\n  # activate your virtual environment an run\n  poetry add git+https://github.com/For-a-few-DPPs-more/spatstat-interface.git\n  # pip install git+https://github.com/For-a-few-DPPs-more/spatstat-interface.git\n  ```\n\n### Install in editable mode and potentially contribute to the project\n\nYou may consider [forking the repository](https://github.com/For-a-few-DPPs-more/spatstat-interface/fork).\n\nIn any case, your can clone the repository\n\n- if you have forked the repository\n\n  ```bash\n  git clone https://github.com/your_user_name/spatstat-interface.git\n  ```\n\n- if you have **not** forked the repository\n\n  ```bash\n  git clone https://github.com/For-a-few-DPPs-more/spatstat-interface.git\n  ```\n\n#### Using `poetry`\n\nThe package can be installed in **editable** mode along with\n\n- main (non-optional) dependencies, see `[tool.poetry.dependencies]` in [`pyproject.toml`](./pyproject.toml)\n- development dependencies, `[tool.poetry.dev-dependencies]` in [`pyproject.toml`](./pyproject.toml)\n\n```bash\ncd spatstat-interface\n# activate your virtual environment or run\n# poetry shell  # to create/activate local .venv (see poetry.toml)\npoetry install\n# poetry install --no-dev  # to avoid installing the development dependencies\n```\n\n#### Using `pip`\n\nFor now, packages defined only by a [`pyproject.toml`](./pyproject.toml) file **can\'t be installed editable mode directly** using `pip`.\n\nAlternatives\n\n1. consider [using `poetry` instead](#using-poetry)\n\n2. otherwise, for your convenience, the [`pyproject.toml`](./pyproject.toml) file was duplicated into a [`setup.cfg`](./setup.cfg) file to enable editable install using `pip`.\n\n   - modify the `[build-system]` section in [`pyproject.toml`](./pyproject.toml) to\n\n      ```toml\n      [build-system]\n      requires = ["setuptools >= 40.9.0", "wheel"]\n      build-backend = "setuptools.build_meta"\n      ```\n\n   - intstall the project in editable mode\n\n      ```bash\n      cd spatstat-interface\n      # activate your virtual environment and run\n      pip install -e .\n      ```\n\n## Documentation\n\n### Main resources\n\n- [`notebooks`](./notebooks) showcase detailed examples\n- [`rpy2` documentation](https://rpy2.github.io/doc.html)\n- [`spatstat` documentation](https://rdocumentation.org/search?q=spatstat)\n\n### Notes about `spatstat`\n\nThe [`spatstat`](https://github.com/spatstat/spatstat) package has recently been split into multiple sub-packages and extensions.\n\nUsing `spatstat-interface`, sub-packages and extensions are accessible in the following way\n\n```python\nfrom spatstat_interface.interface import SpatstatInterface\n\nspatstat = SpatstatInterface(update=True)\n# spatstat.core is None\n# spatstat.geom is None\n\n# load/import sub-packages or extensions\nspatstat.import_package("core", "geom", update=True)\nspatstat.core\nspatstat.geom\n```\n\n### Calling functions\n\n#### Calling function.variant\n\nTo call the R `function.variant`\n\n```R\n# R code pcf.ppp\nspatstat.core::pcf.ppp(X)\n```\n\nReplace `.` by `_` to call `function_variant` in Python\n\n```Python\n# Python code pcf_ppp\nspatstat.core.pcf_ppp(X)\n```\n\n#### Keyword arguments\n\nConsider using Python dictionaries to pass keyword arguments.\nBelow are a few examples.\n\n- dot keywords, for example passing `var.approx` keyword argument won\'t work in Python\n\n  ```R\n  # R code\n  spatstat.core::pcf.ppp(X, kernel="epanechnikov", var.approx=False)\n  ```\n\n  ```Python\n  # Python code\n  params = {"kernel": "epanechnikov", "var.approx": False}\n  spatstat.core.pcf_pp(X, **params)\n  ```\n\n- reserved keywords, for example `lambda` is a reserved Python keyword; it can\'t be used as a keyword argument\n\n  ```R\n  # R code\n  spatstat.core::dppGauss(lambda=rho, alpha=alpha, d=d)\n  ```\n\n  ```Python\n  # Python code\n  params = {"lambda": rho, "alpha": alpha, "d": d}\n  spatstat.core.dppGauss(**params)\n  ```\n',
    'author': 'Guillaume Gautier',
    'author_email': 'guillaume.gga@gmail.com',
    'maintainer': 'Guillaume Gautier',
    'maintainer_email': 'guillaume.gga@gmail.com',
    'url': 'https://github.com/For-a-few-DPPs-more/spatstat-interface',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
