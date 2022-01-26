# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['doniclient',
 'doniclient.osc',
 'doniclient.tests',
 'doniclient.tests.osc',
 'doniclient.tests.v1',
 'doniclient.v1']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML<=5.1.2',
 'keystoneauth1>=3.17.3',
 'osc-lib>=1.14.1',
 'python-dateutil<=2.8.0',
 'python-openstackclient[cli]>=4.0.2']

entry_points = \
{'openstack.cli.extension': ['inventory = doniclient.osc.plugin'],
 'openstack.inventory.v1': ['hardware_availability_add = '
                            'doniclient.osc.availability:AddHardwareAvailability',
                            'hardware_availability_list = '
                            'doniclient.osc.availability:ListHardwareAvailability',
                            'hardware_availability_remove = '
                            'doniclient.osc.availability:RemoveHardwareAvailability',
                            'hardware_availability_set = '
                            'doniclient.osc.availability:UpdateHardwareAvailability',
                            'hardware_create = '
                            'doniclient.osc.cli:CreateHardware',
                            'hardware_delete = '
                            'doniclient.osc.cli:DeleteHardware',
                            'hardware_import = '
                            'doniclient.osc.cli:ImportHardware',
                            'hardware_list = doniclient.osc.cli:ListHardware',
                            'hardware_set = doniclient.osc.cli:UpdateHardware',
                            'hardware_show = doniclient.osc.cli:GetHardware',
                            'hardware_sync = doniclient.osc.cli:SyncHardware']}

setup_kwargs = {
    'name': 'python-doniclient',
    'version': '0.4.3',
    'description': 'This is a plugin for the openstack commandline client, to enable support for the Doni hardware inventory project',
    'long_description': '# python-doniclient\nClient for Chameleon Registration Service\n',
    'author': 'Chameleon Cloud',
    'author_email': 'contact@chameleoncloud.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ChameleonCloud/python-doniclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
