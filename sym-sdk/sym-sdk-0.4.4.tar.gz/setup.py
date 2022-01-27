# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sym',
 'sym.sdk',
 'sym.sdk.annotations',
 'sym.sdk.integrations',
 'sym.sdk.integrations.dangerous',
 'sym.sdk.templates',
 'sym.sdk.tests',
 'sym.sdk.tests.annotations',
 'sym.sdk.tests.integrations',
 'sym.sdk.tests.static',
 'sym.sdk.util',
 'sym.sdk.util.template']

package_data = \
{'': ['*']}

install_requires = \
['bcrypt>=3.2,<4.0',
 'pydantic>=1.7.3,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'structlog>=20.1,<21.0',
 'virtualenv>=20.4.7,<21.0.0']

setup_kwargs = {
    'name': 'sym-sdk',
    'version': '0.4.4',
    'description': "Sym's Python SDK",
    'long_description': 'Sym Python SDK\n================\n\n`Sym <https://symops.com/>`_ is the security workflow platform made for engineers, by engineers.\n\nWe solve the intent-to-execution gap between policies and workflows by providing fast-moving engineering teams with the just-right primitives to roll out best-practice controls.\n\nThis is the Python SDK for Sym.\nFor guides and other help, check out our `main docs site <https://docs.symops.com/>`_.\n\nThe SDK docs are broken into several core modules, which are described below.\nClick on one to see the classes and functions available in your `Handlers <https://docs.symops.com/docs/handlers>`_.\n\nThe Sym SDK is used to customize workflow templates that are exposed by our `Terraform provider <https://docs.symops.com/docs/terraform-provider>`_. Here\'s an example using the ``sym:approve`` Template!\n\n.. code-block:: python\n\n   from sym.sdk.annotations import reducer\n   from sym.sdk.integrations import pagerduty, okta, slack\n\n   @reducer\n   def get_approvers(evt):\n      # The import here uses credentials defined in an Integration in Terraform\n      if pagerduty.is_on_call(evt.user, schedule="id_of_eng_on_call"):\n         # This is a self-approval in a DM\n         return slack.user(evt.user)\n\n      if evt.payload.fields["urgency"] == "Emergency":\n         # This is a self-approval in a channel\n         return slack.channel("#break-glass", allow_self=True)\n\n      on_call_mgrs = okta.group("OnCallManagers").members()\n      # This would cause each on-call manager to be DMed\n      return slack.group([slack.user(x) for x in on_call_mgrs])\n\nIf you\'re interested in using Sym, please `reach out <https://symops.com/sales>`_!\n',
    'author': 'Sym Engineering',
    'author_email': 'pypi@symops.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sdk.docs.symops.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.6,<4.0.0',
}


setup(**setup_kwargs)
