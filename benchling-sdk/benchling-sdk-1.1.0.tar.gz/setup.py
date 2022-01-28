# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['benchling_api_client',
 'benchling_api_client.api',
 'benchling_api_client.api.aa_sequences',
 'benchling_api_client.api.apps',
 'benchling_api_client.api.assay_results',
 'benchling_api_client.api.assay_runs',
 'benchling_api_client.api.authentication',
 'benchling_api_client.api.batches',
 'benchling_api_client.api.blobs',
 'benchling_api_client.api.boxes',
 'benchling_api_client.api.containers',
 'benchling_api_client.api.custom_entities',
 'benchling_api_client.api.dna_alignments',
 'benchling_api_client.api.dna_oligos',
 'benchling_api_client.api.dna_sequences',
 'benchling_api_client.api.dropdowns',
 'benchling_api_client.api.entries',
 'benchling_api_client.api.events',
 'benchling_api_client.api.exports',
 'benchling_api_client.api.feature_libraries',
 'benchling_api_client.api.folders',
 'benchling_api_client.api.inventory',
 'benchling_api_client.api.lab_automation',
 'benchling_api_client.api.label_templates',
 'benchling_api_client.api.legacy_workflows',
 'benchling_api_client.api.legacy_workflows_deprecated',
 'benchling_api_client.api.locations',
 'benchling_api_client.api.mixtures',
 'benchling_api_client.api.oligos',
 'benchling_api_client.api.organizations',
 'benchling_api_client.api.plates',
 'benchling_api_client.api.printers',
 'benchling_api_client.api.projects',
 'benchling_api_client.api.registry',
 'benchling_api_client.api.requests',
 'benchling_api_client.api.rna_oligos',
 'benchling_api_client.api.schemas',
 'benchling_api_client.api.tasks',
 'benchling_api_client.api.teams',
 'benchling_api_client.api.users',
 'benchling_api_client.api.warehouse',
 'benchling_api_client.api.workflow_outputs',
 'benchling_api_client.api.workflow_task_groups',
 'benchling_api_client.api.workflow_tasks',
 'benchling_api_client.models',
 'benchling_sdk',
 'benchling_sdk.auth',
 'benchling_sdk.helpers',
 'benchling_sdk.models',
 'benchling_sdk.services']

package_data = \
{'': ['*'],
 'benchling_sdk': ['codegen/templates/*',
                   'codegen/templates/property_templates/*']}

install_requires = \
['attrs>=20.1.0,<21.0.0',
 'backoff>=1.10.0,<2.0.0',
 'dataclasses-json>=0.5.2,<0.6.0',
 'httpx>=0.15.0,<0.16.0',
 'python-dateutil>=2.8.0,<3.0.0',
 'typing-extensions>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'benchling-sdk',
    'version': '1.1.0',
    'description': 'SDK for interacting with the Benchling Platform.',
    'long_description': '# Benchling SDK\n\nA Python 3.7+ SDK for the [Benchling](https://www.benchling.com/) platform designed to provide typed, fluent\ninteractions with [Benchling APIs](https://docs.benchling.com/reference).\n\n## Installation\n\nInstall the dependency via [Poetry](https://python-poetry.org/) (if applicable):\n\n```bash\npoetry add benchling-sdk\n```\n \nOr [Pip](https://pypi.org/project/pip/):\n \n```bash\npip install benchling-sdk\n```\n\n## Documentation\n\nDocumentation for the SDK is kept up-to-date at [docs.benchling.com](https://docs.benchling.com), and you can get started with\nit using this guide:\n[https://docs.benchling.com/docs/getting-started-with-the-sdk](https://docs.benchling.com/docs/getting-started-with-the-sdk).\n\n## Support\n\nTo report issues with using the SDK, contact [support@benchling.com](mailto:support@benchling.com).\n',
    'author': 'Benchling Support',
    'author_email': 'support@benchling.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
