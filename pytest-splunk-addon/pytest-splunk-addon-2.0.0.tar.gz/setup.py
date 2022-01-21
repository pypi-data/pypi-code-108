# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_splunk_addon',
 'pytest_splunk_addon.helmut',
 'pytest_splunk_addon.helmut.app',
 'pytest_splunk_addon.helmut.connector',
 'pytest_splunk_addon.helmut.exceptions',
 'pytest_splunk_addon.helmut.log',
 'pytest_splunk_addon.helmut.manager',
 'pytest_splunk_addon.helmut.manager.confs',
 'pytest_splunk_addon.helmut.manager.confs.rest',
 'pytest_splunk_addon.helmut.manager.confs.sdk',
 'pytest_splunk_addon.helmut.manager.indexes',
 'pytest_splunk_addon.helmut.manager.indexes.rest',
 'pytest_splunk_addon.helmut.manager.indexes.sdk',
 'pytest_splunk_addon.helmut.manager.jobs',
 'pytest_splunk_addon.helmut.manager.jobs.rest',
 'pytest_splunk_addon.helmut.manager.jobs.sdk',
 'pytest_splunk_addon.helmut.manager.roles',
 'pytest_splunk_addon.helmut.manager.roles.sdk',
 'pytest_splunk_addon.helmut.manager.saved_searches',
 'pytest_splunk_addon.helmut.manager.saved_searches.sdk',
 'pytest_splunk_addon.helmut.manager.users',
 'pytest_splunk_addon.helmut.manager.users.sdk',
 'pytest_splunk_addon.helmut.misc',
 'pytest_splunk_addon.helmut.splunk',
 'pytest_splunk_addon.helmut.util',
 'pytest_splunk_addon.helmut_lib',
 'pytest_splunk_addon.standard_lib',
 'pytest_splunk_addon.standard_lib.addon_parser',
 'pytest_splunk_addon.standard_lib.cim_compliance',
 'pytest_splunk_addon.standard_lib.cim_tests',
 'pytest_splunk_addon.standard_lib.event_ingestors',
 'pytest_splunk_addon.standard_lib.fields_tests',
 'pytest_splunk_addon.standard_lib.index_tests',
 'pytest_splunk_addon.standard_lib.requirement_tests',
 'pytest_splunk_addon.standard_lib.sample_generation',
 'pytest_splunk_addon.standard_lib.utilities',
 'pytest_splunk_addon.tools']

package_data = \
{'': ['*'], 'pytest_splunk_addon.standard_lib': ['data_models/*']}

install_requires = \
['addonfactory-splunk-conf-parser-lib>=0.3.3,<0.4.0',
 'faker>=4.1,<12.0',
 'filelock>=3.0,<4.0',
 'httplib2',
 'jsonschema>=4.2.1,<5.0.0',
 'junitparser>=2.2.0,<3.0.0',
 'pytest-ordering',
 'pytest-xdist',
 'pytest>5.4.0,<6.3',
 'requests>=2,<3',
 'splunk-sdk>=1.6,<2.0',
 'splunk_appinspect>=2,<3']

extras_require = \
{'docker': ['lovely-pytest-docker>=0,<1']}

entry_points = \
{'console_scripts': ['cim-field-report = '
                     'pytest_splunk_addon.tools.cim_field_report:main',
                     'cim-report = '
                     'pytest_splunk_addon.standard_lib.utilities.junit_parser:main',
                     'generate-indextime-conf = '
                     'pytest_splunk_addon.standard_lib.utilities.create_new_eventgen:main'],
 'pytest11': ['plugin = pytest_splunk_addon.plugin',
              'splunk = pytest_splunk_addon.splunk']}

setup_kwargs = {
    'name': 'pytest-splunk-addon',
    'version': '2.0.0',
    'description': 'A Dynamic test tool for Splunk Apps and Add-ons',
    'long_description': None,
    'author': 'rfaircloth-splunk',
    'author_email': 'rfaircloth@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
