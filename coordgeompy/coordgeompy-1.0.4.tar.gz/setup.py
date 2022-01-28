# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['coordgeompy']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.1,<2.0.0']

setup_kwargs = {
    'name': 'coordgeompy',
    'version': '1.0.4',
    'description': 'A simple coordinate geometry helper package',
    'long_description': "[![ci-cd](https://github.com/UBC-MDS/coordgeompy/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/coordgeompy/actions/workflows/ci-cd.yml)\n[![codecov](https://codecov.io/gh/UBC-MDS/CoordGeomPy/branch/main/graph/badge.svg?token=9jgbpldNoe)](https://codecov.io/gh/UBC-MDS/CoordGeomPy)\n[![Documentation Status](https://readthedocs.org/projects/coordgeompy/badge/?version=latest)](https://coordgeompy.readthedocs.io/en/latest/?badge=latest)\n\n# CoordGeomPy\n\nA simple coordinate geometry helper package. This package is developed for the UBC MDS DSCI 524 Collaborative Software Development course at the University of British Columbia.\n\n## Overview\n\nThis starter package allows users to perform various geometric operations like calculate distance between two parallel lines, distance between two n dimensional vectors, intersection of lines in 3-Dimensional space and so on. Our motivation in creating this package was to allow users with minimal experience in python coding to be able to perform these geometric calculations easily.\n## Installation\n\n```bash\n$ pip install git+https://github.com/UBC-MDS/CoordGeomPy.git@v1.0.0\n```\n\n## Features\n\nThere are four main functions planned for development as outlined below. Additional functions may be added in the future.\n\nFunction 1 `dist_pll_lines_2d`: This function allows a user to calculate the distance between two parallel lines. This is the distance between the points where a perpendicular line intersects between the two parallel lines. This function will find that distance (d).\n\nFunction 2 `get_distance`: This function allows a user to calculate the the distance between two n dimensional vectors. Possible metrics that can be used with this function includes: Euclidean, Manhattan, Chebyshev, or Minkowski\n\nFunction 3 `is_intersection_3d`: This function allows a user to determine whether two infinite lines intersect in 3-dimensional space. The function will return True or False based on the input arguments.\n\nFunction 4 `is_orthogonal`: This function allows a user to determine whether two infinite lines are perpendicular in n-dimensional space. The function will return True or False based on the input arguments.\n\nWhile we are not really reinventing the wheel on coordinate geometry calculations with our package, we used this as an opportunity to gain some experience in understanding how these calculations function in python language. There are existing packages that execute similar functions. For example, [SymPy](https://www.sympy.org/en/index.html) is a Python library that contains comprehensive mathematical functions including intersection of lines, shortest distance between a point and a line etc. We also found a package [coordinate-geometry 1.0.02](https://pypi.org/project/coordinate-geometry/) that had similar functions to calculating distance between two points, a point and a line, area of a triangle etc. [Scipy's](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html) `scipy.spatial.distance.cdist` functions similarly to Function 2. \n## Usage\n\n- TODO\n\n## Documentation \n\nThe official documentation is hosted on [Read the Docs](https://coordgeompy.readthedocs.io/en/latest/)\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## Contributors\n\nWe welcome and recognize all contributors. Names and GitHub @usernames listed below:\n\n- Arlin Cherian: @arlincherian\n- Nico Van Den Hooff: @nicovandenhooff\n- Zheren Xu: @ZherenXu\n- Jordan Casoli: @jcasoli\n\n## License\n\n`CoordGeomPy` was created by Jordan Casoli, Nico Van Den Hooff, Arlin Cherian and Zheren Xu. It is licensed under the terms of the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\n## Credits\n\n`CoordGeomPy` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Jordan Casoli, Nico Van Den Hooff, Arlin Cherian and Zheren Xu',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
