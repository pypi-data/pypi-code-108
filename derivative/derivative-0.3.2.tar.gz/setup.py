# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['derivative']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18.3,<2.0.0',
 'pytest>=5.4.3,<6.0.0',
 'scipy>=1.4.1,<2.0.0',
 'sklearn>=0.0,<0.1']

extras_require = \
{'docs': ['sphinx>=3.0.2,<4.0.0',
          'nbsphinx>=0.6.1,<0.7.0',
          'ipykernel>=5.2.1,<6.0.0',
          'jupyter_client>=6.1.3,<7.0.0',
          'sphinx_rtd_theme>=0.4.3,<0.5.0',
          'matplotlib>=3.2.1,<4.0.0']}

setup_kwargs = {
    'name': 'derivative',
    'version': '0.3.2',
    'description': 'Numerical differentiation in python.',
    'long_description': '|RTD| |PyPI| |LIC|\n\nNumerical differentiation of noisy time series data in python\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\n**derivative** is a Python package for differentiating noisy data. The package showcases a variety of improvements that can be made over finite differences when data is not clean.\n\nWant to see an example of how **derivative** can help? Check us out in **PySINDy** (`github.com/dynamicslab/pysindy <https://github.com/dynamicslab/pysindy/>`_), a sparse-regression framework for discovering nonlinear dynamical systems from data!\n\nThis package binds common differentiation methods to a single easily implemented differentiation interface to encourage user adaptation.\nNumerical differentiation methods for noisy time series data in python includes:\n\n1. Symmetric finite difference schemes using arbitrary window size.\n\n2. Savitzky-Galoy derivatives (aka polynomial-filtered derivatives) of any polynomial order with independent left and right window parameters.\n\n3. Spectral derivatives with optional filter.\n\n4. Spline derivatives of any order.\n\n5. Polynomial-trend-filtered derivatives generalizing methods like total variational derivatives.\n\n.. code-block:: python\n\n    from derivative import dxdt\n    import numpy as np\n\n    t = np.linspace(0,2*np.pi,50)\n    x = np.sin(x)\n\n    # 1. Finite differences with central differencing using 3 points.\n    result1 = dxdt(x, t, kind="finite_difference", k=1)\n\n    # 2. Savitzky-Golay using cubic polynomials to fit in a centered window of length 1\n    result2 = dxdt(x, t, kind="savitzky_golay", left=.5, right=.5, order=3)\n\n    # 3. Spectral derivative\n    result3 = dxdt(x, t, kind="spectral")\n\n    # 4. Spline derivative with smoothing set to 0.01\n    result4 = dxdt(x, t, kind="spline", s=1e-2)\n\n    # 5. Total variational derivative with regularization set to 0.01\n    result5 = dxdt(x, t, kind="trend_filtered", order=0, alpha=1e-2)\n\n\nReferences:\n-----------\n\n[1] Numerical differentiation of experimental data: local versus global methods- K. Ahnert and M. Abel\n\n[2] Numerical Differentiation of Noisy, Nonsmooth Data- Rick Chartrand\n\n[3] The Solution Path of the Generalized LASSO- R.J. Tibshirani and J. Taylor\n\n\n.. |RTD| image:: https://readthedocs.org/projects/derivative/badge/?version=latest\n   :target: https://derivative.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n  \n.. |LIC| image:: https://img.shields.io/badge/License-MIT-blue.svg\n   :target: https://derivative.readthedocs.io/en/latest/license.html\n   :alt: MIT License\n\n.. |PyPI| image:: https://badge.fury.io/py/derivative.svg\n    :target: https://pypi.org/project/derivative/0.3.1/\n\n',
    'author': 'Andy Goldschmidt',
    'author_email': 'andygold@uw.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andgoldschmidt/derivative',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
