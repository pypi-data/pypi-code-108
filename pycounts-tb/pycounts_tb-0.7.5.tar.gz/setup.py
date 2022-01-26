# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pycounts_tb', 'pycounts_tb.data']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.0,<4.0.0']

setup_kwargs = {
    'name': 'pycounts-tb',
    'version': '0.7.5',
    'description': 'Calculate words  in a text file!',
    'long_description': '# pycounts\n\nCalculate word counts in a text file!\n\n## Installation\n\n```bash\n$ pip install pycounts\n```\n\n## Usage\n\n`pycounts` can be used to count words in a text file and plot the results\nas follows:\n\n```python\nfrom pycounts.pycounts import count_words\nfrom pycounts.plotting import plot_words\nimport matplotlib.pyplot as plt\n\nfile_path = "test.txt"  # path to your file\ncounts = count_words(file_path)\nfig = plot_words(counts, n=10)\nplt.show()\n```\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines.\nPlease note that this project is released with a Code of Conduct.\nBy contributing to this project, you agree to abide by its terms.\n\n## License\n\n`pycounts` was created by Tomas Beuzen. It is licensed under the terms\nof the MIT license.\n\n## Credits\n\n`pycounts` was created with\n[`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and\nthe `py-pkgs-cookiecutter`\n[template](https://github.com/py-pkgs/py-pkgs-cookiecutter).',
    'author': 'Tomas Beuzen',
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
