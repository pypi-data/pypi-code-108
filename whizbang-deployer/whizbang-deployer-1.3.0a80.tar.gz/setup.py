# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whizbang',
 'whizbang.config',
 'whizbang.container',
 'whizbang.core',
 'whizbang.data',
 'whizbang.data.databricks',
 'whizbang.data.pyodbc',
 'whizbang.domain',
 'whizbang.domain.handler',
 'whizbang.domain.manager',
 'whizbang.domain.manager.az',
 'whizbang.domain.manager.bicep',
 'whizbang.domain.manager.databricks',
 'whizbang.domain.manager.pyodbc',
 'whizbang.domain.menu',
 'whizbang.domain.models',
 'whizbang.domain.models.active_directory',
 'whizbang.domain.models.databricks',
 'whizbang.domain.models.datafactory',
 'whizbang.domain.models.keyvault',
 'whizbang.domain.models.menu',
 'whizbang.domain.models.sql',
 'whizbang.domain.models.storage',
 'whizbang.domain.repository',
 'whizbang.domain.repository.az',
 'whizbang.domain.repository.databricks',
 'whizbang.domain.repository.sql_server',
 'whizbang.domain.shared_types',
 'whizbang.domain.solution',
 'whizbang.domain.workflow',
 'whizbang.domain.workflow.bicep',
 'whizbang.domain.workflow.databricks',
 'whizbang.domain.workflow.datalake',
 'whizbang.notes',
 'whizbang.util']

package_data = \
{'': ['*'], 'whizbang': ['reference/*']}

install_requires = \
['az.cli>=0.5,<0.6',
 'azure-cli>=2.30.0,<3.0.0',
 'databricks-cli==0.16.2',
 'dependency-injector>=4.35.2,<5.0.0',
 'jsonpath-ng>=1.5.3,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyodbc>=4.0.32,<5.0.0',
 'pytest>=6.2.4,<7.0.0',
 'sqlparse>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['whizbang = whizbang.__main__:main']}

setup_kwargs = {
    'name': 'whizbang-deployer',
    'version': '1.3.0a80',
    'description': 'Whizbang Deployer - An all-in-one Azure deployment solution',
    'long_description': '## Whizbang\n\nThe Whizbang deployer is a tool designed to simplify deployments of Azure solutions.  The solutions contains utilities and functions that implmenting projects use to deploy specific azure solutions for customers.\n\n### Installation\n\nIt it important to note that this package is installed and distributed in two different modes:\n- **Local Binary Installation** -> This requires the needed packages to be install globally.  This is how development with dependent projects (i.e. empower) is typically done.\n- **Containerized** -> The containerized method includes binary dependencies which are used for CI/CD and is how the artifact is actually deployed and used in production.\n\n#### Mac Prequisites\n- `brew install docker docker-compose`\n\n#### Windows Prequisites\n_TODO_\n\n#### Local Binary Build\n`poetry install`\n`poetry build`\n`pip3 uninstall whizbang-deployer -y`\n`pip3 install ./dist/whizbang*.whl`\n_Then run any solution file directly: `python solution.py`_\n\n**To run tests:**\n`python3 -m pytest`\n\n#### Containerized Build\n_These may no longer work._\n\n**To run pytests:**\n- `docker-compose -f docker_builds/docker-compose.yml up --build pyenv`\n\n**To run pytests with watch:**\n- `docker-compose -f docker_builds/docker-compose.yml up --build pyenv-watch`\n',
    'author': 'Brian Aiken',
    'author_email': 'baiken@hitachisolutions.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hitachisolutionsamerica/whizbang-deployer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
