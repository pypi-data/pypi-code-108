# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['testpackagemds']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.0,<4.0.0']

setup_kwargs = {
    'name': 'testpackagemds',
    'version': '0.4.0',
    'description': 'Calculate words  in a text file!',
    'long_description': '# testpackagemds 0.1.0\nA package created to try a GitHub Actions workflow!\n\n## Installation\n\n```bash\n$ pip install testpackagemds\n```\n\n## Usage\n\n\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`testpackagemds` was created by Florencia. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`testpackagemds` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Florencia. Test based in Tomas Beuzen work',
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
