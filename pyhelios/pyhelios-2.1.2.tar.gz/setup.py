# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyhelios']

package_data = \
{'': ['*'], 'pyhelios': ['share/plot/*', 'share/templates/*']}

install_requires = \
['cmake-format>=0.6.0,<0.7.0',
 'flatdict>=4.0.0,<5.0.0',
 'ipython>=7.0.0,<8.0.0',
 'jinja2>=3.0.0,<4.0.0',
 'loguru==0.5.3',
 'numpy>=1.21.0,<2.0.0',
 'pygments>=2.0.0,<3.0.0',
 'pytomlpp>=1.0.0,<2.0.0',
 'rich>=10.0.0,<11.0.0',
 'traitlets>=5.0.0,<6.0.0',
 'typer>=0.4.0,<0.5.0',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['pyhls = pyhelios.pyhls:app']}

setup_kwargs = {
    'name': 'pyhelios',
    'version': '2.1.2',
    'description': "The HELIOS' toolbox",
    'long_description': "# pyhelios: the Helios' toolbox\n\n## Installation\n\n```sh\npip install pyhelios\n```\n\n## Contributing\n\nThe pyhelios Python package is managed by awesome tools: [poetry](https://python-poetry.org/) and [tox](https://tox.wiki/en/latest/index.html).\n\n1. Create a virtual environment using poetry.\n\n```sh\npoetry env use `which python`\n```\n\n2. Build the pyhelios Python package (sdist and wheel).\n\n```sh\npoetry build\n```\n\n2. Install in the previously created virtual environment.\n\n```sh\npoetry install\n```\n\n3. Run the tests.\n\n```sh\npoetry run python -m tox\n```\n\n4. Publish to the [Python Package Index](https://pypi.org/)\n\n```sh\npoetry publish\n```\n",
    'author': 'Julien Vanharen',
    'author_email': 'julien.vanharen@gmail.com',
    'maintainer': 'Julien Vanharen',
    'maintainer_email': 'julien.vanharen@gmail.com',
    'url': 'https://pypi.org/project/pyhelios',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
