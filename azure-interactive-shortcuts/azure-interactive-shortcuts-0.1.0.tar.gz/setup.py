# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['azure_interactive_shortcuts']

package_data = \
{'': ['*']}

install_requires = \
['argcomplete>=2.0.0,<3.0.0',
 'dataclasses-json>=0.5.6,<0.6.0',
 'logging-actions>=0.1.6,<0.2.0',
 'prompt-toolkit>=3.0.24,<4.0.0',
 'returns>=0.18.0,<0.19.0',
 'rich>=11.0.0,<12.0.0']

entry_points = \
{'console_scripts': ['azis = azure_interactive_shortcuts:_main',
                     'azure-interactive-shortcuts = '
                     'azure_interactive_shortcuts:_main']}

setup_kwargs = {
    'name': 'azure-interactive-shortcuts',
    'version': '0.1.0',
    'description': 'Helpful tools for using Azure resources interactively at the command line',
    'long_description': '# Shortcuts for interacting with Azure resources\n## Usage\n### Print a VM IP after fuzzy searching\n```\n$ azure-interactive-shortcuts public-vm-ip\n⠙ Collecting IP addresses from all VMs using Azure CLI\n```\n```\n$ azure-interactive-shortcuts public-vm-ip\nazis public-vm-ip\n[19:12:24] Found 180 virtual machines, and 96 public ip   _public_vm_ip.py:76\n           addresses                                                         \n           4 ip addresses have the same name, and have    _public_vm_ip.py:85\n           been discarded                                                    \nSelect an IP address:\n aatifs-cool-vm1-ip1   Resource group: my-rg1, VMs: aatifs-cool-VM1... \n aatifs-cool-vm1-ip2   Resource group: my-rg1, VMs: aatifs-cool-VM1... \n aatifs-cool-vm2-ip3   Resource group: my-rg2, VMs: aatifs-cool-VM2... \n aatifs-cool-vm2-ip4   Resource group: my-rg2, VMs: aatifs-cool-VM2... \n```\n\nThis allows you to have quick one-liners:\n```bash\nssh azureuser@"$(azis public-vm-ip)"\n```\n\n## Installation\nRecommended installation is with [pipx](https://github.com/pypa/pipx):\n```bash\npython3 -m pip install --user pipx\npython3 -m pipx ensurepath\npython3 -m pipx install azure-interactive-shortcuts\n```\n\n### Autocompletion\nAutocompletion is done with [argcomplete](https://github.com/kislyuk/argcomplete)\n```bash\npipx install --force argcomplete\n\n# ~/.bashrc\neval "$(register-python-argcomplete azis)"\neval "$(register-python-argcomplete azure-interactive-shortcuts)"\n```',
    'author': 'Aatif Syed',
    'author_email': 'aatifsyedyp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aatifsyed/azure-interactive-shortcuts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
