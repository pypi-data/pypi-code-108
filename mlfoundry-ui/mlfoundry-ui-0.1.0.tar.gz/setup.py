# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlfoundry_ui',
 'mlfoundry_ui.cli',
 'mlfoundry_ui.webapp',
 'mlfoundry_ui.webapp.model_comparison',
 'mlfoundry_ui.webapp.model_view']

package_data = \
{'': ['*']}

install_requires = \
['hydralit>=1.0.10,<2.0.0',
 'matplotlib>=3.0.3',
 'mlflow>=1.14',
 'numpy>=1.17.0',
 'pandas>=1.0.0',
 'plotly>=5.5.0,<6.0.0',
 'streamlit>=1.3.0,<2.0.0',
 'whylogs>=0.6.15']

entry_points = \
{'console_scripts': ['mlfoundry_ui = '
                     'mlfoundry_ui.cli.cli_interface:create_mlfoundry_ui_cli']}

setup_kwargs = {
    'name': 'mlfoundry-ui',
    'version': '0.1.0',
    'description': 'Dashboard code for mlfoundry',
    'long_description': '# mlfoundry-ui\n\n## Development Instructions \n```\nvirtualenv venv \nsource venv/bin/activate\npip install poetry \npoetry install\n\npip install pre-commit\npre-commit install\n```\n',
    'author': 'Abhishek Choudhary',
    'author_email': 'abhichoudhary06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/truefoundry/mlfoundry-ui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
