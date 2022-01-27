# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pycounts_thomassiu']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0']

setup_kwargs = {
    'name': 'pycounts-thomassiu',
    'version': '0.2.4',
    'description': 'Calculate word counts in a text file',
    'long_description': '# pycounts_thomassiu\n\nCalculate word counts in a text file!.\n\n## Installation\n\n```bash\n$ pip install pycounts_thomassiu\n```\n\n## Usage\n\n`pycounts_thomassiu` can be used to count words in a text file and plot results\nas follows :\n\n```python\nfrom pycounts_thomassiu.pycounts import count_words\nfrom pycounts_thomassiu.plotting import plot_words\nimport matplotlib.pyplot as plt\n\nfile_path = "test.txt"  # path to your file\ncounts = count_words(file_path)\nfig = plot_words(counts, n=10)\nplt.show()\n```\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`pycounts_thomassiu` was created by Thomas Siu. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`pycounts_thomassiu` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Thomas Siu',
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
