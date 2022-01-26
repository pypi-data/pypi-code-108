# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['konan_sdk', 'konan_sdk.endpoints', 'konan_sdk.konan_service']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT[crypto]>=2.1.0,<3.0.0',
 'fastapi-utils>=0.2.1,<0.3.0',
 'fastapi>=0.70,<0.71',
 'loguru>=0.5.3,<0.6.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'konan-sdk',
    'version': '1.2.3',
    'description': "Python SDK for Konan's API",
    'long_description': '### Getting Started\n\n```Python\nfrom konan_sdk.sdk import KonanSDK\n\nif __name__ == \'__main__\':\n    # Initialize the SDK. Set verbose to True if you want verbose logging.\n    sdk = KonanSDK(verbose=False)\n\n    # Login user your valid konan credentials\n    user = sdk.login("<email>", "<password>")\n\n    # Define the input data to be passed to your model\n    input_data = {"feature_1": 1, "feature_2": "abc", }\n\n    # Run the prediction\n    prediction_uuid, ml_output = sdk.predict("<deployment_uuid>", input_data)\n\n    # Print the returned output\n    print(prediction_uuid, ml_output)\n```',
    'author': 'Synapse Analytics',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SynapseAnalytics/konan-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
