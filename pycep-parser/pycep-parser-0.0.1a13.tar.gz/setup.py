# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycep']

package_data = \
{'': ['*']}

install_requires = \
['lark>=1.0.0,<2.0.0', 'typing-extensions>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'pycep-parser',
    'version': '0.0.1a13',
    'description': 'A Python based Bicep parser',
    'long_description': '# pycep\n\n[![codecov](https://codecov.io/gh/gruebel/pycep/branch/master/graph/badge.svg?token=49WHVYGE1D)](https://codecov.io/gh/gruebel/pycep)\n[![PyPI](https://img.shields.io/pypi/v/pycep-parser)](https://pypi.org/project/pycep-parser/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pycep-parser)](https://github.com/gruebel/pycep)\n![CodeQL](https://github.com/gruebel/pycep/workflows/CodeQL/badge.svg)\n\nA fun little project, which has the goal to parse\n[Azure Bicep](https://github.com/Azure/bicep) files.\nThis is still a very early stage, therefore a lot can and will change.\n\n## Current capabalities\n\n[Supported capabilities](docs/capabilities.md)\n\n## Next milestones\n\n### General\n- [x] Complete loop support\n- [x] Param decorator\n- [x] Resource/Module decorator\n- [x] Target scope\n- [ ] Existing resource keyword\n- [ ] Module alias\n- [ ] Deployment condition\n- [x] Adding line numbers to element blocks\n\n### Functions\n- [x] Any\n- [ ] Array\n  - [ ] array\n  - [ ] concat\n  - [ ] contains\n  - [x] empty\n  - [ ] first\n  - [ ] intersection\n  - [ ] items\n  - [ ] last\n  - [ ] length\n  - [ ] max\n  - [ ] min\n  - [ ] range\n  - [ ] skip\n  - [ ] take\n  - [x] union\n- Resource\n  - [x] extensionResourceId\n  - [ ] getSecret\n  - [ ] list*\n  - [ ] pickZones\n  - [ ] reference\n  - [x] resourceId\n  - [x] subscriptionResourceId\n  - [x] tenantResourceId\n- [ ] Scope\n  - [ ] managementGroup\n  - [x] resourceGroup\n  - [x] subscription\n  - [ ] tenant\n\n### Operators\n- [ ] Accessor\n- [ ] Numeric\n\n### CI/CD\n- [ ] Fix security issues found by Scorecard\n\n## Considering\n- Adding line numbers to other parts\n\n## Out-of-scope\n- Bicep to ARM converter and vice versa\n',
    'author': 'Anton Grübel',
    'author_email': 'anton.gruebel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gruebel/pycep',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
