# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reggy']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=8.0.1,<9.0.0',
 'pandas>=1.3.5,<2.0.0',
 'tensorflow-probability>=0.15.0,<0.16.0',
 'tensorflow>=2.7.0,<3.0.0']

setup_kwargs = {
    'name': 'reggy',
    'version': '0.1.0',
    'description': 'Regressions with arbitrarily complex regularization terms.',
    'long_description': '# reggy\n\n[![PyPI](https://img.shields.io/pypi/v/reggy.svg?style=flat)](https://pypi.python.org/pypi/reggy)\n[![Tests](https://github.com/kpj/reggy/workflows/Tests/badge.svg)](https://github.com/kpj/reggy/actions)\n\nRegressions with arbitrarily complex regularization terms.\n\nCurrently supported regularization terms:\n* LASSO\n\n\n## Installation\n\n```bash\n$ pip install reggy\n```\n\n\n## Usage\n\nA simple example with LASSO regularization:\n```python\nimport reggy\nimport numpy as np\n\n\nalpha = 0.3\nbeta = 1.7\n\nX = np.random.normal(size=(1000, 1))\ny = np.random.normal(X * beta + alpha, size=(1000, 1))\n\nmodel = reggy.RegReg(X, y, regularizers=[reggy.lasso])\nmodel.fit()\n\nprint(model.coef())\n## (array([[0.27395004]], dtype=float32), array([[1.2682909]], dtype=float32))\n```\n',
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
