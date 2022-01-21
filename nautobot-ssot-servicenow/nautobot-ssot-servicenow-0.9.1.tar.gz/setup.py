# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nautobot_ssot_servicenow',
 'nautobot_ssot_servicenow.diffsync',
 'nautobot_ssot_servicenow.migrations',
 'nautobot_ssot_servicenow.tests']

package_data = \
{'': ['*'],
 'nautobot_ssot_servicenow': ['data/*',
                              'static/nautobot_ssot_servicenow/*',
                              'templates/nautobot_ssot_servicenow/*']}

install_requires = \
['Jinja2<3',
 'PyYAML>=5.4.1,<6.0.0',
 'diffsync>=1.3.0,<2.0.0',
 'nautobot-ssot>=1.0.1,<2.0.0',
 'nautobot>=1.2.0,<2.0.0',
 'pysnow>=0.7.17,<0.8.0']

setup_kwargs = {
    'name': 'nautobot-ssot-servicenow',
    'version': '0.9.1',
    'description': 'Nautobot SSoT ServiceNow',
    'long_description': '# Nautobot Single Source of Truth -- ServiceNow Data Target\n\nA plugin for [Nautobot](https://github.com/nautobot/nautobot), building atop the [nautobot-ssot](https://github.com/nautobot/nautobot-plugin-ssot/) plugin.\n\nThis plugin provides the ability to synchronize basic data from Nautobot into ServiceNow. Currently the following data is mapped and synchronized:\n\n- Nautobot Manufacturer table to ServiceNow Company table\n- Nautobot DeviceType table to ServiceNow Hardware Product Model table\n- Nautobot Region and Site tables to ServiceNow Location table\n- Nautobot Device table to ServiceNow IP Switch table\n- Nautobot Interface table to ServiceNow Interface table\n\nFor more information about general usage of the Nautobot SSoT plugin, refer to [its documentation](https://nautobot-plugin-ssot.readthedocs.io/).\n\n## Installation and Configuration\n\nThe plugin is available as a Python package in PyPI and can be installed with `pip` into an existing Nautobot installation:\n\n```shell\npip install nautobot-ssot-servicenow\n```\n\n> The plugin is compatible with Nautobot 1.2.0 and higher\n\nOnce installed, the plugin needs to be enabled in your `nautobot_config.py` and configured appropriately:\n\n```python\n# nautobot_config.py\nPLUGINS = [\n    "nautobot_ssot",\n    "nautobot_ssot_servicenow",\n]\n\nPLUGINS_CONFIG = {\n    "nautobot_ssot": {\n        "hide_example_jobs": True,\n    },\n    "nautobot_ssot_servicenow": {\n        "instance": os.getenv("SERVICENOW_INSTANCE"),\n        "username": os.getenv("SERVICENOW_USERNAME"),\n        "password": os.getenv("SERVICENOW_PASSWORD"),\n    },\n}\n```\n\nThe plugin behavior can be controlled with the following list of settings:\n\n- `instance`: The ServiceNow instance to point to (as in `<instance>.servicenow.com`)\n- `username`: Username to access this instance\n- `password`: Password to access this instance\n\nThere is also the option of omitting these settings from `PLUGINS_CONFIG` and instead defining them through the UI at `/plugins/ssot-servicenow/config/` (reachable by navigating to **Plugins > Installed Plugins** then clicking the "gear" icon next to the *Nautobot SSoT ServiceNow* entry) using Nautobot\'s standard UI and [secrets](https://nautobot.readthedocs.io/en/stable/core-functionality/secrets/) functionality.\n\n> If you configure the plugin\'s settings in `PLUGINS_CONFIG`, those values will take precedence over any configuration in the UI.\n\nDepending on the amount of data involved, and the performance of your ServiceNow instance, you may need to increase the Nautobot job execution time limits ([`CELERY_TASK_SOFT_TIME_LIMIT`](https://nautobot.readthedocs.io/en/stable/configuration/optional-settings/#celery_task_soft_time_limit) and [`CELERY_TASK_TIME_LIMIT`](https://nautobot.readthedocs.io/en/stable/configuration/optional-settings/#celery_task_time_limit)) so that the job can execute to completion without timing out.\n\n## Questions\n\nFor any questions or comments, please check the [FAQ](FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #networktocode).\nSign up [here](http://slack.networktocode.com/)\n\n## Usage\n\nOnce the plugin is installed and configured, from the Nautobot SSoT dashboard view (`/plugins/ssot/`), ServiceNow will be shown as a Data Target. You can click the **Sync** button to access a form view from which you can run the Nautobot-to-ServiceNow synchronization Job. Running the job will redirect you to a Nautobot **Job Result** view, from which you can access the **SSoT Sync Details** view to see detailed information about the outcome of the sync Job.\n\n![Detail View](https://raw.githubusercontent.com/nautobot/nautobot-plugin-ssot-servicenow/develop/docs/images/detail-view.png)\n\n---\n\n![Results View](https://raw.githubusercontent.com/nautobot/nautobot-plugin-ssot-servicenow/develop/docs/images/result-view.png)\n',
    'author': 'Network to Code, LLC',
    'author_email': 'opensource@networktocode.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nautobot/nautobot-plugin-ssot-servicenow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
