# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reggy']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.5,<2.0.0',
 'tensorflow-probability>=0.15.0,<0.16.0',
 'tensorflow>=2.7.0,<3.0.0']

setup_kwargs = {
    'name': 'reggy',
    'version': '0.2.0',
    'description': 'Python package for regularized regressions.',
    'long_description': '# reggy\n\n[![PyPI](https://img.shields.io/pypi/v/reggy.svg?style=flat)](https://pypi.python.org/pypi/reggy)\n[![Tests](https://github.com/kpj/reggy/workflows/Tests/badge.svg)](https://github.com/kpj/reggy/actions)\n\nPython package for regularized regressions.\n\nSupported regularization terms:\n* Ridge\n* LASSO\n* Network-fusion penalty (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6030897/)\n\n\n## Installation\n\n```bash\n$ pip install reggy\n```\n\n\n## Usage\n\nA simple example with LASSO regularization:\n```python\nimport reggy\nimport numpy as np\n\n\nalpha = 0.3\nbeta = 1.7\n\nX = np.random.normal(size=(100, 1))\ny = np.random.normal(X * beta + alpha, size=(100, 1))\n\nmodel = reggy.RegReg(X, y, family=reggy.gaussian_family, regularizers=[(0.5, reggy.lasso)])\nmodel.fit()\n\nprint(model.intercept_, model.coef_)\n## [[0.22491232]] [[0.9219889]]\n```\n',
    'author': 'kpj',
    'author_email': 'kim.philipp.jablonski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kpj/reggy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.0,<3.10.0',
}


setup(**setup_kwargs)
