# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ingeniiadfg',
 'ingeniiadfg.activities',
 'ingeniiadfg.templates',
 'ingeniiadfg.templates.dataset',
 'ingeniiadfg.templates.integration_runtime',
 'ingeniiadfg.templates.linked_service',
 'ingeniiadfg.templates.trigger']

package_data = \
{'': ['*']}

install_requires = \
['deepdiff==5.5.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['ingeniiadfg = ingeniiadfg.main:app']}

setup_kwargs = {
    'name': 'ingeniiadfg',
    'version': '0.1.5',
    'description': 'Generate Azure Data Factory objects from configuration',
    'long_description': "# Ingenii Azure Data Factory Generator\nPython based generator to create Azure Data Factory pipelines from configurations.\n\nThis package integrates easily with the [Ingenii Azure Data Platform](https://github.com/ingenii-solutions/azure-data-platform), but this package can be used independently as long as some resouces are created ahead of time. These are detailed in the [Usage documentation](docs/user/Usage.md).\n\n* Current Version: 0.1.5\n\n## Package installation\n\nInstall the package [using pip](https://pip.pypa.io/en/stable/user_guide/) with \n```\npip install ingeniiadfg\n```\nor, for a particular version\n```\npip install ingeniiadfg==0.1.5\n```\nAlternatively, add it to your repository's current `requirements.txt` file. \n\n## Using the package\n\nFor details on using the package please refer to the [Azure Data Factory Usage documentation](docs/user/Usage.md).\n\n## Example CI/CD\n\nFor deploying into a Data Factory that is not integrated with a repository, also known as 'live' mode, we have included some example CI/CD pipelines in the `CICD` folder. These are in the format to be read by Azure Pipelines. Feel free to use these yourself or for inspiration in creating your own pipelines. \n\n## Version History\n\n* `0.1.5`: Move to a CLI package, and add several fixes \n* `0.1.4`: Add object annotations to track what is managed by this package \n* `0.1.3`: Extend schedule to handle when only the hours of the dayt are specified \n* `0.1.2`: Change the name of the secret name for the SAS URI to access the config tables\n* `0.1.1`: Add schedule generation from configuration, many more tests\n* `0.1.0`: Initial package, FTP/SFTP connections with basic authentication\n",
    'author': 'Greg Atkins',
    'author_email': 'greg@ingenii.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
