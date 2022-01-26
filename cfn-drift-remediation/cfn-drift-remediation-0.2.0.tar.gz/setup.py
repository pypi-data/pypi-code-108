# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cfn_drift_remediation']

package_data = \
{'': ['*'], 'cfn_drift_remediation': ['cloudformation_resource_schemas/*']}

install_requires = \
['boto3>=1.20.43,<2.0.0',
 'fastjsonschema>=2.15.3,<3.0.0',
 'jsonpointer>=2.2,<3.0']

entry_points = \
{'console_scripts': ['cfn-drift-remediation = cfn_drift_remediation.cli:run']}

setup_kwargs = {
    'name': 'cfn-drift-remediation',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Ben Bridts',
    'author_email': None,
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
