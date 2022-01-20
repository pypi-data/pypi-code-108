# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ciscoisesdk',
 'ciscoisesdk.api',
 'ciscoisesdk.api.v3_0_0',
 'ciscoisesdk.api.v3_1_0',
 'ciscoisesdk.api.v3_1_1',
 'ciscoisesdk.models',
 'ciscoisesdk.models.validators',
 'ciscoisesdk.models.validators.v3_0_0',
 'ciscoisesdk.models.validators.v3_1_0',
 'ciscoisesdk.models.validators.v3_1_1']

package_data = \
{'': ['*']}

install_requires = \
['fastjsonschema>=2.14.5,<3.0.0',
 'future>=0.18.2,<0.19.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.25.1,<3.0.0',
 'xmltodict==0.12.0']

setup_kwargs = {
    'name': 'ciscoisesdk',
    'version': '1.4.1',
    'description': 'Cisco Identity Services Engine Platform SDK',
    'long_description': '=============\nciscoisesdk\n=============\n\n**ciscoisesdk** is a *community developed* Python library for working with the Identity Services Engine APIs. \nOur goal is to make working with Cisco Identity Services Engine in Python a *native* and *natural* experience!\n\n.. code-block:: python\n\n    from ciscoisesdk import IdentityServicesEngineAPI\n    from ciscoisesdk.exceptions import ApiError\n\n    # Create a IdentityServicesEngineAPI connection object;\n    # it uses ISE custom URL, username, and password, with ISE API version 3.1.0\n    # and its API Gateway enabled,\n    # and verify=True to verify the server\'s TLS certificate.\n    api = IdentityServicesEngineAPI(username=\'admin\',\n                                    password=\'C1sco12345\',\n                                    uses_api_gateway=True,\n                                    base_url=\'https://198.18.133.27\',\n                                    version=\'3.1.0\',\n                                    verify=True)\n    # NOTE: This collection assumes that the ERS APIs and OpenAPIs are enabled.\n\n    # Get allowed protocols (first page)\n    search_result = api.allowed_protocols.get_all().response.SearchResult\n    if search_result and search_result.resources:\n      for resource in search_result.resources:\n        resource_detail = api.allowed_protocols.get_by_id(\n                            resource.id\n                          ).response.AllowedProtocols\n        print("Id {}\\nName {}\\nallowChap {}\\n".format(resource_detail.id,\n                                                      resource_detail.name,\n                                                      resource_detail.allowChap))\n    print("----------")\n\n    # Handle pagination with a generator\n    allowed_protols_gen = api.allowed_protocols.get_all_generator()\n    for allowed_protocols_page_resp in allowed_protols_gen:\n      allowed_protols_result = allowed_protocols_page_resp.response.SearchResult\n      for resource in allowed_protols_result.resources:\n        resource_detail = api.allowed_protocols.get_by_id(\n                            resource.id\n                          ).response.AllowedProtocols\n        print("Id {}\\nName {}\\nallowChap {}\\n".format(resource_detail.id,\n                                                      resource_detail.name,\n                                                      resource_detail.allowChap))\n\n    # Filter network device\n    device_list_response = api.network_device.get_all(filter=\'name.EQ.ISE_EST_Local_Host_19\')\n    device_responses = device_list_response.response.SearchResult.resources\n    device_response = device_responses[0]\n\n    # Get network device detail\n    device_response_detail = api.network_device.get_by_id(device_response.id).response.NetworkDevice\n\n    # Delete network device\n    delete_device = api.network_device.delete_by_id(device_response.id)\n\n    # Create network device\n    try:\n        network_device_response = api.network_device.create(\n                                    name=\'ISE_EST_Local_Host_19\',\n                                    network_device_iplist=[{"ipaddress": "127.35.0.1", "mask": 32}])\n        print("Created, new Location {}".format(network_device_response.headers.Location))\n    except ApiError as e:\n        print(e)\n\n    # Advance usage example using Custom Caller functions\n    ## Define a Custom caller named function\n    ## Call them with:\n    ##    get_created_result(network_device_response.headers.Location)\n    def get_created_result(location):\n        return api.custom_caller.call_api(\'GET\', location)\n\n    ## Define the get_created_result function\n    ## under the custom_caller wrapper.\n    ## Call them with:\n    ##    api.custom_caller.get_created_result(network_device_response.headers.Location)\n    def setup_custom():\n        api.custom_caller.add_api(\'get_created_result\',\n                                    lambda location:\n                                    api.custom_caller.call_api(\'GET\', location)\n                                  )\n\n    # Add the custom API calls to the connection object under the custom_caller wrapper\n    setup_custom()\n\n    # Call the newly added functions\n    created_device_1 = get_created_result(network_device_response.headers.Location)\n    created_device_2 = api.custom_caller.get_created_result(network_device_response.headers.Location)\n    print(created_device_1.response == created_device_2.response)\n\n\n\nIntroduction_\n\n\nInstallation\n------------\n\nInstalling and upgrading ciscoisesdk is easy:\n\n**Install via PIP**\n\n.. code-block:: bash\n\n    $ pip install ciscoisesdk\n\n**Upgrading to the latest Version**\n\n.. code-block:: bash\n\n    $ pip install ciscoisesdk --upgrade\n\n\nDocumentation\n-------------\n\n**Excellent documentation is now available at:**\nhttps://ciscoisesdk.readthedocs.io\n\nCheck out the Quickstart_ to dive in and begin using ciscoisesdk.\n\n\nRelease Notes\n-------------\n\nPlease see the releases_ page for release notes on the incremental functionality and bug fixes incorporated into the published releases.\n\n\nQuestions, Support & Discussion\n-------------------------------\n\nciscoisesdk is a *community developed* and *community supported* project.  If you experience any issues using this package, please report them using the issues_ page.\n\n\nContribution\n------------\n\nciscoisesdk_ is a community development projects.  Feedback, thoughts, ideas, and code contributions are welcome!  Please see the `Contributing`_ guide for more information.\n\n\nInspiration\n------------\n\nThis library is inspired by the webexteamssdk_  library\n\nChange log\n----------\n\nAll notable changes to this project will be documented in the CHANGELOG_ file.\n\nThe development team may make additional name changes as the library evolves with the ISE APIs.\n\n\n*Copyright (c) 2021 Cisco and/or its affiliates.*\n\n.. _Introduction: https://ciscoisesdk.readthedocs.io/en/latest/api/intro.html\n.. _ciscoisesdk.readthedocs.io: https://ciscoisesdk.readthedocs.io\n.. _Quickstart: https://ciscoisesdk.readthedocs.io/en/latest/api/quickstart.html\n.. _ciscoisesdk: https://github.com/CiscoISE/ciscoisesdk\n.. _issues: https://github.com/CiscoISE/ciscoisesdk/issues\n.. _pull requests: https://github.com/CiscoISE/ciscoisesdk/pulls\n.. _releases: https://github.com/CiscoISE/ciscoisesdk/releases\n.. _the repository: ciscoisesdk_\n.. _pull request: `pull requests`_\n.. _Contributing: https://github.com/CiscoISE/ciscoisesdk/blob/master/docs/contributing.rst\n.. _webexteamssdk: https://github.com/CiscoDevNet/webexteamssdk\n.. _CHANGELOG: https://github.com/CiscoISE/ciscoisesdk/blob/main/CHANGELOG.md\n',
    'author': 'Jose Bogarin Solano',
    'author_email': 'jbogarin@altus.cr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ciscoisesdk.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
