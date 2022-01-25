# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['levocli',
 'levocli.apitesting',
 'levocli.apitesting.runs',
 'levocli.commands',
 'levocli.handlers',
 'levocli.runners',
 'levocli.runners.levo_plans',
 'levocli.runners.levo_plans.modules',
 'levocli.runners.levo_plans.modules.bespoke',
 'levocli.runners.levo_plans.modules.schemathesis',
 'levocli.runners.levo_plans.modules.zaproxy',
 'levocli.runners.levo_plans.reporters',
 'levocli.runners.schemathesis',
 'levocli.runners.schemathesis.reporters']

package_data = \
{'': ['*']}

install_requires = \
['betterproto>=2.0.0b3,<3.0.0',
 'cattrs>=1.9.0,<2.0.0',
 'click-loglevel>=0.4.0,<0.5.0',
 'click>=8.0,<9.0',
 'colorama>=0.4.4,<0.5.0',
 'cryptography>=36.0.1,<37.0.0',
 'envyaml>=1.10.211231,<2.0.0',
 'grpcio>=1.37.0,<2.0.0',
 'jsonpath-ng>=1.5.3,<2.0.0',
 'levo-commons==0.1.26',
 'levo-ssrfmap>=0.1.12,<0.2.0',
 'orjson>=3.6.5,<4.0.0',
 'protobuf>=3.15.8,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-owasp-zap-v2.4>=0.0.19,<0.0.20',
 'questionary>=1.10.0,<2.0.0',
 'reportportal-client>=5.1.0,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=11.0.0,<12.0.0',
 'schemathesis==3.11.7',
 'sgqlc>=14.0,<15.0',
 'structlog>=21.4.0,<22.0.0',
 'yamlordereddictloader>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['levo = levocli.cli:levo']}

setup_kwargs = {
    'name': 'levo',
    'version': '0.4.5',
    'description': "Levo.ai's CLI that users can use to automatically trigger functional and security testing of their APIs.",
    'long_description': None,
    'author': 'Buchi Reddy B',
    'author_email': 'buchi@levo.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
